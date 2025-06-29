from datetime import datetime
from airflow.datasets import Dataset
from helper.callbacks.slack_notifier import slack_notifier

from cosmos.config import ProjectConfig, ProfileConfig, RenderConfig
from cosmos.profiles.postgres import PostgresUserPasswordProfileMapping
from cosmos import DbtDag

import os

DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/dags/flights_warehouse/flights_dbt"

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH,
    project_name="flight_db_warehouse",
)

profile_config = ProfileConfig(
    profile_name="flight_db_warehouse",
    target_name="final",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id='flight-db-dwh',
        profile_args={"schema": "flight-db-dwh"}
    )
)

dag = DbtDag(
    dag_id="flights_warehouse_pipeline",
    schedule=[
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.aircrafts_data"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.airports_data"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.bookings"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.flights"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.seats"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.tickets"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.ticket_flights"),
        Dataset("postgres://flight-db-dwh:5432/flight-db-dwh.stg.boarding_passes")
    ],
    catchup=False,
    start_date=datetime(2024, 10, 1),
    project_config=project_config,
    profile_config=profile_config,
    render_config=RenderConfig(
        dbt_executable_path="/opt/airflow/dbt_venv/bin",
        emit_datasets=True
    ),
    default_args={
        'on_failure_callback': slack_notifier
    }
)