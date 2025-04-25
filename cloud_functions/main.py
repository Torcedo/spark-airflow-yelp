import functions_framework
import google.auth
import google.auth.transport.requests
import requests
import json

DAG_NAME = "parametrized_transform_dag"
PROJECT_ID = "datasparkyelp"
LOCATION = "europe-west1"
COMPOSER_ENV_NAME = "datasparkyelp-composer"

@functions_framework.cloud_event
def trigger_dag(cloud_event):
    data = cloud_event.data
    bucket = data['bucket']
    name = data['name']

    if not name.startswith("json_file/"):
        print(f"Ignoré : {name} n'est pas dans json_file")
        return 

    json_file_name = name.split("json_file/")[-1]

    # Authentification
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    id_token = credentials.token

    # Récupération de l'URL Airflow via l'API officielle
    composer_env_url = f"https://composer.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/environments/{COMPOSER_ENV_NAME}"
    env_resp = requests.get(composer_env_url, headers={"Authorization": f"Bearer {id_token}"})
    webserver_url = env_resp.json()["config"]["airflowUri"]

    # Appel vers Airflow pour créer un dagRun
    airflow_api_url = f"{webserver_url}/api/v1/dags/{DAG_NAME}/dagRuns"
    payload = {
        "dag_run_id": f"trigger-{json_file_name.replace('.', '-')}",
        "conf": {
            "json_file": json_file_name,
            "project_id": PROJECT_ID
        }
    }

    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(airflow_api_url, headers=headers, json=payload)

    if 200 <= response.status_code < 300:
        print(f"DAG {DAG_NAME} déclenché avec succès pour {json_file_name}")
    else:
        print(f"Erreur déclenchement DAG: {response.status_code} - {response.text}")
