from airflow import DAG
from airflow.operators.empty import EmptyOperator
from pendulum import datetime

from cosmos.providers.dbt.task_group import DbtTaskGroup

with DAG(
    dag_id="jaffle_shop_filtered",
    start_date=datetime(2022, 11, 27),
    schedule=None,
    catchup=False,
) as dag:

    pre_dbt_workflow = EmptyOperator(task_id="pre_dbt_workflow")

    jaffle_shop = DbtTaskGroup(
        dbt_root_path="/usr/local/airflow/dags/dbt",
        dbt_project_name="jaffle_shop",
        conn_id="airflow_db",
        dbt_args={
            "schema": "public",
            "dbt_executable_path": "/usr/local/airflow/dbt_venv/bin/dbt"
        },
        select={"configs": ["tags:customers"]},
        dag=dag,
    )

    post_dbt_workflow = EmptyOperator(task_id="post_dbt_workflow")

    pre_dbt_workflow >> jaffle_shop >> post_dbt_workflow
