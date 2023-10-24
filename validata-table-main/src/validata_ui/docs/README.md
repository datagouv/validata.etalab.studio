# Validata UI

Validata UI est une application Web dédiée à la validation de fichiers tabulaires (CSV, Excel, OpenOffice Calc) par rapport à un schéma de table (cf. [spécification Frictionless](https://specs.frictionlessdata.io/table-schema/) en anglais).

En savoir plus sur le projet [Validata](https://validata.fr/doku.php "Voir le site officiel").

## Questions fréquemment posées (FAQ)

### Une erreur est survenue durant la validation

Cette intitulé est suivi par un message en anglais qui signale généralement un problème de cohérence entre le schéma choisi et le contenu du fichier à valider.

#### primary key

Si le message d'erreur contient l'expression `primary key`, il est probable que le problème provienne d'une colonne déclarée comme _clef primaire_ dans le schéma et absente du fichier tabulaire à valider.

2 possibilités de correction :

- retirer la propriété `primaryKey` du schéma
- ajouter la colonne manquante dans le fichier tabulaire à valider

#### constraint "pattern"

Si le message d'erreur contient `constraint "pattern" is "` suivi d'une série de caractères, il est probable que le problème vienne d'une erreur de syntaxe dans la définition d'une [expression régulière](https://fr.wikipedia.org/wiki/Expression_r%C3%A9guli%C3%A8re "page Wikipedia") dans le schéma utilisé.

2 possibilités de correction :

- corriger la syntaxe de l'expression régulière utilisée
- retirer la contrainte d'expression régulière en la remplaçant si c'est possible par
  - d'autres [contraintes](https://specs.frictionlessdata.io/table-schema/#constraints "Documentation TableSchema") proposées par tableschema
  - un [custom check](https://gitlab.com/validata-table/validata-core/-/blob/master/validata_core/custom_checks/README.md "Documentation Validata") adapté
