# Réponses du test


Lancez le serveur.
Allez dans "/solutions" 
Installez les librairies necessaires via "pip install -r requirements.txt"
Lancez le code via ligne de commande, comme avec: 

python dailyRoutine.py -url [URL_DU_SERVEUR] -schedule_date 14:34

-url: l'url du serveur
-schedule_date: l'heure a laquelle l'operation quotidienne est prevue (pour tester, mettez l'heure actuelle +1 minute)

Note: Vous pouvez lancer le script avec l'argument "-nowait" pour lancer le script immédiatement



### Étape 3: Pas de tests?

=> J'ai laissé la phase de test vers la fin du test technique, et j'ai réalisé qu'utiliser un parser d'argument et que mon architecture rendait cela plus compliqué que prévu. Je préfère vous rendre le test technique sans les tests unitaires que de passer deux heures à debugger le tout (sachant que mon setup de python ne trouve pas les modules de pytest correctement, il n'était pas configuré correctement à l'avance sur mon ordinateur personel).

J'ai tout de même ajouté "test_solution" pour écrire quels tests j'aurai écris sinon.


## Questions (étapes 4 à 7)

### Étape 4

(Cf l'image)

Chaque Users n'a qu'un seule historique d'écoute.

Chaque historique d'écoute a plusieurs musiques et une musique peut avoir plusieurs historique d'écoutes.

L'idée est de créer une table intermédiaire "Occurrences De Musiques" liés à l'historique.

De ce fait, un historique d'écoute a plusieurs occurrences de musiques, mais une musique n'a qu'une seule occurrence de musiques /!\ pour un historique de musique donné /!\

### Étape 5

Les métriques les plus importantes à vérifier sont:

- La qualité des données, si notre base de données a des champs manquant ou si elles font sens. 
=> Compter les champs nuls dans notre BDD, ou tester les données entrantes (ou seulement une partie si nous traitons énormément de données)

- Le rendement des données, comme le temps de nos requêtes ou celui des mises à jours de nos processus.
=> Optimiser le code et la gestion des informations.
Par exemple, il serait plus intelligent de faire plusieurs requêtes différentes tout le long de la journée pour ne pas avoir a tout traiter d'un coup.

- La rentabilité de notre algorithme, nécessaire pour évaluer l'efficacité de nos recommandations de musique. Pour cela, il faudra probablement ajouter a la base de données des valeurs de "score de recommandations", pour savoir si un utilisateur a plus écouté de musiques du genre conseillé ou non.

- Je ne pense pas que la sécurité des données soit réellement observable via nos bases de données et algorithmes, mais un ensemble de tests de stress serait nécessaire a minima.


### Étape 6


Afin d'effectuer des recommandations, il nous faut un algorithme de machine learning qui prends en entrée un utilisateur avec son historique de musiques, et qui nous donne en sortie une ou plusieurs musiques recommandés.

Il faudrait alors développer un algorithme de machine learning, ici je choisirais l'approche d'intelligence artificielle par réseaux de neurones, mais d'autres approches existent en fonction de notre budget et quantité de données.


Le facteur majeur qu'il reste a déterminé, c'est de trouver un moyen d'évaluer la "likability" qu'un utilisateur aurait envers une chanson.


En effet, il serait maladroit de recommender du jazz a un utilisateur qui n'a écouté une musique de jazz que pendant 3 secondes contre la musique au complet, ou si l'utilisateur a écouté une musique plusieurs fois ou non. Il faudrait donc ajouter une métrique d'écoute et utiliser le nombre de fois que l'utilisateur a écouté chaque morceau.


Ainsi, avec cette contrainte en tête, il suffirait d'entrainer un réseau de neurones qui prends en entré un utilisateur et la liste d'écoute ainsi que à quel point il écoute chaque musiques pour produire une liste de morceau recommandé.


L'implémentation serait donc la suivante:

Créer ce réseau de neurones, utiliser les données de notre base de données pour l'entrainer et créer notre modèle.
Puis, à chaque fois que l'utilisateur écoute une nouvelle chanson, aka met à jour sa liste de lecture, il suffit que son application envoi une requête au serveur selon un nouveau endpoint Rest:

@app.get("/updateRecommendations", tags=["HTTP methods"])
async def updateRecommendation(user, newListenHistory) -> Page[TracksOut]:
	// Fetch the model

	// Inject the new data to the model

	// Get the recommended tracks

	// Show the tracks to the user
	return tracks


### Étape 7

En partant du principe que nous possédons déjà un modèle d'apprentissage intégré à notre pipeline et que nous avons nos Bases de données prêtes à l'instant T.

Notre modèle a besoin de données pour s'entrainer et se tester. A l'état T, nous disposons déjà de la Base de donnée actuelle.

Pour accéder à ces données, nous n'avons besoin que des ID de chaque donnée. 

Ainsi, à l'instant T, nous aurions un fichier train_ID contenant les ID de nos données que nous utiliserons pour la phase d'entrainement, et un fichier test_ID avec lequel nous évaluons la précision de notre modèle.


Dés lors que de nouvelles données apparaissent à l'instant T+1, il suffit d'incrémenter ces fichier train_ID et test_ID avec les ID des nouvelles données récupérées quotidiennement, répartissant environs 80% d'entre elle dans l'entrainement et le reste pour la validation, et il suffira alors de mettre a jour le modèle de notre algorithme une fois l'entrainement finis.


A noter que, en fonction du temps d'entrainement, il serait peut être judicieux d'entrainer notre modèle moins souvent que notre BDD n'est à jour, à T+3 par exemple ou lorsqu'on a un nombre significatif de nouvelles données.




