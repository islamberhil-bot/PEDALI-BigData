# PEDALI — Plateforme Big Data

Projet universitaire — Ecosysteme Big Data 2
Annee universitaire 2026-2027

## Objectif

Construire une plateforme Big Data pour analyser les trajets
de velos et trottinettes PEDALI dans quatre villes marocaines :
Casablanca, Rabat, Marrakech et Tanger.

## Architecture

- Docker et Docker Compose : conteneurisation
- Apache Spark 3.5.3 : traitement distribue
- Spark Master et deux Workers
- Apache Kafka 3.9.1 : ingestion des evenements
- MinIO : stockage Data Lake
- JupyterLab : notebooks PySpark
- Parquet : stockage analytique Silver

## Jalon 1 — Parties 1, 2 et 3

### Partie 1 : Infrastructure

- Cluster Spark Standalone avec 2 Workers
- Topic Kafka `trips` avec 3 partitions
- Bucket MinIO `lake`
- Jupyter connecte au Master Spark
- Test distribue sur 1000 elements

Master Spark :
spark://spark-master:7077

### Partie 2 : Spark RDD

50 000 evenements JSONL generes.

Repartition :
- ENDED : 30 228
- RESERVED : 7 425
- UNLOCKED : 7 387
- CANCELLED : 3 453
- FAULT_REPORTED : 1 507

Chiffre d'affaires des trajets termines :
- Casablanca : 174 698,09 MAD
- Marrakech : 173 034,32 MAD
- Tanger : 172 358,22 MAD
- Rabat : 172 312,90 MAD

Total : 692 403,53 MAD

Analyses RDD :
- Chiffre d'affaires par ville
- Duree moyenne par ville et type de vehicule
- Top 5 des stations de depart
- Lineage, DAG, stages et shuffle

### Partie 3 : Spark SQL et DataFrames

- Lecture JSON avec schema explicite
- Comparaison RDD / DataFrame / SQL
- Jointure avec un referentiel de 400 stations
- Analyse des types de zones
- Comparaison UDF Python et fonctions natives
- Analyse des plans avec explain(True)
- Export Silver en Parquet partitionne par ville

Validation :
- RDD = DataFrame = SQL (a l'arrondi pres)
- 0 difference entre UDF et fonctions natives
- 0 trajet ENDED sans station correspondante
- 30 228 lignes Silver
- 4 partitions geographiques

## Organisation

- notebooks/ : traitements Jupyter
- scripts/ : generation et utilitaires
- data/ : donnees locales
- config/ : configurations
- spark-apps/ : tests Spark
- results/ : resultats et captures
- graphx/ : travaux du jalon 2

## Demarrage

Les services Spark sont actuellement definis dans
compose.spark.yml et partagent le reseau Docker pedali-test.

Commande pour demarrer Spark :

docker compose -f compose.spark.yml up -d --pull never

Les conteneurs Kafka, MinIO et Jupyter doivent egalement
etre demarres. Une configuration Compose unique sera
ajoutee pour automatiser leur lancement.

## Interfaces

- Spark Master : http://localhost:8080
- JupyterLab : http://localhost:8889
- Spark Driver UI : http://localhost:4040
- MinIO Console : http://localhost:9001

Les ports Spark Driver peuvent varier selon les sessions.

## Remarques

Le jeu de donnees est synthetique.
Les resultats correspondent a une execution de test.
Les secrets MinIO ne doivent pas etre publies sur GitHub.
