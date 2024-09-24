import os
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from pendulum import datetime

from cosmos import DbtTaskGroup, ProjectConfig, ExecutionConfig
from cosmos.constants import ExecutionMode


DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))

GCP_PROJECT_ID = "<<<<YOUR_GCP_PROJECT_ID>>>>"
GCP_LOCATION = "<<<<YOUR_GCP_REGION>>>>"
GCP_CLOUD_RUN_JOB_NAME = "astronomer-cosmos-example"

project_config = ProjectConfig(
    dbt_project_path=(DBT_ROOT_PATH / "jaffle_shop").as_posix(),
)

execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.GCP_CLOUD_RUN_JOB,
)

with DAG(
    dag_id="jaffle_shop",
    start_date=datetime(2022, 11, 27),
    schedule=None,
    catchup=False,
) as dag:

    pre_dbt_workflow = EmptyOperator(task_id="pre_dbt_workflow")

    jaffle_shop = DbtTaskGroup(
        group_id="jaffle_shop",
        project_config=project_config,
        execution_config=execution_config,
        operator_args={
            "project_id": GCP_PROJECT_ID,
            "region": GCP_LOCATION,
            "job_name": GCP_CLOUD_RUN_JOB_NAME,
            },
        default_args={"retries": 2},
        dag=dag,
    )

    post_dbt_workflow = EmptyOperator(task_id="post_dbt_workflow")

pre_dbt_workflow >> jaffle_shop >> post_dbt_workflow