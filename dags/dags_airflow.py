from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
import re 

import subprocess
import os

# Configuration du DAG
# Buckets

PROJECT_ID = 'datasparkyelp'
REGION = 'europe-west1'
CLUSTER_NAME = 'datasparkyelp-dataproc'

BUCKET_RAW = 'datasparkyelp-yelp-raw'
BUCKET_SCRIPTS = 'datasparkyelp-spark-scripts'
BUCKET_INTERMEDIATE = 'datasparkyelp-yelp-intermediate'



LOCAL_DATA_FOLDER = '/opt/airflow/data'
LOCAL_SCRIPT_FOLDER = '/opt/airflow/scripts'
DESTINATION_FOLDER = 'json_file'


PYTHON_SCRIPTS = [
    f for f in os.listdir(LOCAL_SCRIPT_FOLDER)
    if f.endswith('.py') and os.path.isfile(os.path.join(LOCAL_SCRIPT_FOLDER, f))
]

EXCLUDED_JSONS = ['yelp_academic_dataset_checkin.json']
JSON_FILES = [
    f for f in os.listdir(LOCAL_DATA_FOLDER)
    if f.endswith('.json') 
    and os.path.isfile(os.path.join(LOCAL_DATA_FOLDER, f))
    and f not in EXCLUDED_JSONS
]


default_args = {
    'owner': 'mat',
}

def upload_json_if_not_exists(json_file: str, **kwargs):
    hook = GCSHook()
    object_path = f"{DESTINATION_FOLDER}/{json_file}"

    if hook.exists(bucket_name=BUCKET_RAW, object_name=object_path):
        print(f"Fichier déjà présent : gs://{BUCKET_RAW}/{object_path} — skip upload")
    else:
        print(f"Upload du fichier : {json_file}")
        hook.upload(
            bucket_name=BUCKET_RAW,
            object_name=object_path,
            filename=os.path.join(LOCAL_DATA_FOLDER, json_file),
            mime_type='application/json'
        )

def create_upload_json_task(json_file: str):
    return PythonOperator(
        task_id=f"conditional_upload_json_{json_file.replace('.json', '')}",
        python_callable=upload_json_if_not_exists,
        op_args=[json_file],
        provide_context=True
    )


def upload_script_to_gcs(script_name: str):
    return LocalFilesystemToGCSOperator(
        task_id=f"upload_script_{script_name.replace('.py', '')}",
        src=os.path.join(LOCAL_SCRIPT_FOLDER, script_name),
        dst=f"{script_name}",  # nom du fichier dans le bucket GCS
        bucket=BUCKET_SCRIPTS,
    )

def create_spark_transform_task(json_file: str):
    output_name = (
        "checkin" if "checkin_opti" in json_file else json_file.replace("yelp_academic_dataset_", "").replace(".json", "")
    )
    script_spark = f"{output_name}_transform.py"
    if script_spark not in PYTHON_SCRIPTS:
        return None
    return DataprocSubmitJobOperator(
        task_id=f"transform_{output_name}",
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": f"gs://{BUCKET_SCRIPTS}/{script_spark}",
                "args": [
                    f"gs://{BUCKET_RAW}/{DESTINATION_FOLDER}/{json_file}",
                    f"gs://{BUCKET_INTERMEDIATE}/parquet/{output_name}/"
                ]
            },
        },
        region=REGION,
        project_id=PROJECT_ID
    )

def load_parquet_to_bigquery(output_name: str):
    return GCSToBigQueryOperator(
        task_id=f"load_{output_name}_to_bq",
        bucket=BUCKET_INTERMEDIATE,
        source_objects=[f"parquet/{output_name}/*.parquet"],
        destination_project_dataset_table=f"{PROJECT_ID}.yelp.{output_name}",
        source_format='PARQUET',
        write_disposition='WRITE_TRUNCATE',  
        autodetect=True,
        create_disposition='CREATE_NEVER',
    )


with DAG(
    dag_id='upload_json_and_scripts_to_gcs',
    description='Upload dynamically all .json and .py files to GCS buckets',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=['upload', 'gcs', 'yelp', 'scripts']
) as dag:
    # Upload des fichiers JSON
    with TaskGroup("upload_jsons", tooltip="Upload all JSON files") as json_group:
        upload_json_tasks = [
            create_upload_json_task(json_file)
            for json_file in JSON_FILES
        ]

    # Upload des scripts .py
    with TaskGroup("upload_scripts", tooltip="Upload all PySpark and Python scripts") as script_group:
        upload_script_tasks = [
            upload_script_to_gcs(script_name)
            for script_name in PYTHON_SCRIPTS
        ]

    with TaskGroup("spark_transforms", tooltip="Apply Spark transformations on Dataproc") as transform_group:
        transform_tasks = []
        for json_file in JSON_FILES:
            if "checkin" in json_file and "opti" not in json_file:
                continue
            output_name = (
                "checkin" if "checkin_opti" in json_file else json_file.replace("yelp_academic_dataset_", "").replace(".json", "")
            )
            type_match = re.match(r"(business|review|tip|user|checkin)", output_name)
            if type_match:
                script_name = f"{type_match.group(1)}_transform.py"
            else:
                continue
            if script_name not in PYTHON_SCRIPTS:
                continue
            script_name = f"{output_name}_transform.py"
            task = create_spark_transform_task(json_file)
            if task:
                transform_tasks.append(task)
                # Sensor : vérifier que le fichier JSON est bien présent
                wait_for_json = GCSObjectExistenceSensor(
                    task_id=f"wait_for_json_{output_name}",
                    bucket=BUCKET_RAW,
                    object=f"{DESTINATION_FOLDER}/{json_file}",
                    timeout=120,
                    poke_interval=10,
                    mode='poke'
                )
                # Sensor : vérifier que le script Spark est bien présent
                wait_for_script = GCSObjectExistenceSensor(
                    task_id=f"wait_for_script_{output_name}",
                    bucket=BUCKET_SCRIPTS,
                    object=script_name,
                    timeout=120,
                    poke_interval=10,
                    mode='poke'
                )
                upload_task_id = f"upload_jsons.conditional_upload_json_{json_file.replace('.json', '')}"
                script_task_id = f"upload_scripts.upload_script_{output_name}_transform"
                dag.get_task(upload_task_id) >> wait_for_json
                dag.get_task(script_task_id) >> wait_for_script
                # Dépendances : attendre la présence du JSON + script avant de transformer
                [wait_for_json, wait_for_script] >> task

    with TaskGroup("load_to_bigquery", tooltip="Load Parquet into BigQuery") as load_group:
        load_tasks = []
        for json_file in JSON_FILES:
            if "checkin" in json_file and "opti" not in json_file:
                continue

            output_name = (
                "checkin" if "checkin_opti" in json_file
                else json_file.replace("yelp_academic_dataset_", "").replace(".json", "")
            )
            load_task = load_parquet_to_bigquery(output_name)
            load_tasks.append(load_task)
            
            transform_task_id = f"spark_transforms.transform_{output_name}"
            dag.get_task(transform_task_id) >> load_task