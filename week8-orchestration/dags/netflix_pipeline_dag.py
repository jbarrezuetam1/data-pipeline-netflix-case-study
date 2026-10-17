"""
Orchestrates the full Netflix-inspired lakehouse pipeline:
Bronze -> Silver -> Data Quality -> Gold.

Each task runs an existing Python/Spark/dbt script from the project
using a separate virtual environment (pipeline_venv) that holds the
pipeline's dependencies, kept isolated from Airflow's own environment.
"""

from datetime import datetime
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_ROOT = "/opt/airflow/project"
VENV_PYTHON = "/home/airflow/pipeline_venv/bin/python"
VENV_DBT = "/home/airflow/pipeline_venv/bin/dbt"

default_args = {
    "owner": "juanjose",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}

with DAG(
    dag_id="netflix_pipeline",
    description="Bronze -> Silver -> Data Quality -> Gold for the Netflix case study",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,  # manual trigger only, for now
    catchup=False,
    tags=["netflix", "capstone"],
) as dag:

    # ---- Bronze layer ----
    bronze_shareholder_letter = BashOperator(
        task_id="bronze_shareholder_letter",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"{VENV_PYTHON} week4-bronze-layer/shareholder_letter_connector.py"
        ),
    )

    bronze_engagement_report = BashOperator(
        task_id="bronze_engagement_report",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"{VENV_PYTHON} week4-bronze-layer/engagement_report_connector.py"
        ),
    )

    bronze_tmdb_movies = BashOperator(
        task_id="bronze_tmdb_movies",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"{VENV_PYTHON} week4-bronze-layer/tmdb_load_to_iceberg.py"
        ),
    )

    # ---- Silver layer ----
    silver_shareholder_letter = BashOperator(
        task_id="silver_shareholder_letter",
        bash_command=(
            f"cd {PROJECT_ROOT}/week5-silver-layer && "
            f"{VENV_PYTHON} shareholder_letter_silver.py"
        ),
    )

    silver_engagement_report = BashOperator(
        task_id="silver_engagement_report",
        bash_command=(
            f"cd {PROJECT_ROOT}/week5-silver-layer && "
            f"{VENV_PYTHON} engagement_report_silver.py"
        ),
    )

    silver_tmdb_movies = BashOperator(
        task_id="silver_tmdb_movies",
        bash_command=(
            f"cd {PROJECT_ROOT}/week5-silver-layer && "
            f"{VENV_PYTHON} tmdb_movies_silver.py"
        ),
    )

    # ---- Data quality ----
    validate_data_quality = BashOperator(
        task_id="validate_data_quality",
        bash_command=(
            f"cd {PROJECT_ROOT}/week6-data-quality && "
            f"{VENV_PYTHON} validate_silver_tables.py"
        ),
    )

    # ---- Gold layer ----
    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=(
            f"cd {PROJECT_ROOT}/week7-gold-layer/netflix_gold && "
            f"{VENV_DBT} run --profiles-dir ."
        ),
    )

    # ---- Dependencies ----
    bronze_shareholder_letter >> silver_shareholder_letter
    bronze_engagement_report >> silver_engagement_report
    bronze_tmdb_movies >> silver_tmdb_movies

    [silver_shareholder_letter, silver_engagement_report, silver_tmdb_movies] >> validate_data_quality

    validate_data_quality >> dbt_run_gold