from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowSkipException
from airflow import AirflowException

from helper.minio import CustomMinio
from sqlalchemy import create_engine
from pangres import upsert
from datetime import timedelta
from minio.error import S3Error 

import pandas as pd
import json

class Load:
    @staticmethod
    def _flights(table_name, incremental, **kwargs):
        date = kwargs.get('ds')
        table_pkey = kwargs.get('table_pkey')

        object_name = f'/flight/{table_name}-{(pd.to_datetime(date) - timedelta(days=1)).strftime("%Y-%m-%d")}.csv' if incremental else f'/flight/{table_name}.csv'
        bucket_name = 'extracted-data'
        engine = create_engine(PostgresHook(postgres_conn_id='flight-db-dwh').get_uri())

        try:
            df = CustomMinio._get_dataframe(bucket_name, object_name)
            
            # Convert specific columns to JSON string format for JSONB compatibility in Postgres
            jsonb_columns = ['model', 'airport_name', 'city', 'contact_data']
            
            for col in jsonb_columns:
                if col in df.columns:
                    df[col] = df[col].apply(json.dumps)
            
            if df.empty:
                raise AirflowSkipException(f"Dataframe for {table_name} is empty. Skipped...")
            
            if table_name not in table_pkey:
                raise ValueError(f"Primary key for {table_name} is not defined in the provided pkey_flight_table variable.")
            
            df = df.set_index(table_pkey[table_name])

            upsert(
                con=engine,
                df=df,
                table_name=table_name,
                schema='stg',
                if_row_exists='update'
            )

            engine.dispose()
        
        except(S3Error, FileNotFoundError) as e:
            engine.dispose()
            raise AirflowSkipException(f"{table_name} doesn't have new data. Skipped... : {str(e)}")
    
        except Exception as e:
            engine.dispose()
            raise AirflowException(f"Error when loading {table_name} : {str(e)}")