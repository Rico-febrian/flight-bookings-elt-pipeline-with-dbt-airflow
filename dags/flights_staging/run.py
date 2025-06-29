from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pendulum import datetime

from flights_staging.tasks.main import extract, load
from helper.callbacks.slack_notifier import slack_notifier
from airflow.models.variable import Variable

default_args = {
    'on_failure_callback': slack_notifier
}

@dag(
    dag_id='flights_staging_pipeline',
    description='Extract flights data and load into staging area',
    start_date=datetime(2024, 9, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args
)

def flight_staging():
    incremental_mode = eval(Variable.get('flight_staging_incremental_mode'))
    
    extract_tasks = extract(incremental=incremental_mode)
    first_load_task, last_load_task = load(incremental=incremental_mode)
    
    trigger_transformation = TriggerDagRunOperator(
        task_id='trigger_flights_warehouse_pipeline',
        trigger_dag_id='flights_warehouse_pipeline',
    )

    extract_tasks >> first_load_task
    last_load_task >> trigger_transformation
    
    return trigger_transformation

flight_staging()