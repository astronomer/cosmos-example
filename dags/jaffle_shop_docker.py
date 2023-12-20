from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from pendulum import datetime

from cosmos.operators.docker import DbtRunOperationDockerOperator, DbtSeedDockerOperator

# PATH within the Docker container for the DBT project
PROJECT_DIR = "dags/dbt/jaffle_shop"

DBT_IMAGE = "dbt-jaffle-shop:1.0.0"

PROJECT_SEEDS = ["raw_customers", "raw_payments", "raw_orders"]
with DAG(
    dag_id="jaffle_shop_docker",
    start_date=datetime(2022, 11, 27),
    schedule=None,
    catchup=False,
) as dag:

    pre_dbt_workflow = EmptyOperator(task_id="pre_dbt_workflow")

    with TaskGroup(group_id="drop_seeds_if_exist") as drop_seeds:
        for seed in PROJECT_SEEDS:
            DbtRunOperationDockerOperator(
                task_id=f"drop_{seed}_if_exists",
                macro_name="drop_table",
                args={"table_name": seed},
                project_dir=PROJECT_DIR,
                schema="public",
                conn_id="postgres_default",
                image=DBT_IMAGE,
                network_mode="bridge",
            )

    create_seed = DbtSeedDockerOperator(
        task_id="seed",
        project_dir=PROJECT_DIR,
        schema="public",
        conn_id="postgres_default",
        image=DBT_IMAGE,
        network_mode="bridge",
    )

    post_dbt_workflow = EmptyOperator(task_id="post_dbt_workflow")

    pre_dbt_workflow >> drop_seeds >> create_seed >> post_dbt_workflow
