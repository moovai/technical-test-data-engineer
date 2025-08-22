# Réponses du test

- [INFO] la méthode Page.with_custom_options a été supprimée en v0.13 j'ai rétrogadé la lib de votre api et j'ai maj requirements.txt pip install "fastapi-pagination<0.13"

J'ai proposé une solution relativement simple car je ne vois pas l'intérêt de complexifier inutilement ce processus, mais on peut ajouter du traitement en fonction de l'utilisation des données, principalement dans le fichier de normalisation.

https://pypi.org/project/pandas/
https://pypi.org/project/httpx/
https://blog.alphorm.com/maitriser-yield-python

## Questions (étapes 4 à 7)

### Étape 4

Je travaille actuellement avec neo4j c'est donc tout naturellement que je proposerais cette solution, c'est une base graph adaptée à la recommandation et utilisant Cypher. Cypher permet d’exprimer et d’exécuter facilement des traversées multi-sauts (plus simple que sql). Je proposerai un modèle avec 4 noeuds de base :User, :Track, :Artist, :Genre reliés par des relations comme :LISTENED, :PERFORMED_BY, :HAS_GENRE et :SIMILAR (bien sûr ça peut largement être évolutif en fonction des variables récupérées = genre, age etc). Cette solution permet de réaliser des requêtes de recommandation sans jointures sql complexes.


### Étape 5

Possibilité de mettre des logs pour suivre l'état du pipeline durant son processus et un script qui mesure son état en fonction des mesures paramétrées (durée, succès etc) avec une alerte mail à partir d'une plage d'écart. Le pipeline est vraiment très simple alors des logs au niveau de l'appel API me semblent important et une vérification de l'enregistrement des données dans la db mais pas besoin de plus.

### Étape 6

À chaque nouvelle ingestion des données on refait un calcul de similarité sur les utilisateurs, les morceaux, les albums, les artistes en fonction des titres écouté par les utilisateurs, en limitant le nombre de titre, pour ne garder que les meilleurs voisins et pour ne garder que ce qui est récent.

### Étape 7

Je mettrais des logs pour vérifier les performances des recommandations en fonction des scores de similarité présent dans la db. Si les logs indiquent que les utilisateurs sont moins satisfait de leur recommandation (seuil) cela déclencherait un ré-entrainement du modèle avec un versionning pour ne pas écraser le précédent modèle et je ferais de l'A/B testing pour vérifier la pertinence du nouveau modèle en fonction du précédent.

