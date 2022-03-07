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

      3.1. [Démarrage des noeuds](#section-start-nodes)  
      3.2. [Tests de bon fonctionnement de l'API](#section-test-api)     
      3.3. [Requêter l'API](#section-use-api)

---

## 1. Présentation <a name='section-presentation'></a>
[Back to top](#cell-toc)<br/>

Ce projet a été réalisé dans le cadre de la formation de "**Data Engineer**" réalisée chez [DataScientest](https://datascientest.com/).


<br/>

### 1.1. Objectifs <a name='section-objectifs'></a>
[Back to top](#cell-toc)<br/>

L'objectif de ce dernier projet est de choisir, mettre en place, et peupler une base de 
données à partir d'un jeu de données de l'open data, et d'implémenter une API permettant de requêter cette base de 
données.


<br/>

### 1.2. Architecture du projet <a name='section-architecture'></a>
[Back to top](#cell-toc)<br/>

Le projet repose sur les éléments suivants:

   * **API REST**  
     développée en Python avec la librairie Flask  
     L'API sera hébergée dans un container Docker appelé: <span style='color:darkmagenta;'>project3-api-server</span>
     
   * **Serveur de Base de données**  
     Dans le cadre de ce projet c'est MongoDB qui a été utilisée.  
     Le serveur de base de données sera également hébergé dans un container Docker appelé: <span style='color:darkmagenta;'>project3-mongo-server</span>

   * **Module de chargement de données**  
     Ce module a pour objectif de charger les données (contenues intialement dans le fichier <span style='color:darkgreen;'>data/top250-00-19.csv</sapn> depuis la racine du projet) au sein de la base de données MongoDB.  
     Le container Docker correspondant à ce module a pour nom: <span style='color:darkmagenta;'>project3-mongo-loader</span>

   * **Machine hôte**  
     La machine hôte est la machine à partir de laquelle le projet sera mis en oeuvre et démarré.  
     C'est donc elle qui hébergera les containers Docker composant le projet.

A noter que l'ensemble des containers Docker évoqués ci-dessus (project3-api-server, project3-mongo-server, project3-mongo-loader) seront pilotés par le biais de Docker Compose.

La logique est la suivante:

   * Lors de la phase de démarrage de ces containers via Docker Compose, chacun d'eux démarreront en respectant l'ordre suivant:
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
        par Docker Compose. Ce mode de fonctionnement permet de laisser l'opportunité à ce container de s'assurer que collection cible est bien présente dans la base "Football" au sein de MongoDB. Si la collection est détectée alors le travail de ce container prend fin et le container s'arrête automatiquement. Si par contre, il ne détecte par la présence 
        de la collection, alors la tâche de chargement de données sera démarrée et la base de données sera ré-initialisée 
        avec les données contenues dans le fichier csv.  
        Le chargement des données est géré par un programme Python dont le code est disponible depuis le répertoire 
        src > mongo-loader à partir de la racine du projet.

      - <u>project3-api-server</u>  
        Ce container héberge l'API et est donc dépend des deux premiers autres containers.  
        Le fait de démarrer en dernier l'API permet à la fois d'avoir une base de données déjà démarrée et également chargée avec les données.

Les communications entre la base mongo et les deux autres containers seront rendues possibles grâce au réseau Docker 
nommé <span style='color:darkmagenta;'>project3-net-bdd</span>.  
De plus, le port local 27017 de la machine hôte sera redirigé vers le port d'écoute de MongoDB (port: 27017) sur le container project3-mongo-server. Cette redirection est assurée par Docker Compose et a pour but de laisser un accès direct
à la base de données depuis la machine hôte. C'est donc par ce biais qu'il sera possible de requêter l'API depuis la machine hôte.


<br/>

### 1.3. Jeu de données <a name='section-data'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 1.4. Système de base de données <a name='section-sys-db'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 1.5. Fonctionnalités de l'API <a name='section-api-functionalities'></a>
[Back to top](#cell-toc)<br/>


<br/>

## 2. Contenu <a name='section-content'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 2.1. Technologies utilisées <a name='section-technos'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 2.2. Description du contenu du projet <a name='section-projet-content'></a>
[Back to top](#cell-toc)<br/>



<br/>

## 3. Mise en oeuvre du projet <a name='section-setup'></a>
[Back to top](#cell-toc)<br/>



<br/>

### 3.1. Démarrage des noeuds <a name='section-start-nodes'></a>
[Back to top](#cell-toc)<br/>

<br/>

### 3.2. Tests de bon fonctionnement de l'API <a name='section-test-api'></a>
[Back to top](#cell-toc)<br/>


<br/>

### 3.3. Requêter l'API <a name='section-use-api'></a>
[Back to top](#cell-toc)<br/>

