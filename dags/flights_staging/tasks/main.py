from airflow.decorators import task_group
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from flights_staging.tasks.components.extract import Extract
from flights_staging.tasks.components.load import Load

@task_group
def extract(incremental):            
    table_to_extract = eval(Variable.get('list_flight_table'))

    for table_name in table_to_extract:
        current_task = PythonOperator(
            task_id = f'{table_name}',
            python_callable = Extract._flights,
            trigger_rule = 'none_failed',
            op_kwargs = {
                'table_name': f'{table_name}',
                'incremental': incremental
            }
        )

        current_task

@task_group
def load(incremental):
    table_to_load = eval(Variable.get('list_flight_table'))
    table_pkey = eval(Variable.get('pkey_flight_table'))
    
    previous_task = None
    first_task = None
    
    for table_name in table_to_load:
        current_task = PythonOperator(
            task_id = f'{table_name}',
            python_callable = Load._flights,
            trigger_rule = 'none_failed',
            op_kwargs = {
                'table_name': table_name,
                'table_pkey': table_pkey,
                'incremental': incremental
            },
        )
        
        if previous_task:
            previous_task >> current_task
        else:
            first_task = current_task
        previous_task = current_task
        
    return first_task, previous_task