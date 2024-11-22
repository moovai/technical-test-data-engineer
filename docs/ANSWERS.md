# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

C'était mon but de faire ce flux de données aussi simple et facile à utiliser que possible. Après avoir installé les
modules dans requirements.txt (pip install -r requirements.txt), le tout devrait fonctionner sans problèmes. Donc, les
étapes:

1 - pip install -r requirements.txt
2 - cd src/moovitamix_fastapi, python -m uvicorn main:app --reload
3 - python data_flux.py, ou rouler ça dans le IDE de votre choix

Après ça, vous pouvez simplement suivre le processus. Des petits notes expliquant ma démarche:

1 - Tous les fichiers que le flux crée vont se retrouver dans src/data. Plus sur ça en bas.
2 - Pour simuler le fait que ce flux est supposé d'opérer quotidiennement, le flux que j'ai fait va créer un fichier
    'last_run.json' qui va lui informer quand le dernier cycle a commencé. Le flux va donc opérer dans un while True
    loop et va utiliser sleep pour 24h après. Évidemment, dans un environnement production, je ne l'aurais pas fait
    comme ça; j'aurais plutôt utilisé des services d'orchestration, par exemple AWS EventBridge. Pour cette exemple,
    je pense que ce que j'ai fait sert comme une assez bonne démonstration. Si vous voulez voir l'opération plus vite,
    change data_flux.py ligne 201 à handle_process_interval(timedelta(seconds=x)), ou enlève le ainsi que ligne 197 
    complètement et ajuste les indentations si vous voulez seulement que ça roule juste une fois.
3 - Les instructions ont dit qu'on n'a pas besoin de faire un DB pour cette exercise, mais je voulais quand même faire
    quelque chose pour mieux visualiser la solution. Donc, le flux va créer un fichier csv en format pandas DataFrame
    pour chaque endpoint _ainsi_ qu'un SQLite DB (encore un fois, je ferais pas ça en production). Comme décrit avant,
    tous les fichiers se retrouveront dans src/data.

Quelque chose que j'ai noté mais pas osé de changer: TracksOut remplit le valuer de genre avec fake.word() au lieu
d'utiliser genres_list. J'étais un peu surpris par ça.


## Questions (étapes 4 à 7)

### Étape 4

Dans ce cas, vu qu'il y a un fort probabilité que les colonnes de chaque endpoint changeront pas souvent, j'ai osé
utiliser un DB relationnel et non quelque chose comme MongoDB. Je n'ai pas l'impression que la flexibilité offert 
par des DB non-relationnels sera utilisé souvent dans cette application.

En termes des tables, ils sont clairement décrites dans src/moovitamix_fastapi/models.py, mais je pense que ça vaut la
peine d'expliquer quelques décisions.

1 - Me basant sur le fait que chaque endpoint retourne un created_at et un updated_at pour chaque rangée de data (et le
    gros bon sens aussi ;) ), c'était assez clair pour moi que les colonnes 'id' ou 'user_id' devraient être des clés
    primaires; j'imagine qu'on n'aurait jamais besoin de deux rangées pour le même usager, et si les données d'un usager
    devraient changer, on pourrait update son rangée, et c'est pour ça que la colonne 'updated_at' existe :)
2 - La colonne 'user_id' de 'local_history' est un ForeignKey, pointant à 'id' de 'users'. Par contre, 'items' de 
    'local_history' réfère aux valeurs de 'id' de 'tracks', mais je ne l'ai pas mis comme ForeignKey. La raison, c'est
    que cette valeur est sérialisé en string avant d'être mis dans le DB.
3 - En plus, j'ai fait que la colonne 'email' devrait contenir des valeurs uniques, vu que le email est probablement
    ce qui distingue les usagers quand ils registrent leur compte.
4 - Tous les colonnes 'created_at' ou 'updated_at' sont de type datetime, et ont comme default value la date actuelle.
5 - Pour les colonnes 'id' ou 'user_id' j'ai utilisé le type Integer. Pour tout autre, String (ou Varchar).
6 - La longueur des colonnes a été fait avec cette logique: 
    (a) les colonnes ou l'usager doit selectionner un valeur provenant du système ou qu'ils peuvent pas entrer 
    manuellement ont des longueurs un peu plus long que la longueur maximum possible des réponses. Pour être plus clair,
    'gender' provient d'une liste, et la plus longue option est de 20 caractères. J'ai mis un longueur de 50 pour avoir 
    un assez grand 'safety margin' au cas ou des nouvelles options sont ajoutés au liste dans le futur. Pour 'duration' 
    j'ai mis un limite de 10 car c'est un mesure de temps et non un input, et 10 caractères de temps mettraient le track
    dans la magnitude de 1 à 10 jours. Peu probable mais on sait jamais :)
    (b) J'ai pas appliqué ce logique pour 'genres' ou 'favorite_genres', même si ils proviennent d'une liste de choix 
    aussi. Le fait que les mots soient pluriels suggère qu'un jour, ils peuvent contenir des combinaisons d'options de
    la liste, donc ça fait qu'il soit 'future proofed' à cet égard.
    (c) Pour tout autre string ou varchar, j'ai mis 255 caractères comme limite. C'est une bonne longueur pour assurer
    que l'usager n'aurait jamais trop peu de place, sans les laisser la possibilité de remplir la base de données avec 
    trop d'information, par accident ou par exprès.

