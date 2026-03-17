# Journal - semaine 3 - 18 février
## Lecture et filtrage du corpus de flux RSS

> **Objectif** : ajouter des fonctions permettant de filtrer les données à charger en fonction de la date, de la source ou de la catégorie des articles.

## Répartition des rôles
- `r1` : filtrage en fonction de la **date** -> Anna (`as`), relue par Morgane
- `r2` : filtrage en fonction de la **source** -> Marc (`me`)
- `r3` : filtrage en fonction de la **catégorie** -> Morgane (`mb`), relue par Anna

## Exercice 1 - Lecture du code précédent
### Difficultés
1. Le code initial dont nous avons hérité ne fonctionnait que pour un fichier et non pour un corpus (dossier avec plusieurs fichiers).  
2. En outre, le code initial reposait exclusivement sur des arguments positionnels (la `methode` et le `fichier_xml` devaient être saisis dans un ordre strict, sans tirets). Une première correction du script a introduit des arguments optionnels (notamment le drapeau `-w` pour le `directory walker`), créant ainsi une interface "hybride" mélangeant arguments positionnels et optionnels (mauvaise idée !). Cette situation a posé plusieurs problèmes techniques majeurs lors de l'intégration des filtres.

### Solutions
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

## Exercice 2 - Nouvelles fonctionnalités
### Etape préliminaire
Nous avons décidé, d'un commun accord, après avoir rectifié le code dont nous avions hérité, de coder avant toutes choses la fonction filtrage ainsi que la structure "squelette" initiale et de définir les noms des fonctions, et ce afin de nous faciliter les merges à venir.
1. correction du code précédent
2. création de la fonction filtrage
3. création du squelette des trois fonctions `r1`, `r2` et `r3` avec leurs signatures et les docstrings.

### r1 : filtrage par date
```python
# r1 : filtrage par date
def filtre_date(item: dict) -> bool:
    """fonction de filtrage en fonction de la date.
    Les dates doivent être parsées avec le module 'datetime'"""
    return True
```
#### Difficultés
1. Les dates dans les flux RSS ne sont pas toutes écrites au même format, ce qui rend leur lecture difficile par le script.
2. Python refuse de comparer une date qui contient un fuseau horaire avec une date sans fuseau horaire.

#### Solutions
1. J'ai utilisé le module `dateutil.parser` car il est capable de lire automatiquement presque n'importe quel format de date.
2. Pour simplifier les comparaisons, j'ai supprimé les fuseaux horaires de toutes les dates avec `.replace(tzinfo=None)`. Ainsi, toutes les dates sont standardisées et la comparaison fonctionne sans erreur.
3. Si un article n'a pas de date, j'ai choisi de le garder par défaut pour ne pas perdre d'informations.

### r2 : filtrage par source

```python
# r2 : filtrage par source
def filtre_source(item: dict) -> bool:
    """fonction de filtrage en fonction de la ou des sources (nom du journal).
    1) filtrage des sources
    2) garantir l'unicité des articles"""
    return True
```
#### Difficultés
1. Problèmes lorqu'une seule source est données.
Python interprétait parfois l'argument comme une chaîne de caractères et non comme une liste. Le programme parcourait alors la chaîne lettre par lettre (b, l, a, s, t), ce qui produisait le double de résultats dont des faux résultats.
2. Sensible à la casse.
Les noms des sources dans les flux RSS ne sont pas homogènes (ex : "Blast -- articles.xml", "BFM --.xml"). Il faut donc qu'une entrée simple de l'utilisateur soit comprise et puisse récuperer les articles voulu.
3. Transformer les fonctions fonctions filtrage en fonction qui renvois un bool et qui est utilisé dans une plus grosse fonction. Ne dois pas traiter tout les articles mais juste un.

