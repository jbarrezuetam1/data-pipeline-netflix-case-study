"""
Sanity check for the Spark -> Iceberg -> S3A -> MinIO chain.
Creates a small Iceberg table, writes one row, reads it back.
"""

from spark_session import get_spark_session

spark = get_spark_session()

spark.sql("CREATE NAMESPACE IF NOT EXISTS local.bronze")

spark.sql(
    """
    CREATE TABLE IF NOT EXISTS local.bronze.connection_test (
        id INT,
        message STRING
    )
    USING iceberg
    """
)

spark.sql(
    "INSERT INTO local.bronze.connection_test VALUES (1, 'Hello from Iceberg on MinIO')"
)

spark.sql("SELECT * FROM local.bronze.connection_test").show()

spark.stop()