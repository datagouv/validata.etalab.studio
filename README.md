# Préambule
Ce dépôt a pour but d'héberger les fichiers de configuration nécessaires 
au bon déploiement de l'outil Validata Table sur le serveur de data.gouv.fr.

Ce dépôt n'a pas vocation à héberger de code source.

Ce document a pour but de détailler la procédure de déploiement de 
l'outil Validata Table (issu du projet gitlab [Validata Table](https://gitlab.com/validata-table/validata-table)) 
sur le serveur de data.gouv.fr.


# Déploiement de l'outil Validata Table sur le serveur de data.gouv.fr

Le serveur de data.gouv.fr héberge deux services distincts :
- l'interface utilisateur de Validata Table : [Validata.fr](https://validata.fr/)
- l'[API de Validata Table](https://api.validata.etalab.studio/apidocs)

Le déploiement de chacun de ces deux services se fait par le biais 
de deux docker-compose distincts.

Pour chacun des deux services, deux environnements Docker sont déployés :
- un environnement de préproduction
- un environnement de production

L'ensemble des fichiers de configuration des environnements Docker sont hébergés sur le dépôt 
GitHub de data.gouv.fr [validata.etalab.studio](https://github.com/etalab/validata.etalab.studio)

NB : Historiquement la configuration des environnements Docker liée au service de l'API de Validata
Table était hébergée sur un dépôt GitHub de data.gouv.fr distinct
[api.validata.etalab.studio](https://github.com/etalab/api.validata.etalab.studio).
Avec le travail réalisé dans le cadre de la mise en place d'un mono-repo 
sur le projet [Validata Table](https://gitlab.com/validata-table/validata-table) et la réalisation 
d'un nouveau package commun `validata-table` utilisé par l'interface utilisateur et l'API, ce dépôt 
api.validata.etalab.studio n'a plus raison d'être utilisé dans le déploiement de l'outil Validata Table.

## Procédure de déploiement

NB : Cette procédure est actuellement appliquée par l'équipe de multi (Amélie Rondot), 
sous vérification de l'équipe de data.gouv.fr (Geoffrey Aldebert et Pierlou Ramade)

### Etapes préalables à la mise en préproduction :
- Sur une machine quelconque :
  - Récupération du code source du dépôt GitHub de data.gouv.fr [validata.etalab.studio](https://github.com/etalab/validata.etalab.studio)
    par un `git clone`
  - Création d'une branche de travail locale à partir de la branche `preprod` : 
  ```
  git checkout preprod
  git checkout -b "work-branch"
  ```
  - Modification du fichier des [requirements.txt](https://github.com/etalab/validata.etalab.studio/blob/766ac9bf46ca6202a0f0b29e55f287fbf5f09dc4/requirements.txt) 
  pour modifier la version du package `validata-table` selon sa dernière version disponible, 
  et commit des modifications dans cette branche de travail `work-branch` et `push`de cette branche sur le dépôt 
  distant :
  ```
  git add requirements.txt && git commit -m "update validata-table version package"
  git push origin work-branch
  ```
- Sur le dépôt GitHub de data.gouv.fr [validata.etalab.studio](https://github.com/etalab/validata.etalab.studio) : 
  - Réalisation d'une PR de cette branche de travail `work-branch` vers la branche `preprod` 
  avec demande de review auprès de l'équipe de data.gouv.fr (Geoffrey Aldebert et Pierlou Ramade)
  - Review par l'équipe de data.gouv.fr de la PR
  - SI la PR est validée par l'équipe de data.gouv.fr, cliquer sur `Merge pull request` dans l'interface du dépôt GitHub

### Mise en préproduction
- Sur le serveur de data.gouv.fr (accès privé)
  - se placer dans le dossier correspondant à l'environnement de préproduction 
  de l'interface utilisateur :
  ```commandline
  cd preprod.validata.etalab.studio
  ```
  - faire un `pull` de la branche de `preprod`
  ```commandline
  git checkout preprod
  git pull preprod
  ```
  - vérifier que le fichier `.env` existe dans ce répertoire et intègre toutes 
  les variables d'environnement requises au bon fonctionnement de la préproduction :
    - ENV_NAME=preprod
    - FLASK_SECRET_KEY=***
    - PORT_NUMBER=5060
    - PORT_NUMBER_API=5070
  
  #### Déploiement de l'interface utilisateur
  - Builder et lancer l'environnement Docker permettant de déployer 
  l'interface utilisateur de Validata Table en préproduction :
  ```
  docker-compose up --build -d
  ```
  - Vérifier le comportement attendu de l'interface utilisateur en préproduction sur
  https://preprod-validata.dataeng.etalab.studio/
  (conjointement équipe multi et équipe de data.gouv.fr)

  #### Déploiement de l'API
  - Builder et lancer l'environnement Docker permettant de déployer 
  l'API de Validata Table en préproduction :
  ```
  docker-compose -f docker-compose.api.yml up --build -d
  ```
  - Vérifier le comportement attendu de l'API en préproduction sur
  https://preprod-api-validata.dataeng.etalab.studio/ 
  (conjointement équipe multi et équipe de data.gouv.fr)

### Etapes préalables à la mise en production :
Si le comportement observé en préproduction correspond au comportement attendu
relatif la montée de version du package `validata-table`, poursuivre les étapes suivantes
pour la mise en production :

- Sur le dépôt GitHub de data.gouv.fr [validata.etalab.studio](https://github.com/etalab/validata.etalab.studio) : 
  - Création d'une PR de la branche `preprod` vers la branche `master` 
  avec demande de review auprès de l'équipe de data.gouv.fr (Geoffrey Aldebert et Pierlou Ramade)
  - Review par l'équipe de data.gouv.fr de la PR
  - Si la PR est validée par l'équipe de data.gouv.fr, cliquer sur `Merge pull request` dans l'interface du dépôt GitHub

### Mise en production :
- Sur le serveur de data.gouv.fr (accès privé)
  - se placer dans le dossier correspondant à l'environnement de production 
  de l'interface utilisateur :
  ```commandline
  cd validata.etalab.studio
  ```
  - faire un `pull` de la branche de `master`
  ```commandline
  git checkout master
  git pull master
  ```
  - vérifier que le fichier `.env` existe dans ce répertoire et intègre toutes 
  les variables d'environnement requises au bon fonctionnement de la production :
    - ENV_NAME=prod
    - FLASK_SECRET_KEY=***
    - PORT_NUMBER=5059
    - PORT_NUMBER_API=5069
  
  #### Déploiement de l'interface utilisateur
  - Builder et lancer l'environnement Docker permettant de déployer 
  l'interface utilisateur de Validata Table en production :
  ```
  docker-compose up --build -d
  ```
  - Vérifier le comportement attendu de l'interface utilisateur en préproduction sur
  https://validata.fr/
  (conjointement équipe multi et équipe de data.gouv.fr)

  #### Déploiement de l'API
  - Builder et lancer l'environnement Docker permettant de déployer 
  l'API de Validata Table en production :
  ```
  docker-compose -f docker-compose.api.yml up --build -d
  ```
  - Vérifier le comportement attendu de l'API en production sur
  https://api.validata.etalab.studio/apidocs
  (conjointement équipe multi et équipe de data.gouv.fr)
  
# Notes complémentaires
### Caractéristiques du serveur de data.gouv.fr
- OS utilisé : à compléter
- La version de `docker-compose` utilisée sur le serveur de data.gouv.fr est la `1.29.2` :
```
docker-compose version
>>>
docker-compose version 1.29.2, build 5becea4c
docker-py version: 5.0.0
CPython version: 3.7.10
OpenSSL version: OpenSSL 1.1.0l  10 Sep 2019
```
Il est à noter que depuis juillet 2023 la version `v1` de Docker Compose 
n'est plus maintenue, [cf doc](https://docs.docker.com/compose/).
Il est donc recommandé de migrer Docker Compose vers la version 2 sur le serveur de data.gouv.fr.

- La version de `docker`utilisée sur le serveur de data.gouv.fr est la `20.10.8` :
```
docker version
>>>
Client: Docker Engine - Community
 Version:           20.10.8
 API version:       1.41
 Go version:        go1.16.6
 Git commit:        3967b7d
 Built:             Fri Jul 30 19:54:02 2021
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.8
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.16.6
  Git commit:       75249d8
  Built:            Fri Jul 30 19:52:10 2021
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.4.9
  GitCommit:        e25210fe30a0a703442421b0f60afac609f950a3
 runc:
  Version:          1.0.1
  GitCommit:        v1.0.1-0-g4144b63
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```
