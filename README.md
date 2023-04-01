# cosmos-example

This is an Astro CLI project used to show Cosmos examples.

## Running

Ensure you have the Astro CLI >= 1.8.0 installed

Run `astro dev start` to start the project. By default, this runs against the Airflow metadata database. To reset the database, run `astro dev kill` and then `astro dev start`.

## Examples

This repo comes with a few examples located in the `dags/` directory. These are meant to be used as a reference for how to use the various features of Cosmos.

### jaffle_shop

This DAG demonstrates a simple example of running the dbt jaffle shop project using Cosmos. It uses a virtual environment for the dbt commands, which is created in the Dockerfile and used in the `DbtTaskGroup`.

### jaffle_shop_filtered

This DAG demonstrates an example of filtering/selecting models instead of using all models in a project. In this case, we've filtered down to `tags:customer`, and there are two models with this tag:
- `stg_customers`
- `customers`

The `stg_customers` tag is defined in [`dags/dbt/jaffle_shop/models/staging/schema.yml`](dags/dbt/jaffle_shop/models/staging/schema.yml) using a config file. The `customers` tag is defined directly in the model SQL, located in [`dags/dbt/jaffle_shop/models/customers.sql`](dags/dbt/jaffle_shop/models/customers.sql).
