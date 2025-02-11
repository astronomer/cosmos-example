"""
An example DAG that uses Cosmos to render a dbt project as a TaskGroup with AWS ECS.
"""

import os

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator

from cosmos import ProfileConfig, DbtTaskGroup, ProjectConfig, ExecutionConfig
from cosmos.constants import ExecutionMode


DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))


project_config = ProjectConfig(
    dbt_project_path=(DBT_ROOT_PATH / "jaffle_shop").as_posix(),
)
shared_execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.AWS_ECS,
)

shared_profile_config = ProfileConfig(
    profile_name="postgres_profile",
    target_name="dev",
    profiles_yml_filepath=DBT_ROOT_PATH / "jaffle_shop" / "profiles.yml",
)


aws_ecs_operator_args = {
    "aws_conn_id": "aws_conn",
    "cluster": "<<<YOUR AWS CLUSTER NAME>>>",
    "task_definition": "<<<YOUR AWS TASK DEFINITION NAME>>>",
    "container_name": "<<<YOUR AWS CONTAINER NAME>>>",
    "profile_config": shared_profile_config,
    "launch_type": "FARGATE",
    "network_configuration": {
        "awsvpcConfiguration": {
            "subnets": ["<<<YOUR AWS SUBNET IDs>>>"],
            "assignPublicIp": "ENABLED",
        }
    },
    "deferrable": True,
    "environment_variables": {
        "ACCESS_KEY": "{{ conn.aws_conn.access_key }}",
        "SECRET_ACCESS_KEY": "{{ conn.postgres_conn.secret_access_key }}",
        "POSTGRES_PASSWORD": "{{ conn.postgres_conn.password }}",
        "POSTGRES_PORT": "{{ conn.postgres_conn.port }}",
        "POSTGRES_SCHEMA": "{{ conn.postgres_conn.schema }}",
        "POSTGRES_USER": "{{ conn.postgres_conn.login }}",
    },
    # "secured_variables": ["POSTGRES_PASSWORD"],
}

with DAG(
    dag_id="jaffle_shop_aws_ecs",
    start_date=datetime(2022, 11, 27),
    schedule=None,
    catchup=False,
) as dag:
    pre_dbt = EmptyOperator(task_id="pre_dbt")

    customers = DbtTaskGroup(
        group_id="aws_ecs_dbt",
        project_config=project_config,
        execution_config=shared_execution_config,
        profile_config=shared_profile_config,
        operator_args=aws_ecs_operator_args,
        default_args={"retries": 2},
        dag=dag,
    )

    post_dbt = EmptyOperator(task_id="post_dbt")

    pre_dbt >> customers >> post_dbt