Pour quelle type de DB relationnel, ma suggestion serait Posgres. Pour l'application tel quel, ça serait peut-être
un peu trop, mais ça donnerait du 'future proofing' à notre application qu'on apprécierait eventuellement. Par exemple,
on prendrait peut-être pas avantage des capacités de concurrence de Postgres si on écrit une fois par jour et lis pas
beaucoup plus souvent que ça, mais pour une application qui sert des milliers de clients, à quelque point, c'est
prévisible qu'on écrivera plus souvent qu'une fois par jour (peut-être on aurait tellement de données qu'on devrait
écrire des batch assez souvent), et on lira fort probablement très souvent pour entrainer les modèles. Postgres est
très capable de soutenir ces sortes de travaux, a des fonctionnalités au dela des DB comme MySQL, et peut facilement
être incorporé dans des solutions cloud comme AWS (que je vais beaucoup en discuter dans les prochains questions).

### Étape 5

Si on a un client, ça veut dire qu'on est en production, et si on est en production, ça nous aiderait beaucoup d'avoir
notre app sur un service cloud comme AWS. Je vais décrire ce que je ferais avec AWS, mais c'est certain que la logique
s'appliquerait assez bien pour n'importe quelle service cloud incorporant des fonctionnalités similaires (ou peut-être
des solutions à l'interne, si l'équipe a assez de temps):

CloudWatch pourrait beaucoup faire pour nous dans cette situation. Pour commencer, on pourrait ajouter des logs plus
robustes que ce que j'ai fait pour la démonstration en utilisant le Logger() class et faire de notre code beaucoup
plus verbose (expliquant ce qui se passe à chaque étape, utiliser les différentes classes de logging dont INFO,
WARNING, etc.). Comme ça, on pourrait consulter les logs de façon régulière pour nous assurer que tout va bien, et
voir ce qui s'est passé si tout ne va _pas_ bien. En plus, on pourrait l'utiliser pour vérifier des KPI comme
durée d'opération par cycle, ou temps pris pour que l'API répond, ou même la durée de temps que le API ou DB soient non
accessible ou le nombre d'erreurs subi par le flux dans une période de temps. On pourrait l'automatiser encore plus et
mettre en place des alarmes qui notifieraient des personnes concernées au cas ou des problèmes sont identifiées.
Finalement, on pourrait relier le tout avec AWS Lambda et EventBridge pour faire des inspections régulières définis par
ces mêmes personnes concernées. On pourrait même aller un autre pas d'avance et mettre en place des codes dans Lambda
pour redémarrer le API ou DB si ils sont non accessibles.

Ça dépend vraiment du temps qu'on a comme équipe; on peut faire des très belles choses avec des services cloud pour
faciliter notre vie :)
    

### Étape 6

C'est pour ça que c'est une bonne idée d'utiliser Postgres avec AWS RDS :) En supposant que tous les données qu'on a
besoin pour calculer nos recommandations proviennent du flux de données qu'on vient de développer, on pourrait
exploiter les fonctionnalités d'AWS pour faire le reste. Pour commencer, si on a besoin, on pourrait utiliser les
fonctionnalités ETL de AWS, dont Glue entre autres, pour transformer les données en format plus digestible pour les
modèles et, à la suite, à l'aide de Lambda, déplacer ces données transformés à un autre table du DB ou peut-être à S3. 
Après, on pourrait utiliser SageMaker pour faire le déploiement du modèle et le sauvegardement de ses prédictions
soit dans notre DB our sur S3. Finalement, l'application pourrait se mêler de transférer ces recommandations à l'usager,
peut-être avec un request API séparé qui est envoyé chaque fois que l'app est ouvert, ou chaque x minutes, etc. On va
falloir considérer aussi la fréquence avec laquelle on veut générer des nouvelles prédictions. Supposant qu'on veut
tout simplement produire des prédictions à une intervalle fixte et que l'usager va tout simplement recevoir les
prédictions les plus récentes (comme fait Spotify avec son Discover Weekly, qui roule assurément à une fréquence
hebdomadaire), on pourrait utiliser CloudWatch et EventBridge pour démarrer des jobs de calculation chaque heure, jour,
semaine, ..., à un temps prédéterminé.

Encore un fois, j'utilise AWS comme exemple, mais c'est certainement des étapes similaires pour des autres clouds comme
Google ou Azure :)

### Étape 7

Le processus ici serait similaire à un certain niveau à ce que j'ai décrit dans l'étape 6. On va quand-même avoir
besoin d'extraire nos données de RDS, on va peut-être avoir besoin de le transformer avec Glue et le stocker avec S3,
on va avoir besoin de SageMaker pour entraîner les modèles et pour les rouler, et on va devoir sauvegarder les modèles
et leurs prédictions quelque part comme S3 ou RDS (mais celui-ci, juste pour les prédictions, probablement), et on va
devoir établir une fréquence pour le tout. La plus grande différence serait probablement, en fait, la fréquence; on
pourrait bel et bien entraîner les modèles à des intervalles régulières, mais c'est probablement inefficace de l'en
faire. À place, ça serait plus logique d'établir des conditions qui déclencheraient un retraining. Par exemple, si on
utilise le pourcentage de chançons dans le 'listen_history' d'un usager qui étaient recommandé par les modèles, ou qui
sont du genre recommandé comme indicateur, on pourrait déclencher un retraining seulement quand cette indicateur tombe
en dessous d'un valeur prédéterminé. Encore une fois, ça s'accomplit assez facilement avec CloudWatch et Lambda, entre
autres. Après ça, comme dit avant, on extrait et transforme nos données, on les utilise pour faire le training d'un
nouveau modèle (incluant l'évaluation et déploiment du nouveau modèle), on stock les modèles et leurs prédictions
quelque part, et on laisse l'application interagir avec comme elle en veut :)



J'espère que j'ai pas trop écrit! Merci pour votre temps et pour l'opportunité, et avec un peu de bonne chance, à
bientôt :)
