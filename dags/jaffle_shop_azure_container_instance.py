"""
An example DAG that uses Cosmos to render a dbt project as a TaskGroup with Azure Container Instances.
"""
import os

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, ExecutionMode

DEFAULT_DBT_ROOT_PATH = Path(__file__).parent / "dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))

shared_execution_config = ExecutionConfig(
    execution_mode=ExecutionMode.AZURE_CONTAINER_INSTANCE,
    dbt_project_path="/code/dbt/jaffle_shop"  # This is the path to the code in the Docker container!
)

shared_profile_config = ProfileConfig(
    profile_name="jaffle_shop",
    target_name="dev",
    profiles_yml_filepath=DBT_ROOT_PATH / "jaffle_shop" / "profiles.yml"
)

azure_container_instance_operator_args = {
    "image": "<<<REPLACE WITH YOUR IMAGE>>>",
    "ci_conn_id": "aci",
    "registry_conn_id": "acr",
    "resource_group": "<<<REPLACE WITH YOUR RESOURCE GROUP>>>",
    "name": "astro-aci-{{ ti.task_id.replace('.','-').replace('_','-') }}",
    "region": "West Europe",
    "environment_variables": {
        "POSTGRES_DATABASE": "{{ conn.aci_db.schema }}",
        "POSTGRES_HOST": "{{ conn.aci_db.host }}",
        "POSTGRES_PASSWORD": "{{ conn.aci_db.password }}",
        "POSTGRES_PORT": "{{ conn.aci_db.port }}",
        "POSTGRES_SCHEMA": "{{ conn.aci_db.schema }}",
        "POSTGRES_USER": "{{ conn.aci_db.login }}",
    },
    "secured_variables": ["POSTGRES_PASSWORD"]
}

with DAG(
        dag_id="jaffle_shop_azure_container_instance",
        start_date=datetime(2022, 11, 27),
        schedule=None,
        catchup=False,
) as dag:

    pre_dbt = EmptyOperator(task_id="pre_dbt")

    customers = DbtTaskGroup(
        group_id="dbt",
        project_config=ProjectConfig(
            manifest_path=DBT_ROOT_PATH / "jaffle_shop" / "target" / "manifest.json",
            project_name="jaffle_shop"),
        execution_config=shared_execution_config,
        operator_args=azure_container_instance_operator_args,
        profile_config=shared_profile_config,
        default_args={"retries": 2},
    )

    post_dbt = EmptyOperator(task_id="post_dbt")

    pre_dbt >> customers >> post_dbt
