 # Journal - séance 4 - 11 mars 2026 - Refactorisation du code et sérialisation du corpus

## Exercice 1

### R3 - Anna Ushmarina
Cette semaine le code hérité est propre et fonctionnel : nous avons pu passé directement à l'Exercice 1. J'ai initialisé datastructures.py et défini la @dataclass Article avec ses champs en anglais.

**Difficultés rencontrée**
1. J'ai vite réalisé que remplacer nos dictionnaires par des objets risquait de faire planter tout le code (parseurs et filtres) géré par le reste de mon équipe.
2. Je devais absolument éviter le bug classique de la mémoire partagée en Python lors de l'initialisation de ma liste de catégories.

**Solutions**
1. J'ai appliqué un typage strict (`str`, `list[str]`) et j'ai utilisé `field(default_factory=list)` pour m'assurer que je créais bien une liste indépendante pour chaque article.
2. J'ai laissé des consignes claires dans le code pour mes coéquipiers, en leur expliquant qu'ils devaient désormais remplacer leur ancienne syntaxe `article["attribut"]` par `article.attribut`.

## Exercice 2

### R3 - Anna Ushmarina
Pour l'Exercice 2, j'ai pris le rôle 3 (r3) sur ma propre branche. Ma mission : gérer la sauvegarde et le chargement de notre corpus d'articles au format Pickle, puis préparer le script pour la fusion avec le reste de l'équipe.

**Difficultés rencontrée**
1. Contrairement aux formats texte classiques (comme le JSON ou le XML), Pickle sérialise les objets en binaire. Il fallait donc s'assurer de manipuler les fichiers correctement pour ne pas corrompre les données.

**Solutions**
1. J'ai codé save_pickle (wb avec pickle.dump) et load_pickle (rb avec pickle.load) en m'assurant de bien gérer l'ouverture des fichiers en mode binaire.

## Exercice 3

###R3 - Anna Ushmarina

J'ai dû relire le code de r1. Dans l'ensemble, le script était bon ; j'ai restructuré un peu la fonction `load_xml` pour placer la partie `except` après le reste du code afin de faciliter la lisibilité et la fonctionnalité. Tag ajouté.