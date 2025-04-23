# Projet d'Ingestion de Données Yelp sur Google Cloud Platform

## Contexte du Projet

L'objectif de ce projet est d'assimiler et maîtriser les technologies cloud proposées par Google Cloud Platform (GCP) à travers un cas concret d'ingestion et de traitement de données issues du dataset Yelp. Ce projet illustre un traitement par batch avec une approche ELT (Extract, Load, Transform), dans laquelle les données sont d'abord chargées telles quelles dans le data lake (Cloud Storage), puis transformées via Spark (Dataproc) avant d'être chargées dans l'entrepôt de données (BigQuery).
Les données transformées pourraient être utilisées pour la création de dashboards analytiques ou pour proposer des recommandations personnalisées aux utilisateurs finaux.

Ce projet est basé sur une architecture en médaillon, permettant une gestion optimale des données en plusieurs niveaux : bronze (raw), silver (intermediate) et gold(structuré pour analyse dans bigquery).
Le DAG à été fait sous 2 formes différentes avec dags_airflow qui me permettais de faire toutes mes transformations sur un dossier en LOCAL via docker et dags_airflow_cloud
qui comme son nom l'indique fait le DAG mais cette fois-ci dans le cloud spécifiquement sur un fichier. Grâce à la définition d'une Cloud Function, dès qu'un fichier arrivait
il est soumis au DAG pour être ingérer.
## Technologies et Outils Utilisés

- **Google Cloud Platform (GCP)**
  - Cloud Storage
  - BigQuery
  - Dataproc (configuration : master `e2-standard-4`, workers `e2-standard-2`, image `2.1-debian11` stable PySpark)
  - Cloud Composer (Airflow)

- **Terraform** (Infrastructure as Code)
- **Docker Compose** (Environnement de développement reproductible)
- **Apache Spark (PySpark)** (Transformations distribuées)
- **Apache Airflow** (Orchestration automatisée)

## Structure du Projet
```text
├── dags                         # Définition des DAG Airflow
│   └── __pycache__/
├── data                         # Données sources JSON
├── docker                       # Configuration Docker et Docker Compose
├── gcp-creds                    # Fichiers d'authentification GCP
├── intermediate                 # Données transformées (Parquet)
│   └── datasparkyelp-yelp-intermediate
│       ├── business
│       ├── review
│       ├── tip
│       ├── user
│       └── checkin
├── spark                        # Scripts PySpark pour transformations
└── terraform                    # Infrastructure as Code avec Terraform
    ├── .terraform
    │   ├── modules
    │   └── providers
    │       └── registry.terraform.io
    │           └── hashicorp
    │               └── google
    │                   └── 5.45.2
    │                       └── windows_386
    └── modules
        ├── bigquery            # Schémas et ressources BigQuery
        │   └── schemas
        ├── composer            # Déploiement de Cloud Composer
        ├── dataproc            # Configuration des clusters Dataproc
        └── storage             # Buckets Cloud Storage
```
## Étapes de Déploiement

### 1. Configuration initiale

- Générer une clé de service depuis GCP avec les permissions nécessaires (Storage Admin, BigQuery Admin, Dataproc Admin, Composer Admin).
- Placer le fichier JSON des credentials dans le dossier `gcp-creds/`.
- Initialiser l’environnement Docker pour le développement local :

  docker-compose up -d

### 2. Déploiement de l’infrastructure avec Terraform

  cd terraform
  terraform init
  terraform plan
  terraform apply

Cela crée :
- les buckets Cloud Storage (`raw`, `intermediate`, etc.)
- un cluster Dataproc avec Spark installé
- un environnement Cloud Composer (Airflow)
- les tables BigQuery avec les schémas défini

### 3. Orchestration via Airflow

Le DAG Airflow orchestre les étapes suivantes :
1. Upload des fichiers `.json` vers le bucket `raw`
2. Upload des scripts Spark vers le bucket `spark-scripts`
3. Exécution des scripts PySpark via Dataproc pour transformer les données
4. Stockage des fichiers Parquet dans le bucket `intermediate`
5. Chargement final des fichiers Parquet vers BigQuery
<img width="224" alt="image" src="https://github.com/user-attachments/assets/9554c407-7c2b-4e98-9a71-73a6d10fc011" />

## Difficultés rencontrées & Optimisations réalisées

- Problème de mémoire lors du traitement Spark du fichier `checkin.json` (1,3M lignes)
  → Résolu par traitement itératif des timestamps et transformation en format long
- Utilisation de fichiers Parquet partitionnés pour améliorer les performances de lecture BigQuery
- Conteneurisation de Spark avec Docker pour contourner les limites de compatibilité Hadoop sur Windows

## Applications potentielles

- Création de dashboards analytiques (ex: Looker Studio)
- Analyse de sentiment ou recommandations personnalisées à partir des reviews Yelp
- Études de comportements clients ou performances des commerces par région

---

```

