"""
Direct connectivity check to MinIO using boto3, without Spark.
Confirms MinIO is reachable and the bucket exists, independent of
any Hadoop/S3A configuration.
"""

import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin123",
)

response = s3.list_buckets()
print("Buckets found:")
for bucket in response["Buckets"]:
    print(f" - {bucket['Name']}")