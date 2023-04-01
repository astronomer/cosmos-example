FROM quay.io/astronomer/astro-runtime:7.2.0

# install python virtualenv to run dbt
WORKDIR /usr/local/airflow
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir -r dbt-requirements.txt && deactivate