#### Solutions
1. Forcer la récupération sous forme de liste via argparse.
L’utilisation de nargs="+" dans le parser garantit que l’argument --source est toujours une liste, même si une seule source est fournie. Cela évite toute itération accidentelle caractère par caractère.
2. Normalisation des données et verification avec in
Grâce à .lower() et .strip(). Les chaînes issues du flux RSS et celles saisies par l’utilisateur sont transformées en minuscules avant comparaison, rendant le filtre moin sensible à la casse. Plutôt que de comparer strictement deux chaînes, la condition vérifie si la source recherchée est incluse dans la valeur du champ "source". Cela permet de gérer les formats du type "Blast -- articles.xml".
3. Transformation en fonction booléenne
La première version prenait une liste d’articles en entrée et renvoyait directement une liste filtrée. Pour la transformé en booléenne, il a fallut la moddfier en deplaçant une partie des verification et normalisation dans la fonction filtrage globale. Pour la fonction de gérant les répétition le choix à était fait de la garder comme dans la première version pour ne pas alourdir le script.

### r3 : filtrage par catégorie

```python
# r3 : filtrage par catégorie
def filtre_cat(article: dict, categories: list[str]) -> bool|None:
    """fonction de filtrage acceptant une ou plusieurs catégories indiquées dans les balises 'category' des fichiers XML."""
    check_cat = True
    article_categories = [cat.lower() for cat in article.get("categories", [])]
    for category in categories:
        if not category.strip().lower() in article_categories:
            check_cat = False
            break
    return check_cat
```
#### Difficultés
1. **Sensibilité à la casse** : Les catégories extraites des flux RSS (ex: "International") et celles saisies par l'utilisateur dans le terminal (ex: "international") ne correspondaient pas toujours. Une première tentative avec la méthode `.capitalize()` s'est avérée problématique, car elle mettait la première lettre en majuscule mais forçait le reste en minuscules, cassant les catégories composées (ex: "Home Police-Justice").
2. **Gestion des valeurs manquantes** : Certains articles du flux XML ne possédaient tout simplement pas de balise `<category>`. L'appel direct via `article["categories"]` risquait de faire planter le programme avec une KeyError.
3. **Incompatibilité des signatures de fonctions** : La consigne exigeait que la fonction maîtresse `filtrage()` boucle sur les filtres en utilisant `if not filtre(article):` (attendant donc une fonction à un seul argument). Or, filtre_cat nécessitait deux arguments (`article` et `filtres`).

#### Solutions
1. **Sensibilité à la casse** : Utilisation systématique de la méthode .lower() (associée à .strip()) à la fois sur les données extraites et sur les saisies utilisateur, garantissant une comparaison fiable indépendamment de la casse.
2. **Gestion des valeurs manquantes** : Sécurisation via `.get()` : Utilisation de `article.get("categories", [])` couplée à une liste en compréhension : `article_categories = [cat.lower() for cat in article.get("categories", [])]`. Ainsi, si la clé est absente, la fonction renvoie une liste vide, ce qui rejette "proprement" l'article sans faire planter le script (répondant ainsi à la consigne sur le traitement des valeurs manquantes).
3. **Incompatibilité des signatures de fonctions** : Pour respecter la signature à un seul argument requise par `filtrage()`, nous avons utilisé une fonction `lambda` au moment de l'ajout du filtre dans la liste des filtres actifs (`filtre_r3 = lambda article: filtre_cat(article, args.categories)`). C'est là que s'opère la fameuse *enclosure*, qui permet de "figer" et d'"encapsuler" les arguments de l'utilisateur (`args.categories`), de sorte que la fonction principale n'ait plus qu'à lui passer l'`article` courant pour l'évaluer, respectant ainsi l'architecture globale imposée.

## Exercice 3 - Mise en production
### Stratégie
Nous avons tâché, pour chacune des étapes du projet, de minimiser autant que faire se peut les risques de conflits de merge.
1. Définition d'une structure "squelette" commune avant de commencer à coder
2. Relecture mutuelle des fonctions `r1`, `r2` et `r3`
3. Merges successifs :  
a. de `r1` dans `r3`, puis  
b. de `r2` dans `r3 (+r1)`, puis  
c. de `r3 (+r1 +r2)` dans `main`.

### Difficultés
XXX
### Solutions
XXX
