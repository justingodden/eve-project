################################################################################
# Providers
################################################################################
provider "aws" {
  region  = var.region
  profile = var.profile
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--region", local.region]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      # This requires the awscli to be installed locally where Terraform is executed
      args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--region", local.region]
    }
  }
}

provider "kubectl" {
  apply_retry_count      = 5
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  load_config_file       = false

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

################################################################################
# EKS Cluster
################################################################################
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.13"

  cluster_name                   = local.name
  cluster_version                = local.cluster_version
  cluster_endpoint_public_access = true


  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    managed_node_group = {
      instance_types = ["m5.large"]

      ami_type = "AL2_x86_64" # "BOTTLEROCKET_x86_64"
      #   platform = "bottlerocket"

      min_size     = 1
      max_size     = 3
      desired_size = 2

      create_iam_role = true
      #   iam_role_additional_policies = {
      #     additional = aws_iam_policy.eks.arn
      #   }
    }
  }

  # EKS Addons
  cluster_addons = {
    aws-ebs-csi-driver = {
      most_recent = true
    }
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      # Specify the VPC CNI addon should be deployed before compute to ensure
      # the addon is configured before data plane compute resources are created
      # See README for further details
      before_compute = true
      most_recent    = true # To ensure access to the latest settings provided
      configuration_values = jsonencode({
        env = {
          # Reference docs https://docs.aws.amazon.com/eks/latest/userguide/cni-increase-ip-addresses.html
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET       = "1"
        }
      })
    }
  }

  tags = local.tags
}

################################################################################
# EKS Blueprints Addons
################################################################################
module "eks_blueprints_addons" {
  source  = "aws-ia/eks-blueprints-addons/aws"
  version = "~> 1.0"

  cluster_name      = module.eks.cluster_name
  cluster_endpoint  = module.eks.cluster_endpoint
  cluster_version   = module.eks.cluster_version
  oidc_provider_arn = module.eks.oidc_provider_arn

  enable_aws_load_balancer_controller = true
  aws_load_balancer_controller = {
    chart_version = "1.6.2"                                                     # min version required to use SG for NLB feature
    set           = [{ name = "enableServiceMutatorWebhook", value = "false" }] # https://stackoverflow.com/a/76093824/20894958
  }

  enable_argocd = true
  argocd = {
    set = [
      { name = "configs.params.server\\.insecure", value = "true" },
      { name = "server.ingress.enabled", value = "true" },
      { name = "server.ingress.hosts[0]", value = "argocd.eve-project.com" }
    ]
  }

  enable_aws_efs_csi_driver    = true
  enable_karpenter             = false
  enable_cluster_autoscaler    = false
  enable_metrics_server        = true
  enable_kube_prometheus_stack = true
  enable_argo_workflows        = false
  enable_external_secrets      = false

  tags = local.tags
}

################################################################################
# ArgoCD App of Apps Pattern
################################################################################
resource "kubectl_manifest" "argocd_app_of_apps" {
  yaml_body = <<YAML
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
  labels:
    managedBy: terraform
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/justingodden/eve-project.git
    targetRevision: HEAD
    path: argocd/apps
  destination:
    server: "https://kubernetes.default.svc"
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
YAML
  depends_on = [
    module.vpc,
    module.eks,
    module.eks_blueprints_addons
  ]
}

################################################################################
# ArgoCD Nginx Ingress Controller - Terraform controls the Load Balancer indirectly
################################################################################
resource "kubectl_manifest" "argocd_nginx_ingress_controller" {
  yaml_body  = <<YAML
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ingress-nginx
  namespace: argocd
  labels:
    managedBy: terraform
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  sources:
    - repoURL: https://kubernetes.github.io/ingress-nginx
      chart: ingress-nginx
      targetRevision: "*"
      helm:
        releaseName: ingress-nginx
        valueFiles:
          - $values/argocd/manifests/nginx-ingress-controller/values.yaml
    - repoURL: https://github.com/justingodden/eve-project.git
      ref: values
  destination:
    server: "https://kubernetes.default.svc"
    namespace: ingress-nginx
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      selfHeal: true
      prune: true
YAML
  depends_on = [time_sleep.wait_30_seconds]
}

resource "time_sleep" "wait_30_seconds" {
  depends_on = [module.eks_blueprints_addons]

  destroy_duration = "30s"
}

################################################################################
# EKS Additional IAM Policies
################################################################################
resource "aws_iam_policy" "eks" {
  name        = "${local.name}-additional-policy"
  description = "Additional policy for eks cluster ${local.name}."
  path        = "/"
  policy      = data.aws_iam_policy_document.eks.json
}

data "aws_iam_policy_document" "eks" {
  statement {
    sid    = "S3"
    effect = "Allow"

    actions = [
      "s3:*",
      "kms:*",
    ]

    resources = [module.s3.arn]
  }

  statement {
    sid    = "SecretsManager"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
    ]

    resources = [module.secrets-manager.arn]
  }
}

resource "aws_iam_role_policy_attachment" "eks" {
  role       = module.eks.eks_managed_node_groups.managed_node_group.iam_role_name
  policy_arn = aws_iam_policy.eks.arn
}

################################################################################
# VPC
################################################################################
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.name
  cidr = local.vpc_cidr

  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 48)]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  manage_default_network_acl    = true
  default_network_acl_tags      = { Name = "${local.name}-default" }
  manage_default_route_table    = true
  default_route_table_tags      = { Name = "${local.name}-default" }
  manage_default_security_group = true
  default_security_group_tags   = { Name = "${local.name}-default" }

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.name}" = "owned"
    "kubernetes.io/role/elb"              = 1
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.name}" = "owned"
    "kubernetes.io/role/internal-elb"     = 1
  }

  tags = local.tags
}

################################################################################
# RDS
################################################################################
module "rds" {
  source            = "./modules/rds"
  instance_class    = "db.t3.micro"
  allocated_storage = 30
  engine            = "postgres"
  engine_version    = "15.3"
  name              = "${local.name}-db"
  username          = local.rds_login.username
  password          = local.rds_login.password
  db_name           = local.rds_login.db_name
  port              = local.rds_login.port
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.public_subnets
  tags              = local.tags
}

################################################################################
# S3
################################################################################
module "s3" {
  source     = "./modules/s3"
  name       = "${local.name}-${random_id.s3.hex}"
  versioning = false
}

################################################################################
# SecretsManager
################################################################################
module "secrets-manager" {
  source = "./modules/secrets-manager"
  name   = "${local.name}-${random_id.secrets_manager.hex}"
  secrets = merge(
    local.rds_login,
    {
      db_name        = local.rds_login.db_name
      host           = module.rds.address
      db_uri         = "postgresql://${local.rds_login.username}:${local.rds_login.password}@${module.rds.address}:${local.rds_login.port}/${local.rds_login.db_name}"
      s3_bucket_uri  = "s3://${module.s3.bucket_regional_domain_name}"
      openai_api_key = var.openai_api_key
      cohere_api_key = var.cohere_api_key
    }
  )
}

################################################################################
# ECR Repos
################################################################################
module "ecr-data-collector" {
  source = "./modules/ecr"
  name   = "${local.name}/data-collector"
}

module "ecr-summarizer" {
  source = "./modules/ecr"
  name   = "${local.name}/summarizer"
}

module "ecr-frontend" {
  source = "./modules/ecr"
  name   = "${local.name}/frontend"
}

module "ecr-backend" {
  source = "./modules/ecr"
  name   = "${local.name}/backend"
}
