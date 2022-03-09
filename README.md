

---

# Projet 3 : Base de données

![MongoDB logo](assets/images/mongodb-logo.png)


## Formation: Data Engineer

> **Auteurs**: 
> 
> * Christelle PATTYN
> * David CHARLES-ELIE-NELSON

---

<a name='cell-toc'></a>
## Sommaire:

   1. [Présentation](#section-presentation)  

      1.1. [Objectifs](#section-objectifs)  
      1.2. [Architecture du projet](#section-architecture)  
      1.3. [Jeu de données](#section-data)  
      1.4. [Système de base de données](#section-sys-db)  
      1.5. [Fonctionnalités de l'API](#section-api-functionalities)  

   2. [Contenu](#section-content)  

      2.1. [Technologies utilisées](#section-technos)  
      2.2. [Description du contenu du projet](#section-projet-content)
      
      
   3. [Mise en oeuvre du projet](#section-setup)  

      3.1. [Installation](#section-start-nodes)  
      3.2. [Tests de bon fonctionnement de l'API](#section-test-api)     
      3.3. [Requêter l'API](#section-use-api)

---

## 1. Présentation <a name='section-presentation'></a>
[Back to top](#cell-toc)<br/>

Ce projet a été réalisé dans le cadre de la formation de "**Data Engineer**" réalisée chez [DataScientest](https://datascientest.com/).


<br/>

### 1.1. Objectifs <a name='section-objectifs'></a>
[Back to top](#cell-toc)<br/>

L'objectif de ce projet est de choisir, mettre en place, et peupler une base de 
données à partir d'un jeu de données de l'open data, et d'implémenter une API permettant de requêter cette base de 
données.

Nous avons choisi un jeu de données historisant les transferts de footballeurs entre 2000 et 2018, disponible via le lien ci-dessous : 


•	https://www.kaggle.com/vardan95ghazaryan/top-250-football-transfers-from-2000-to-2018

Nous avons décidé de les intégrer dans une base MongoDB, ie une base NoSQL orientée documents. 

Une API a ensuite été créée afin de consulter ces données à partir d'un certain nombre de requêtes, et modifier ces données. L'ensemble des fonctionnalités de l'API est décrite dans la partie [Fonctionnalités de l'API](#section-api-functionalities) 

<br/>

### 1.2. Architecture du projet <a name='section-architecture'></a>
[Back to top](#cell-toc)<br/>

Le projet repose sur les éléments suivants:

   * **API REST**  
     développée en Python avec la librairie Flask  
     L'API sera hébergée dans un container Docker appelé: <span style='color:darkmagenta;'>project3-api-server</span>
     
   * **Serveur de Base de données**  
     Dans le cadre de ce projet c'est MongoDB qui a été utilisé.  
     Le serveur de base de données sera également hébergé dans un container Docker appelé: <span style='color:darkmagenta;'>project3-mongo-server</span>

   * **Module de chargement de données**  
     Ce module a pour objectif de charger les données (contenues intialement dans le fichier <span style='color:darkgreen;'>data/top250-00-19.csv</sapn> depuis la racine du projet) au sein de la base de données MongoDB.  
     Le container Docker correspondant à ce module a pour nom: <span style='color:darkmagenta;'>project3-mongo-loader</span>

   * **Machine hôte**  
     La machine hôte est la machine à partir de laquelle le projet sera mis en oeuvre et démarré.  
     C'est donc elle qui hébergera les containers Docker composant le projet.

A noter que l'ensemble des containers Docker évoqués ci-dessus (project3-api-server, project3-mongo-server, project3-mongo-loader) seront pilotés par le biais de Docker Compose.

La logique est la suivante:

   * Lors de la phase de démarrage de ces containers via Docker Compose, chacun d'eux respectera l'ordre suivant:
      - <u>project3-mongo-server</u>  
        Ce container contient la base de données et est donc nécessaire au bon fonctionnement de l'API.  
        Ce container sera donc systématiquement démarré en premier.  
        Puisque ce container est basé sur l'image mongo:latest, il hérite du mode de fonctionnement suivant:  
        lorsque ce container est démarré pour la première fois, la base de données n'est pas détectée et est
        donc créée automatiquement (le paramétrage de la création de la base de données peut être contrôlée par le biais 
        de variables d'environnement ; permettant notamment de définir le login/password du compte qui permettra de se 
        connecter à la base).  
        Les données de la base de données seront persistantes car le container héberge les fichiers mongo dans un volume
        Docker. Ainsi, même après un arrêt de ce container, les données seront retrouvées une fois que celui-ci aura été
        redémarré.

      - <u>project3-mongo-loader</u>  
        Ce container a pour but de charger la base de données avec les données initialement contenues dans un fichier csv.  
        Même si le chargement des données n'est nécessaire qu'une seule fois (après la création de la base qui est déclenchée lors du tout premier démarrage du container project3-mongo-server), ce container sera systématiquement démarré 
        par Docker Compose. Ce mode de fonctionnement permet de laisser l'opportunité à ce container de s'assurer que la collection cible est bien présente dans la base "Football" au sein de MongoDB. Si la collection est détectée alors le travail de ce container prend fin et le container s'arrête automatiquement. Si par contre, il ne détecte par la présence 
        de la collection, alors la tâche de chargement de données sera démarrée et la base de données sera ré-initialisée 
        avec les données contenues dans le fichier csv.  
        Le chargement des données est géré par un programme Python dont le code est disponible depuis le répertoire 
        src > mongo-loader à partir de la racine du projet.

      - <u>project3-api-server</u>  
        Ce container héberge l'API et est donc dépendant des deux premiers autres containers.  
        Le fait de démarrer en dernier l'API permet à la fois d'avoir une base de données déjà démarrée et également chargée avec les données.

Les communications entre la base mongo et les deux autres containers seront rendues possibles grâce au réseau Docker 
nommé <span style='color:darkmagenta;'>project3-net-bdd</span>.  
De plus, le port local 27017 de la machine hôte sera redirigé vers le port d'écoute de MongoDB (port: 27017) sur le container project3-mongo-server. Cette redirection est assurée par Docker Compose et a pour but de laisser un accès direct
à la base de données depuis la machine hôte. C'est donc par ce biais qu'il sera possible de requêter l'API depuis la machine hôte.


<br/>

### 1.3. Jeu de données <a name='section-data'></a>
[Back to top](#cell-toc)<br/>

Le jeu de données qui a été choisi dans le cadre de ce projet est accessible: [ici](https://www.kaggle.com/vardan95ghazaryan/top-250-football-transfers-from-2000-to-2018)  

Il s'agit de l'ensemble de données des 250 transferts de football les plus chers de la saison 2000-2001 à 2018-2019.  
Le jeu de données a été créé le 1er août 2018 et pour cette raison il peut contenir une liste incomplète pour la dernière partie (été 2018).

Le jeu de données est composé de:
   - 4700 lignes au total
   - 10 colonnes 

Il contient les informations suivantes:
   - le nom d'un joueur de football  
   - l'équipe et la ligue d'où part le joueur
   - l'équipe et la ligue où le joueur arrive
   - une valeur marchande estimée d'un joueur  
   - une valeur réelle d'un transfert  
   - la position d'un joueur au moment du transfert
   - la saison pendant laquelle le transfert a eu lieu

Ce jeu de données est contenu dans le fichier data/<span style='color:darkgreen;'>top250-00-19.csv</span> depuis la racine du projet.


<br/>

### 1.4. Système de base de données <a name='section-sys-db'></a>
[Back to top](#cell-toc)<br/>

Nous avons choisi d'utiliser MongoDB pour héberger les données du projet.  
Le jeu de données initial étant très structuré, nous aurions pu opter pour une base de données RDBMS classique telle que PostgreSQL ; néanmoins notre choix s'est finalement porté sur MongoDB plus pour le fait de vouloir travailler avec une base de données de type NoSQL que par des contraintes liées au jeu de données.

Les données sont donc finalement stockées en base sous un format document tel que celui-ci:

```
{
      "name": "<prénom et nom du joueur>"
   ,  "transfers": [
         {
               "age": <age du joueur au moment du transfert>
            ,  "position": "<position du joueur au moment du transfert>"
            ,  "league": {
                     "from": "<league d'où provient le joueur>"
                  ,  "to": "<league où le joueur est transféré>"
               }
            ,  "team": {
                     "from": "<équipe d'où provient le joueur>"
                  ,  "to": "<équipe où le joueur est transféré>"
               }
            ,  "season": {
                     "begYear": "<année de début de saison>"
                  ,  "endYear": "<année de fin de saison>"
               }
            ,  "cost": {
                     "estimation": "<estimation du montant du transfert du joueur sur le marché>"
                  ,  "réel": "<coût réel du transfert du joueur>"
               }
         }
      ]
}
```


<br/>

### 1.5. Fonctionnalités de l'API <a name='section-api-functionalities'></a>
[Back to top](#cell-toc)<br/>

Voici les routes, statuts et fonctionnalités associées de l'API :  

<br/>

| Type | Route | Fonctionnalité   
| :--- | :--- | :--- 
| GET  | <span style='color:blue;'>/status</span> | permet de vérifier la disponibilité de l'API depuis une machine cliente
| GET  | <span style='color:blue;'>/status/db</span> | permet de vérifier la disponibilité de l'API depuis une machine cliente, ainsi que l'accès à la base de données
| GET  | <span style='color:blue;'>/players/count</span> | renvoie le nombre de joueurs référencés dans la base de données
| GET  | <span style='color:blue;'>/player/find_one</span> | renvoie le premier joueur trouvé en base de données avec l'ensemble des informations qui lui sont associé
| GET  | <span style='color:blue;'>/player/id/<string:id\></span> | renvoie les informations concernant le joueur correspondant à l'ID fourni en argument 
| GET  | <span style='color:blue;'>/player/names</span> | renvoie le noms de tous les joueurs référencés dans la base de données 
| GET  | <span style='color:blue;'>/player/name/<string:name\></span> | renvoie les joueurs dont le nom contient <pattern>, sans tenir compte de la casse
| POST | <span style='color:blue;'>/player/byname</span> | recherche un joueur par son nom exact. PARAM body : Playername
| GET  | <span style='color:blue;'>/transfer/count/per_player</span> | renvoie le nombre de transfers réalisés par joueur 
| GET  | <span style='color:blue;'>/TransfersNbPerTeamFrom</span> | compte le nombre de transfert par équipe d'origine 
| GET  | <span style='color:blue;'>/TransfersNbPerTeamTo</span> | compte le nombre de transfert par équipe cible du transfert
| GET  | <span style='color:blue;'>/TransfersCostMaxPerTeam</span> | compte le transfert le plus cher par équipe
| GET  | <span style='color:blue;'>/league/names</span> | renvoie l'ensemble des noms de league référencés dans la base de données
| GET  | <span style='color:blue;'>/team/names</span> | renvoie l'ensemble des noms d'équipes référencés dans la base de données 
| GET  | <span style='color:blue;'>/teams_per_league</span> | renvoie l'ensemble des noms de clubs référencés dans la base de données par league
| POST | <span style='color:blue;'>/players_left_league_on_period</span> | l'ensemble des noms de joueurs ayant quittés une league donnée sur une période donnée. PARAM body : league_name (nom league), beg_year (année début de période), end_year (année fin de période)
| POST | <span style='color:blue;'>/player/add</span> | ajoute un joueur et son ou ses transferts si le joueur n'existe pas déjà, sinon ajoute uniquement le transfert. PARAM body : name, transfers (liste contenant un ou plusieurs dictionnaires des transfers)

Un exemple des appels pour chacune de ces routes est disponible dans le répertoire "client/postman" depuis la racine du projet.


<br/>

## 2. Contenu <a name='section-content'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 2.1. Technologies utilisées <a name='section-technos'></a>
[Back to top](#cell-toc)<br/>

Dans le cadre de ce projet nous avons utilisés les briques techniques suivantes:

   * **DOCKER**  
   
     Docker est la technologie de containerisation qui a été utilisée pour créer les containers hébergeant:  
     
     * l'API  
     * la base de données MongoDB
     * le client responsable du chargement des données dans la base de données


   * **MONGODB**  
 
     Le type de base de données ayant été retenu pour stocker les données du projet.


   * **PYTHON**  
  
     Le langage de développement utilisé pour coder l'API ainsi que le client responsable du chargement des données.
     Les librairies suivantes ont été utilisées:
         * pymongo
         * flask


<br/>

### 2.2. Description du contenu du projet <a name='section-projet-content'></a>
[Back to top](#cell-toc)<br/>

Le projet est accessible:
   - soit depuis une archive tgz (fournie à DataScientest)
   - soit depuis [github](https://github.com/dav-chris/project-3)

> Vous trouverez ci-dessous un descriptif du contenu du répertoire racine du projet:


   * <span style='color:darkgreen;'>assets</span>  
     Ce répertoire ne contient pas d'information essentielle au projet (il peut être ignoré).  
     Il ne contient que l'image correspondant au logo de MongoDB.

   * <span style='color:darkgreen;'>build</span>  
     répertoire contenant tous les éléments nécessaires à la construction des images Docker.  

     Chaque image Docker possède son répertoire dans <span style='color:darkgreen;'>build/docker/images</span>

      * <span style='color:darkcyan;'>api-server</span>  
        répertoire correspondant à l'image project3-api-server.  
        Cette image contient l'API  et écoute par défaut sur le port 5000 et sur l'ip 0.0.0.0.  
        Il est possible de configurer l'IP et le port d'écoute de l'API par le biais de variables d'environnement.

      * <span style='color:darkcyan;'>ubuntu-python</span>  
        répertoire correspondant à l'image project3-ubuntu-python.  
        Cette image est construite à partir d'une image ubuntu sur laquelle a été installé un environnement Python.
        Elle sert de base à la fois pour l'API ainsi que pour le client qui réalise le chargement des données en 
        base.

      * <span style='color:darkcyan;'>mongo-client</span>  
        répertoire correspondant à l'image project3-mongo-client.  
        Cette image est construite à partir de l'image ubuntu-python sur laquelle a été installée le driver Python pour MongoDB (pymongo).

      * <span style='color:darkcyan;'>mongo-loader</span>  
        répertoire correspondant à l'image project3-mongo-loader.  
        Cette image est construite à partir de l'image project3-mongo-client sur laquelle a été installée le programme Python qui sert à charger les données dans la base Mongo.

   * <span style='color:darkgreen;'>client/postman</span>  
    répertoire contenant un fichier de configuration Postman (postman_collection.json) dans lequel a été exporté un ensemble de requêtes de test de l'API.  

   * <span style='color:darkgreen;'>data</span>  
    répertoire hébergeant le fichier de données (top250-00-19.csv) utilisé pour charger la base de données Mongo.  


   * <span style='color:darkgreen;'>src</span>  
     répertoire contenant les fichiers source développés en language Python.
     On y trouvera notamment les sous -répertoires suivants:  

      * <span style='color:darkgreen;'>api</span>  
       répertoire hébergeant le code source de l'API.  

      * <span style='color:darkgreen;'>mongo-loader</span>  
       répertoire hébergeant le code source ayant été utilisé pour charger les données depuis le fichier csv dans la base Mongo.  

La racine du projet contient en plus, les fichiers suivants:

   * <span style='color:darkgreen;'>docker-compose.yml</span>  
     le fichier de configuration Docker Compose chargé de gérer la construction et le démarrage des containers utilisés par ce projet.

   * <span style='color:darkgreen;'>README.md</span>  
     ce fichier readme.


<br/>

## 3. Mise en oeuvre du projet <a name='section-setup'></a>
[Back to top](#cell-toc)<br/>



<br/>

### 3.1. Installation <a name='section-start-nodes'></a>
[Back to top](#cell-toc)<br/>

Vous trouverez ci-dessous une procédure décrivant comment installer et démarrer l'API du projet

La procédure d'installation qui est décrite ci-dessous suppose que nous disposions de deux machines:

   - <u>une machine hôte</u>  
     (hébergeant les containers correspondant à l'API et à la base de données)  
     Dans notre cas, nous avons pris la VM mise à disposition par datascientest pour héberger l'API.  
     Pour l'équipe datascientest, n'importe quelle machine (Linux de préférence) disposant du prérequis suivant devrait convenir:
     
      - docker version >= 20.10.12 installé et démon Docker démarré            
  
   - <u>une machine cliente</u>  
     Il s'agit d'une machine depuis laquelle les clients de l'API initieront leurs requêtes vers l'API. Pour l'équipe datatascientest, n'importe quelle machine ayant accès à la machine hôte fera l'affaire.
     
     Il faudra de plus veiller à ce qu'une connexion ssh soit possible entre le poste client et la machine hôte. Cette condition est nécessaire pour permettre la mise en place d'une redirection de port via ssh entre ces deux machines.

La procédure décrite ci-dessous permettra le déploiement et la mise en service de l'API sur la machine hôte. 

---

<u>Procédure de déploiement et démarrage de l'API</u>:

**1. Connectez vous sur la machine hôte**  

**2. Rendez vous dans un répertoire dans lequel nous allons récupérer le projet**  

**3. Récupération du projet depuis Github**  
  
Exécuter la commande suivante:

```bash
git clone https://github.com/dav-chris/project-3.git ./project
```

Le résultat devrait être le suivant:  
un répertoire nommé "project" devrait avoir été créé contenant tout le projet.  

Si pour quelque raison que ce soit, des difficultés étaient rencontrées lors de cette étape, il serait alors possible d'extraire le projet depuis l'archive qui a été fournie à DataScientest à l'aide de la commande suivante (en ayant pris soin préalablement d'être positionné dans le répertoire devant contenir le projet):

```bash
tar xvfz project3-deploiement.tgz
```

Désormais avec l'une des deux commandes présentées ci-dessus nous devrions avoir le répertoire "project" présent dans le répertoire courant.

**4. Construction des images Docker**  

Comme précisé dans le chapitre "Architecture du projet" le projet est composé de plusieurs conteneurs Docker:

   * **project3-mongo-server**  
     Ce conteneur contient le serveur MongoDB.  
     Il est construit à partir d'une image Docker ("mongo:latest") qui est une image officielle maintenue par [the Docker Community](https://github.com/docker-library/mongo)  
     Puisque nous utiliserons une image déjà disponible pour ce container il n'y a rien besoin de faire pour ce conteneur. L'image existante sera simplement téléchargée et utilisée par Docker Compose pour la construction du conteneur.
     
   * **project3-mongo-loader**  
     Ce conteneur aura pour tâche de créer et d'alimenter la collection au sein d'une base MongoDB avec les données.  
     Le chargement à proprement parler est réalisé par un programme Python.  
     Pour son bon fonctionnement le conteneur a donc besoin que Python soit installé ainsi que ses dépendances (en l'occurrence la librairie pymongo).  
     La construction de ce conteneur sera réalisée comme suit:
        - à partir de l'image <span style='color:darkmagenta;'>project3-ubuntu-python</span>  
          cette image n'est rien d'autre que l'image <span style='color:darkmagenta;'>ubuntu:latest</span> sur laquelle nous installons Python.
        - depuis l'image <span style='color:darkmagenta;'>project3-ubuntu-python</span> nous construisons l'image <span style='color:darkmagenta;'>project3-mongo-client</span> sur laquelle nous installons les dépendances Python dont aura besoin le "loader" (à savoir pymongo).

Les commandes suivantes vont donc permettre de construire les images Docker nécessaires à l'instanciation des conteneurs Docker:

**[*] Construction de l'image Docker: project3-ubuntu-python**

Dans une console, depuis la racine du projet, exécutez la commande suivante:

```bash
docker image build                                     \
   --file build/docker/images/ubuntu-python/Dockerfile \
   --pull                                              \
   --tag project3-ubuntu-python                        \
   .
```


**[*] Construction de l'image Docker: project3-mongo-client**

Dans une console, depuis la racine du projet, exécutez la commande suivante:

```bash
docker image build                                    \
   --file build/docker/images/mongo-client/Dockerfile \
   --tag project3-mongo-client                        \
   .
```

A noter que les images Docker suivantes seront construites directement par Docker Compose:
   - <span style='color:darkmagenta;'>project3-mongo-loader</span>
   - <span style='color:darkmagenta;'>project3-api-server</span>


**5. Lancement des conteneurs**  

A la racine du projet, vous devriez trouver le fichier docker-compose.yml

Pour lancer l'exécution des conteneurs, voici la commande :

```bash
docker-compose up --build -d
```

Vérifier que les conteneurs sont bien actifs : 
```bash
docker container ls
```
Vous devriez trouver les conteneurs : 
   - project3-mongo-server
   - project3-api-cont 

Le conteneur project3-mongo-loader s'est arrêté dès que le chargement des données s'est effectué (si les données n'existaient pas déjà).

<br/>

### 3.2. Tests de bon fonctionnement de l'API <a name='section-test-api'></a>
[Back to top](#cell-toc)<br/>

Voici quelques commandes qui permettent de vérifier le bon fonctionnement de l'API, à lancer de la machine hôte :

* Tester la disponibilité de l'API

```bash
curl -X GET http://localhost:5000/status  
```

* Tester la disponibilité de l'API et l'accès à la base de données

```bash
curl -X GET http://localhost:5000/status/db
```

* Compter le nombre de joueurs

```bash
curl -X GET http://localhost:5000/players/count
```

* Rechercher un joueur par un prénom ou un nom de famille

```bash
curl -X GET http://localhost:5000/player/name/Zinedine
```

* Rechercher un joueur par son nom complet (prénom nom)

```bash
curl -iX POST localhost:5000/player/byname -d '{"PlayerName":"Giangiacomo Magnani"}' -H 'Content-Type: application/json'
```
   
* Rechercher le premier joueur trouvé en base de données

```bash
curl -X GET http://localhost:5000/player/find_one
```

* Rechercher un joueur par son identifiant  
Récupérer l'identifiant $oid de la requête find_one ci-dessus et remplacer l'identifiant indiqué ci-dessous :
   
```bash
curl -X GET http://localhost:5000/player/id/621cdf4aca20a455e291218a 
```

<br/>

### 3.3. Requêter l'API <a name='section-use-api'></a>
[Back to top](#cell-toc)<br/>

La procédure décrite ci-dessous permettra de valider le bon fonctionnement de l'API en réalisant des requêtes de test.  

**1. Connection à la machine cliente**  

Connectez vous sur la machine cliente (machine  différente de celle où tourne l'API), sur laquelle vous pouvez ouvrir un browser avec Postman par exemple.
   
**2. Redirection de port**

Pour que la machine cliente puisse joindre l'API, nous allons dans un premier temps devoir faire une redirection de port. Pour cela, exécutez la commande suivante en prenant soin de remplacer:
   - <key.pem\>  
     par le nom du fichier correspondant à la clé permettant de se connecter à la machine server
     
   - <username\>  
     par le nom du compte utilisateur permettant de se connecter à la machine server depuis la machine cliente       

   - <machine_server_ip\>  
     par l'adresse IP de la machine qui contient l'API

   - <service_port\>  
     par le port du service exposée par l'API (indiquée dans le fichier docker-compose)   
     

```bash
ssh -i <key.pem\> <username\>@<machine_server_ip\> -fNL 5000:localhost\>:<service_port\>
```

Exemple:
>
>   `ssh -i "data_enginering_machine.pem" ubuntu@34.240.96.199 -fNL 5000:localhost:5000`

**3. Requêter l'API via Postman**

Importer dans Postman le fichier disponible dans le répertoire projet client/postman

Lancer les exemples de requêtes prédéfinies pour l'ensemble des routes de l'API.


