import tarfile
import os

import boto3

tar_filename = "db.tar.xz"


s3 = boto3.client("s3")
with open(tar_filename, "wb") as f:
    s3.download_fileobj(
        "eve-project-2de413a419ed1b48-cc23cc37cdcf9132",
        "langchain-docs-embeddings/db.tar.xz",
        f,
    )

with tarfile.open(tar_filename) as f:
    f.extractall()


if os.path.isfile(tar_filename):
    os.remove(tar_filename)
else:
    print("Not able to delete tar file")
