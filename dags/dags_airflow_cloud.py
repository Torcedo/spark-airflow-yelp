from airflow.models.param import Param
from airflow.models import Variable
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
import re

PROJECT_ID = 'datasparkyelp'
REGION = 'europe-west1'
CLUSTER_NAME = 'datasparkyelp-dataproc'

BUCKET_RAW = 'datasparkyelp-yelp-raw'
BUCKET_SCRIPTS = 'datasparkyelp-spark-scripts'
BUCKET_INTERMEDIATE = 'datasparkyelp-yelp-intermediate'
DESTINATION_FOLDER = 'json_file'

default_args = {'owner': 'mat'}

def extract_keyword_from_filename(filename):
    keywords = ["business", "review", "tip", "user", "checkin"]
    for keyword in keywords:
        if keyword in filename.lower():
            return keyword
    return None

def resolve_script_name(**context):
    file = context['params']['json_file']
    keyword = extract_keyword_from_filename(file)
    if keyword:
        context['ti'].xcom_push(key='output_name', value=keyword)
        return f"{keyword}_transform.py"
    raise ValueError("Aucun mot-clé valide trouvé dans le nom du fichier.")

with DAG(
    dag_id='parametrized_transform_dag',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=['parametrized', 'yelp'],
    params={
        "json_file": Param("yelp_academic_dataset_business.json", type="string"), #Fichier par défault 
        "project_id": Param(PROJECT_ID, type="string")
    }
) as dag:

    resolve_script = PythonOperator(
        task_id="resolve_script",
        python_callable=resolve_script_name,
        provide_context=True
    )
    # Sensors
    wait_for_json = GCSObjectExistenceSensor(
        task_id="wait_for_json",
        bucket=BUCKET_RAW,
        object=f"{DESTINATION_FOLDER}/{{{{ params.json_file }}}}",
        timeout=300,
        poke_interval=10,
        mode='poke'
    )
    wait_for_script = GCSObjectExistenceSensor(
        task_id="wait_for_script",
        bucket=BUCKET_SCRIPTS,
        object="{{ task_instance.xcom_pull(task_ids='resolve_script') }}",
        timeout=300,
        poke_interval=10,
        mode='poke'
    )
    transform = DataprocSubmitJobOperator(
        task_id="transform_data",
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": "gs://" + BUCKET_SCRIPTS + "/{{ task_instance.xcom_pull(task_ids='resolve_script') }}",
                "args": [
                    "gs://" + BUCKET_RAW + "/" + DESTINATION_FOLDER + "/{{ params.json_file }}",
                    "gs://" + BUCKET_INTERMEDIATE + "/parquet/{{ task_instance.xcom_pull(task_ids='resolve_script', key='output_name') }}/"
                ]
            }
        },
        region=REGION,
        project_id=PROJECT_ID
    )
    load = GCSToBigQueryOperator(
        task_id="load_to_bq",
        bucket=BUCKET_INTERMEDIATE,
        source_objects=["parquet/{{ task_instance.xcom_pull(task_ids='resolve_script', key='output_name') }}/*.parquet"],
        destination_project_dataset_table="{{ params.project_id }}.yelp.{{ task_instance.xcom_pull(task_ids='resolve_script', key='output_name') }}",
        source_format='PARQUET',
        write_disposition='WRITE_TRUNCATE',
        autodetect=True,
        create_disposition='CREATE_NEVER'
    )
    resolve_script >> wait_for_script
    wait_for_json >> wait_for_script >> transform >> load