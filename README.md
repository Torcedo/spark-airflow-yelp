# Projet d'Ingestion de Données Yelp sur Google Cloud Platform

## Contexte du Projet

L'objectif de ce projet est d'assimiler et maîtriser les technologies cloud proposées par Google Cloud Platform (GCP) à travers un cas concret d'ingestion et de traitement de données issues du dataset Yelp. Les données transformées pourraient être utilisées pour la création de dashboards analytiques ou pour proposer des recommandations personnalisées aux utilisateurs finaux.

Ce projet est basé sur une architecture en médaillon, permettant une gestion optimale des données en plusieurs niveaux : brut (raw), intermédiaire (transformé) et final (structuré pour analyse).

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
