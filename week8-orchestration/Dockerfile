FROM apache/airflow:2.10.2

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /requirements.txt
RUN python3 -m venv /home/airflow/pipeline_venv && \
    /home/airflow/pipeline_venv/bin/pip install --no-cache-dir -r /requirements.txt