"""
Reusable SparkSession builder configured for:
- Iceberg table format, using a Hadoop catalog (see ADR-005)
- MinIO as the S3-compatible object store backing that catalog (see ADR-006)
"""

import os
from pyspark.sql import SparkSession

# MinIO connection details. These match the credentials set in
# docker-compose.yml. A later step moves these into .env instead
# of hardcoding them here.
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"

# Name of the Iceberg catalog as it appears in SQL, e.g.
# spark.sql("SELECT * FROM local.bronze.shareholder_letter")
CATALOG_NAME = "local"


def get_spark_session(app_name: str = "netflix-pipeline") -> SparkSession:
    spark = (
        SparkSession.builder.appName(app_name)
        # Downloads the Iceberg runtime and the S3A connector automatically.
        .config(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.11.0,"
            "org.apache.hadoop:hadoop-aws:3.4.1",
        )
        # Registers Iceberg's Spark SQL extensions (needed for MERGE,
        # time travel queries, etc.)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        # Defines the "local" catalog as a Hadoop catalog (ADR-005),
        # with its warehouse root inside the "bronze" MinIO bucket.
        .config(f"spark.sql.catalog.{CATALOG_NAME}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.type", "hadoop")
        .config(f"spark.sql.catalog.{CATALOG_NAME}.warehouse", "s3a://bronze/")
        # Points the S3A connector at MinIO and sets its credentials.
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.endpoint.region", "us-east-1")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        # MinIO runs without SSL locally, so SSL is disabled for this connection.
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )
    return spark