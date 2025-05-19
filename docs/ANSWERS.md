# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

Si vous exécutez ces commandes, le pipeline fonctionnera:

```bash
docker compose up --build
```

La première fois il va aussi falloir exécuter:
```bash
chmod +x run_pipeline.sh
```

Pour terminer:
```bash
docker compose down -v
```


J'ai choisi un script shell simple qui peut être programmé quotidiennement avec une tâche cron. Je sauvegarde les métadonnées d'exécution pour le suivi de data lineage ou poure faire un audit. Dans le cas où on aurait besoin d'un framework plus complexe, je peux toujours utiliser un outil comme Airflow/Mage pour l'open source et ADF/AWS Glue pour un framework géré dans le cloud.

Pour la quantité de données traitée, j’ai utilisé Pandas et chargé l’ensemble des données en mémoire, ce qui n’est clairement pas scalable pour de gros volumes. Dans ce cas, on privilégie l’usage de fonctions génératrices et de stratégies de "chunking" pour créer dynamiquement des fichiers exploitables et les ingérer en aval dans un stockage cloud.

Pour les tests unitaires dans mon flux de données, il était important de valider le code source généré, puis avec l'output j'ai aussi validé les relations entre les données, les types de données, l'existence des fichiers et la taille des données attendues.


## Questions (étapes 4 à 7)

### Étape 4

On va utiliser un star schéma simple, où la table de faits est l'historique d'ecoute et les dimensions sont les utilisateurs et les tracks. Les données elles-mêmes sont conformes à SCD1 et si les données étaient plus désordonnées, nous mettrions en œuvre une architecture en médaillon pour garantir que plusieurs couches de données puissent être davantage nettoyées tout en conservant les entrées brutes pour la traçabilité et l'audit. 
En termes de système/outillage de base de données: je proposerais un système de lakehouse qui nous offre une flexibilité des formats, y compris des compressions optimisées et partitioning/clustering avec une facilité d'intégration de l'apprentissage automatique pour notre cas d'utilisation. Snowflake/BigQuery/Databricks comme suggestions d'outil.

### Étape 5

Intégrer avec des outils de surveillance comme Prometheus/Grafana ou utiliser des options intégrées fournies par les fournisseurs cloud. Établir des tableaux de bord de surveillance avec des métriques clés telles que le temps d'exécution du pipeline, l'exhaustivité des données (comptages de données de départ vs comptages de données finales), les taux d'erreur, la fraîcheur des données. Mettre en œuvre des alertes et des notifications et definir un data SLA avec le client.

### Étape 6

Je mettrais en place le systeme suivant:
- Un mécanisme programmé qui s'exécute quotidiennement ou hebdomadairement après l'ingestion réussie des données, garantissant que les recommandations sont basées sur les données les plus récentes.
- Implementation de modeles qui extrait les caractéristiques pertinentes de l'historique d'écoute, y compris les préférences de genre, les artistes fréquemment écoutés et les habitudes d'écoute temporelles.
- Implémentation d'algorithmes comme le filtrage collaboratif ou les recommandations basées sur le contenu, selon le modèle pré-entraîné.
- Une logique spécifique pour traiter les nouveaux utilisateurs sans historique d'écoute, en s'appuyant sur les tendances populaires ou les similitudes démographiques.


### Étape 7

On peut mettre en place un réentraînement automatique basé soit sur la performance, soit sur un horaire planifié.
Pour un déclenchement basé sur la performance, on peut s’appuyer sur l’utilisation réelle des playlists recommandées : clics, temps d’écoute, taux d’engagement, etc.
Sinon, on peut tout simplement planifier un réentraînement quotidien, hebdomadaire ou mensuel, en accord avec les data scientists.

Techniquement, une fois qu’on reçoit le signal en amont (performance ou horaire), on lance le pipeline de réentraînement du système de recommandations. Celui-ci effectue les étapes clés comme le feature engineering, le filtrage collaboratif, etc.

Si on doit aller plus loin et modifier ou affiner le modèle lui-même, on intègre tout ça dans un framework CI/CD avec des tests automatisés pour garantir la stabilité.
En aval, on déploie via un test A/B : certains utilisateurs reçoivent les recommandations de l’ancien modèle, d’autres celles du nouveau. Ça permet de mesurer concrètement l’impact des changements.
