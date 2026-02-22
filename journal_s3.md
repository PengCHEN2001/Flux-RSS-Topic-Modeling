# Journal - semaine 3 - 18 février
## Lecture et filtrage du corpus de flux RSS

> **Objectif** : ajouter des fonctions permettant de filtrer les données à charger en fonction de la date, de la source ou de la catégorie des articles.

### Répartition des rôles
- `r1` : filtrage en fonction de la **date** -> Anna
- `r2` : filtrage en fonction de la **source** -> Marc
- `r3` : filtrage en fonction de la **catégorie** -> Morgane

### Exercice 1 - Lecture du code précédent
#### Difficultés
Le script récupéré du groupe précédent ne fonctionnait que pour un fichier et non pour un corpus (dossier avec plusieurs fichiers).

#### Solutions
Nous avons récupéré sur la proposition de correction mise à disposition par les enseignants la partie manquante, de façon à avoir ce que les fonctions précédemment codées fournissent en sortie un output exploitable par les fonctions à développer par nos soins cette semaine.

### Exercice 2 - Nouvelles fonctionnalités
#### Difficultés
XXX
#### Solutions : étape préliminaire
Nous avons décidé, d'un commun accord, après avoir rectifié le code dont nous avions hérité, de coder avant toutes choses la fonction filtrage ainsi que la structure "squelette" initiale et de définir les noms des fonctions, et ce afin de nous faciliter les merges à venir.
1. correction du code précédent
2. création de la fonction filtrage
3. création du squelette des trois fonctions `r1`, `r2` et `r3` avec leurs signatures et les docstrings.

```python
# r1 : filtrage par date
def filtre_date(item: dict) -> bool:
    """fonction de filtrage en fonction de la date.
    Les dates doivent être parsées avec le module 'datetime'"""
    return True

#Difficultés
#1. Les dates dans les flux RSS ne sont pas toutes écrites au même format, ce qui rend leur lecture difficile par le script.
#2. Python refuse de comparer une date qui contient un fuseau horaire avec une date sans fuseau horaire.

#Solutions
#1. J'ai utilisé le module dateutil.parser car il est capable de lire automatiquement presque n'importe quel format de date.
#2. Pour simplifier les comparaisons, j'ai supprimé les fuseaux horaires de toutes les dates avec .replace(tzinfo=None). Ainsi, toutes les dates sont standardisées et la comparaison fonctionne sans erreur.
#3. Si un article n'a pas de date, j'ai choisi de le garder par défaut pour ne pas perdre d'informations.

# r2 : filtrage par source
def filtre_source(item: dict) -> bool:
    """fonction de filtrage en fonction de la ou des sources (nom du journal).
    1) filtrage des sources
    2) garantir l'unicité des articles"""
    return True


# r3 : filtrage par catégorie
def filtre_cat(item: dict) -> bool:
    """fonction de filtrage acceptant une ou plusieurs catégories indiquées dans les balises 'category' des fichiers XML."""
    return True
```

### Exercice 3 - Mise en production
#### Difficultés
XXX
#### Solutions
XXX
