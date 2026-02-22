# Journal - semaine 3 - 18 février
## Lecture et filtrage du corpus de flux RSS

> **Objectif** : ajouter des fonctions permettant de filtrer les données à charger en fonction de la date, de la source ou de la catégorie des articles.

### Répartition des rôles
- `r1` : filtrage en fonction de la **date** -> Anna
- `r2` : filtrage en fonction de la **source** -> Marc
- `r3` : filtrage en fonction de la **catégorie** -> Morgane

### Exercice 1 - Lecture du code précédent
#### Difficultés
1. Le code initial dont nous avons hérité ne fonctionnait que pour un fichier et non pour un corpus (dossier avec plusieurs fichiers).  
2. En outre, le code initial reposait exclusivement sur des arguments positionnels (la `methode` et le `fichier_xml` devaient être saisis dans un ordre strict, sans tirets). Une première correction du script a introduit des arguments optionnels (notamment le drapeau `-w` pour le `directory walker`), créant ainsi une interface "hybride" mélangeant arguments positionnels et optionnels (mauvaise idée !). Cette situation a posé plusieurs problèmes techniques majeurs lors de l'intégration des filtres.

#### Solutions
1. Nous avons récupéré sur la proposition de correction mise à disposition par les enseignants la partie manquante, de façon à avoir ce que les fonctions précédemment codées fournissent en sortie un output exploitable par les fonctions à développer par nos soins cette semaine.
2. Pour résoudre les problèmes posés par l'interface hybride, mélangeant arguments positionnels et optionnels, et anticiper le merge final, nous avons harmonisé l'ensemble du *parser*. Les anciens arguments positionnels ont tous été transformés en arguments optionnels nommés (`-m` / `--methode` et `--corpus`). Ainsi, l'ordre de saisie n'a plus aucune importance : chaque tiret agit désormais comme une barrière naturelle pour clôturer les listes de filtres, rendant le script robuste et intuitif.

```python
parser = argparse.ArgumentParser(
        description="Lire un fichier xml (flux RSS) avec une méthode à choisir",
        epilog="Exemple d'utilisation avec filtre : python3 rss_reader.py -w glob -m feedparser --corpus ./corpus/ -c spiritueux vins"
    )

    parser.add_argument(
        "-w", "--directory-walker",
        choices=("os", "pathlib", "glob"),
        default="glob"
    )

    parser.add_argument(
        "-m", "--methode",
        choices=("re", "etree", "feedparser"),
        help="Méthode à utiliser : re, etree ou feedparser",
        default="feedparser",
    )

    parser.add_argument(
        "--corpus",
        dest="fichier_xml",
        required=True,
        help="Chemin vers un fichier XML ou un dossier contenant des XML",
    )

    parser.add_argument(
        "-c", "--categories",
        nargs="+", # pour récupérer une liste de mots
        help="Filtrer par une ou plusieurs catégories."
    )
```

### Exercice 2 - Nouvelles fonctionnalités
#### Difficultés


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
def filtre_cat(item: dict, categories: list[str]) -> bool:
    """fonction de filtrage acceptant une ou plusieurs catégories indiquées dans les balises 'category' des fichiers XML."""
    return True
```

### Exercice 3 - Mise en production
#### Difficultés
XXX
#### Solutions
XXX
