from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowSkipException
from airflow import AirflowException

from helper.minio import CustomMinio
from datetime import timedelta

import pandas as pd

class Extract:
    @staticmethod
    def _flights(table_name, incremental, **kwargs):
        try:
            pg_hook = PostgresHook(postgres_conn_id='flight-db-src')
            connection = pg_hook.get_conn()
            cursor = connection.cursor()

            query = f"SELECT * FROM bookings.{table_name}"
            if incremental:
                date = kwargs['ds']
                query += f" WHERE last_update::DATE = '{date}'::DATE - INTERVAL '1 DAY';"

                object_name = f'/flight/{table_name}-{(pd.to_datetime(date) - timedelta(days=1)).strftime("%Y-%m-%d")}.csv'
            
            else:
                object_name = f'/flight/{table_name}.csv'

            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            connection.commit()
            connection.close()

            column_list = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=column_list)
        
            if df.empty:
                raise AirflowSkipException(f"{table_name} doesn't have new data. Skipped...")

            bucket_name = 'extracted-data'
            CustomMinio._put_csv(df, bucket_name, object_name)

        except AirflowSkipException as e:
            raise e
        except Exception as e:
            raise AirflowException(f"Error when extracting {table_name} : {str(e)}")