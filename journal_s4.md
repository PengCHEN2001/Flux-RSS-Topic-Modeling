 # Journal - séance 4 - 11 mars 2026 - Refactorisation du code et sérialisation du corpus

## Exercice 1

### R2 - Anne-lx
Tout fonctionnait bien cette semaine donc on a pas eu de correction à faire. 
Je me suis occupée de séparer le code dans les deux fichiers distincts, j'ai galeré un petit moment pour réussir à tout démeler mais finalement ça a été.

**Difficultés rencontrées:**
Pour rss_reader j'ai eu du mal à réaliser qu'il fallait enlever le walker, ce qui a fait que j'ai tourné en rond pendant un moment.
```py
    """# Sélection du walker
    if args.directory_walker == "os":
        files = walk_os(args.fichier_xml)
    elif args.directory_walker == "pathlib":
        files = walk_pathlib(args.fichier_xml)
    elif args.directory_walker == "glob":
        files = walk_glob(args.fichier_xml)
    else:
        raise KeyError(f"Unknown walker: {args.directory_walker}")

    if not files:
        print("Aucun fichier XML trouvé.")
        sys.exit(1)

    articles = []

    for file in files:
        articles.extend(read_rss(args.methode, file))"""
```
Pour rss_parcours j'ai du modifier quelques lignes parce que ça ne marchait pas, en effet il fallait utiliser des dictionnaires au lieu de données avec des attributs directs.

```py 
def filtre_date(article: Article, start=None, end=None):
    # modif article.date en 
    if not article["date"]:
        return True
    # modif item_date = date_parser.parse(article.date).replace(tzinfo=None) en 
    try:
        item_date = date_parser.parse(article["date"]).replace(tzinfo=None)
```
avant l'article était un objet avec un attribut .date mais maintenant c'est un dico du coup on accède grace à la clef date

```py
def filtre_source(article: Article, sources):
    #modif if s.lower() in article.source.lower() en 
    for s in sources:
        if s.lower() in article["source"].lower():
```
etc, toutes les modifications sont indiquées directement dans le code.

### R3 - Anna Ushmarina
Cette semaine le code hérité est propre et fonctionnel : nous avons pu passé directement à l'Exercice 1. J'ai initialisé datastructures.py et défini la @dataclass Article avec ses champs en anglais.

**Difficultés rencontrée**
1. J'ai vite réalisé que remplacer nos dictionnaires par des objets risquait de faire planter tout le code (parseurs et filtres) géré par le reste de mon équipe.
2. Je devais absolument éviter le bug classique de la mémoire partagée en Python lors de l'initialisation de ma liste de catégories.

**Solutions**
1. J'ai appliqué un typage strict (`str`, `list[str]`) et j'ai utilisé `field(default_factory=list)` pour m'assurer que je créais bien une liste indépendante pour chaque article.
2. J'ai laissé des consignes claires dans le code pour mes coéquipiers, en leur expliquant qu'ils devaient désormais remplacer leur ancienne syntaxe `article["attribut"]` par `article.attribut`.



## Exercice 2

### R1 - Adriano Gallo

Pour l'Exercice 2, j'ai pris le rôle 1 (r1) sur ma propre branche. Ma mission : définir la structure de données Article commune à toute l'équipe, puis implémenter la sauvegarde et le chargement du corpus au format XML.

Difficultés rencontrées

Le format XML ne supporte pas nativement les listes Python. Le champ categories de Article (une list[str]) devait être sérialisé d'une façon que load_xml puisse reconstruire fidèlement.

Lors du chargement, il fallait reconstruire chaque objet Article depuis les nœuds XML sans perdre de données (valeurs vides, catégories manquantes).

Solutions

J'ai encodé les catégories en les joignant avec un séparateur ("|".join(value)) dans save_xml, et en les re-découpant avec split("|") dans load_xml, tout en filtrant les chaînes vides.

J'ai utilisé asdict() de la bibliothèque dataclasses pour convertir automatiquement chaque Article en dictionnaire lors de la sérialisation, ce qui évite de hardcoder les noms de champs et rend le code robuste aux futures modifications de la structure.
### R2 - Anne-lx

J'étais chargée de m'occuper de sauver et charger le corpus des articles au format JSON, tout d'abord j'ai crée un squelette pour le reste de mon groupe afin de rendre le merge plus simple.
Je me suis appuyée sur https://docs.python.org/3/library/json.html pour trouver les informations dont j'avais besoin, notamment le ensure_ascii=True, que je ne connaissais pas.

**Difficultés rencontrée**
Au début je me suis complétement trompée j'ai mélangé le fait d'avoir une liste de dictionnaires en entrée et une liste d'objets en sortie pour save_json et j'ai essayé de redonner une liste de dictionnaires en entrée pour load_json, ce qui n'avait pas de sens, j'ai tourné en rond sur le problème avant de comprendre.

**Solutions**
Mieux lire la documentation et réfléchir attentivement, aussi prendre le temps de vérifier la logique de ce que je suis en train de faire.


### R3 - Anna Ushmarina
Pour l'Exercice 2, j'ai pris le rôle 3 (r3) sur ma propre branche. Ma mission : gérer la sauvegarde et le chargement de notre corpus d'articles au format Pickle, puis préparer le script pour la fusion avec le reste de l'équipe.

**Difficultés rencontrée**
1. Contrairement aux formats texte classiques (comme le JSON ou le XML), Pickle sérialise les objets en binaire. Il fallait donc s'assurer de manipuler les fichiers correctement pour ne pas corrompre les données.

**Solutions**
1. J'ai codé save_pickle (wb avec pickle.dump) et load_pickle (rb avec pickle.load) en m'assurant de bien gérer l'ouverture des fichiers en mode binaire.

## Exercice 3
### R1 - Adriano Gallo

Lors de ma relecture du r2 de ma collègue, j'ai identifié plusieurs points à corriger.

Le bug le plus critique était dans save_json : la variable était déclarée donnees mais utilisée avec accent données.append(...) plus loin, ce qui aurait causé un NameError à l'exécution. J'ai uniformisé le nom.

J'ai aussi simplifié la construction du dictionnaire : au lieu de créer manuellement un dict champ par champ, j'ai utilisé asdict() de dataclasses, qui fait exactement la même chose de façon plus concise et robuste face aux futurs changements de structure.

Dans load_json, j'ai ajouté une vérification FileNotFoundError avant l'ouverture du fichier, et remplacé les accès directs item["key"] par item.get("key", "") pour éviter un crash si un champ est absent.




### R2 - Anne-lx

J'ai relu le code de r3, tout fonctionnait bien, j'ai juste pris la liberté de rajouter un Try et except pour mieux gérer les erreurs mais sinon je n'ai rien ajouté. Tag -relu ajouté.

### R3 - Anna Ushmarina

J'ai dû relire le code de r1. Dans l'ensemble, le script était bon ; j'ai restructuré un peu la fonction `load_xml` pour placer la partie `except` après le reste du code afin de faciliter la lisibilité et la fonctionnalité. Tag ajouté.

Après j'ai fait un merge de la branche r1 vers la mienne. Il y avait pas de conflit grâce à une skelette du script proposée par Anne. J'ai pu tout combiner et faire un push toujours sur ma branche. 
