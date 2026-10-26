"""
Exports the Gold tables used by the Power BI dashboard from the dbt-duckdb
database to Parquet files (see ADR-014). Power BI reads Parquet natively,
which avoids installing a DuckDB ODBC driver.

The Gold models are dbt views over the Silver Iceberg tables in MinIO, so
this script reuses the extensions and S3 secret defined in dbt's
profiles.yml instead of duplicating credentials.

Power BI cannot read list columns, so the genres list of dim_title is also
exported as a separate table with one row per title and genre.

Run from the repository root:
    python week11-dashboard/export_gold_for_bi.py
"""

import os
import re
from pathlib import Path

import duckdb
import yaml

DB_PATH = "week7-gold-layer/netflix_gold/netflix_gold.duckdb"
PROFILES_PATH = "week7-gold-layer/netflix_gold/profiles.yml"
OUTPUT_DIR = Path("week11-dashboard/exports")

TABLES = [
    "dim_date",
    "dim_region",
    "dim_title",
    "fct_engagement",
    "fct_regional_financials",
]


def load_dev_profile(profiles_path):
    """Return the 'dev' output block of the dbt profile."""
    with open(profiles_path) as f:
        profiles = yaml.safe_load(f)
    return profiles["netflix_gold"]["outputs"]["dev"]


def resolve_env_vars(value):
    """Resolve dbt-style {{ env_var('NAME', 'default') }} templates."""
    pattern = r"\{\{\s*env_var\(\s*'([^']+)'\s*(?:,\s*'([^']*)'\s*)?\)\s*\}\}"

    def replace(match):
        name, default = match.group(1), match.group(2)
        return os.environ.get(name, default if default is not None else "")

    return re.sub(pattern, replace, str(value))


def configure_connection(con, profile):
    """Load the extensions and create the S3 secret exactly as dbt does."""
    for extension in profile.get("extensions", []):
        con.execute(f"INSTALL {extension}")
        con.execute(f"LOAD {extension}")

    for raw_secret in profile.get("secrets", []):
        secret = {key: resolve_env_vars(val) for key, val in raw_secret.items()}
        # DuckDB expects host:port without the http:// prefix.
        endpoint = secret["endpoint"].replace("http://", "").replace("https://", "")
        con.execute(
            f"""
            CREATE OR REPLACE SECRET minio_export (
                TYPE {secret["type"]},
                KEY_ID '{secret["key_id"]}',
                SECRET '{secret["secret"]}',
                ENDPOINT '{endpoint}',
                URL_STYLE '{secret["url_style"]}',
                USE_SSL {secret["use_ssl"].lower()},
                REGION '{secret["region"]}'
            )
            """
        )
    # Silver is written by Spark and nothing writes while we export.
    con.execute("SET unsafe_enable_version_guessing = true;")


def export_tables(db_path, output_dir, tables):
    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db_path, read_only=True)
    configure_connection(con, load_dev_profile(PROFILES_PATH))

    for table in tables:
        target = (output_dir / f"{table}.parquet").as_posix()
        con.execute(f"COPY (SELECT * FROM main.{table}) TO '{target}' (FORMAT PARQUET)")
        count = con.execute(f"SELECT COUNT(*) FROM main.{table}").fetchone()[0]
        print(f"{table}: {count} rows -> {target}")

    # One row per title and genre, because Power BI cannot read list columns.
    genre_target = (output_dir / "dim_title_genre.parquet").as_posix()
    con.execute(
        f"""
        COPY (
            SELECT title_english, unnest(genres) AS genre
            FROM main.dim_title
            WHERE genres IS NOT NULL
        ) TO '{genre_target}' (FORMAT PARQUET)
        """
    )
    genre_count = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{genre_target}')"
    ).fetchone()[0]
    print(f"dim_title_genre: {genre_count} rows -> {genre_target}")

    con.close()


if __name__ == "__main__":
    export_tables(DB_PATH, OUTPUT_DIR, TABLES)