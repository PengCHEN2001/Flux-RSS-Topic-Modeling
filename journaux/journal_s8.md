# Corrections apportées aux scripts 

Nous avons créé une branche correction-s8 à partir de main pour y effectuer nos modifications.

1. Alignement du type **Article** dans tout la pipeline

Le problème ce que une partie du code retournait des dictionnaires, alors que le reste du script manipulait des objets **Article** avec accès par attribut : 
```
a.id
a.source
a.date
a.categories
```
Cela provocait des erreurs ``` AttributeError: 'dict' object has no attribute 'id' ```

> Nous avons donc uniformisé le comportement des fonctions de lecture pour qu'elles retournent toutes des objets Article.

2. Correction du champs de la dataclass : **content** au lieu de **description**

Le problème était que dans datastrcutures.py, le dataclass etait définie :
```
@dataclass
class Article:
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str]
```

Mais une partie du code construisait les objets avec : ``` Article(..., description=...) ```

> Nous avons donc remplacé partout description= par content=

3. Réparation du module_etree

Le problème dans ce fichier, était que plusieurs variables utilisées dans la création de l'artcile n'étaient jamais définies : 
- dataid
- title
- pubdate

Le code ne pouvait donc pas s’exécuter.

> Nous avons ajouté la récupération de ces valeurs : 
```
dataid = get_text(item, "guid") or get_text(item, "link")
title = get_text(item, "title")
pubdate = get_text(item, "pubDate")
if not pubdate:
    pubdate = get_text(item, "lastpublished")
```

4. Adaptaction des focntions de filtrage aux objets Article et correction de l'affichage final

Le problème portait sir les fonstions de filtrage qui manipulaient les articles comme des dictionnaires.

> Nous avons remplacé ces accès par des attributs : 
```
article.source
article.id
article.categories
item.date
```

Ensuite nous avons remplacé : for key, value in article.items() par un affichage explicite des attributs : 

```
print(f"id: {article.id}")
print(f"source: {article.source}")
print(f"title: {article.title}")
print(f"content: {article.content}")
print(f"date: {article.date}")
print(f"categories: {article.categories}")
```

5. Corection_s8: 

Rss_reader : il a ete modifié de sorte à ce que l'utilisateur saisisse un fichier et non pas une arborescence. 
Et dans le def  main nous avons retirer les autres args.parse car cela ne nous interesse pas pour le moment .
Rss_parcours nous avons modifier 'sample ' en corpus afin que ce soit plus comprehensible , et nous avons modifier cet argument afin qu'il soit optionnel, comme ca l'utilisateur a le choix entre saisir un dossier ou directement un inputfil qui contient le chemin vers un fichier.


## s8 - Enrichissements du corpus avec des analyseurs morphosyntaxiques. 



> Spacy 

## Exercice 1 — Prise en main des outils

Pour ce projet, j'ai travaillé avec **spaCy**.

## Exercice 2 — Script de démonstration indépendant

En m'inspirant de la documentation, j'ai rédigé le script `demo_spacy.py`. Ce script charge la bibliothèque et traite une phrase issue du corpus à l'aide du modèle français `fr_core_news_md`.

Comme demandé dans l'exercice suivant, ce script m'a permis de me familiariser avec les principales fonctionnalités de l'outil : la tokenisation du texte, ainsi que l'affichage, pour chaque mot, de son lemme, de sa forme et de sa catégorie morphosyntaxique (*POS*).

## Exercice 3 — Intégration au projet

Dans cet exercice, la principale difficulté a d'abord été de déterminer la bonne stratégie d'intégration. La consigne « retourne enrichi » m'a posé problème. J'ai hésité entre deux approches :

- ajouter un champ `tokens: list[Token]` à la dataclass `Article` ;
- créer une dataclass `Token` distincte, avec un champ `id` permettant de la relier à l'article.

J'ai finalement retenu la première solution.

### Étapes réalisées

- Création d'une dataclass `Token` pour stocker les analyses associées à chaque token.
- Ajout, dans `Article`, du champ `tokens: list[Token] = field(default_factory=list)`.
- Création d'une fonction `article_analyzer` dans `datastructures.py` :
  - chargement d'un modèle **spaCy** ;
  - application du modèle à la description de l'article ;
  - parcours des tokens pour stocker les résultats de l'analyse dans des objets `Token`.
- Création du fichier `analyzers.py` :
  - import des fonctions définies dans `datastructures.py` ;
  - définition de la fonction `analyze_corpus`, qui parcourt le corpus et applique `article_analyzer` à chaque article ;
  - ajout d'une fonction principale (`main`).
- Désérialisation des `Article`, enrichissement des données, puis sérialisation.
- Ajout d'un `return` dans la fonction de désérialisation, car lors de l'utilisation dans `analyzers.py`, la variable `corpus` valait `None`.

### Exemple de ligne de commande

```bash
python3 analyzers.py --from-format pickle corpus.pkl corpus.pkl
```


> Stanza
#  Lydia (Rôle 2 : Stanza)

## 1. 

###  Développement de l'analyseur Stanza
* **Objectif** : Enrichir le texte brut avec des informations morphosyntaxiques.
* **Réalisation** : Création de `analyzers.py` intégrant le pipeline `stanza.Pipeline(lang='fr', processors='tokenize,lemma,pos')`.
* **Résultat** : Chaque article contient désormais une liste de `tokens` avec sa forme, son lemme et son étiquette UPOS.

###  Harmonisation et préparation du Merge
* **Objectif** : Rendre le code compatible avec celui des autres membres du groupe (SpaCy/Trankit).
* **Actions** : 
    * Changement des noms de variables de l'anglais (`form`, `lemma`) vers le français (`forme`, `lemme`) pour s'aligner sur la structure de groupe.
    * Correction des erreurs de configuration liées au renommage (conservation de `processor='lemma'` pour Stanza en interne).

## 2. Rapport de Relecture (Peer-Review) de la branche SpaCy

J'ai effectué la relecture de l'analyseur SpaCy. Voici les modifications et observations effectuées pour valider la branche :

* **Correction du bug `token.shape_`** : L'analyseur SpaCy utilisait initialement `shape_` (qui donne la structure abstraite du mot, ex: `Xxxx`). J'ai effectué la modification vers `token.text` pour récupérer le vrai mot.
* **Mise en conformité des Dataclasses** : j'ai harmoniser  harmonisé les champs de la classe `Token` dans ma partie stanza  pour éviter les conflits lors de la fusion sur `main`.
* **Validation** : Après ces corrections, le fichier de sortie de SpaCy est identique en structure à celui de Stanza, ce qui permet un traitement uniforme par la suite.

## 3. Commandes pour tester le projet
Utiliser des guillemets pour les chemins avec espaces 
**Note technique** : Stanza est extrêmement précis pour le français mais très gourmand en ressources. Pour les prochains traitements à grande échelle, il est recommandé de vérifier la disponibilité d'un GPU (`use_gpu=True`) ou de segmenter le corpus en fichiers de 500 articles maximum pour éviter les saturations mémoire. ici j'ai utiliser un seul fichier comme demander dans la feuille d'exercice 

   python3 rss_parcours.py -c "../2026/02/10/mar.10:26/Blast -- articles.xml" --output-file corpus_pour_stanza.json --output-format json

pour lancer l'analyse stanza :
   python3 analyzers.py corpus_pour_stanza.json corpus_final.json --format json



> trankit 

R3 Salma :


type de commande lancé pour tester les script : 
reader : 
'''
 python3 rss_reader.py -r  etree   ~/RSS_doc/2026/02/10/mar.10\:26/Flux\ RSS\ -\ BFM\ BUSINESS\ -\ Consommation.xml
'''

parcours: 
'''
 python3 rss_parcours.py -w glob -m etree -c ~/RSS_doc   --output-file ~/test1.pckl --output-format pickle
 python3 rss_parcours.py -w glob -m feedparser -c ~/RSS_doc   --output-file ~/test1.xml  --output-format xml
'''

Trankit : 

issues rencontrés : 
J'ai rencontré un probleme concernant l'environement vituel.
mais j'ai eu ce message ' This environment is externally managed' cela suggèrait que l'environement pointait vers le systeme et pas vers le venv.
La solution a ete d'Utiliser python -m pip install python-dateutil pour forcer le pip lié au python du venv.
J'ai eu un autre message d'erreur indiquant que le pip n'etait pas installé dans l'environement, donc j'ai Recréer le venv avec --clear : python3 -m venv venv --clear puis réactiver.
Puis lorsque j'ai voulu re tester les script j'ai eu un message indiquant que feedparser etait manquant donc j'ai ' pip install feedparser' .
La version python 3.13 n'etait pas adapté aux outils trankit j'ai du suprime et reinstaller une autre version de python 3.10. 
la solution :Utiliser uv pour créer un venv Python 3.10 et installer la version modifiée du prof : uv venv venv310 --python 3.10 puis uv pip install https://github.com/pmagistry/trankit.git

Mais il etait Impossible de trouver le paquet python3.10 ( La distribution (Ubuntu Plucky / 25.04) ne propose que Python 3.13 dans ses dépôts officiels.).
Solution peu conventionnel : Installer uv (pip install uv --break-system-packages) qui télécharge et gère Python 3.10 automatiquement.

Puis lorsque j'ai créer le dataclass token : j'ai eu ce message d'erreur : NameError / TypeError : token['text'] utilisé comme type
Car Dans une dataclass Python, après : on met un type (str, int…), pas une expression. token['text'] tente d'indexer une variable inexistante.
Donc j'ai déclarer le type str et utiliser token.get('text') uniquement dans la fonction d'analyse.


Puis lorsque j'ai lance la commande : 

'''
python analyzer.py ~/test_small.json ~/corpus_analyzed_small.json --from-format json --to-format json
'''
J'ai eu ce message d'erreur :  AttributeError: 'Article' object has no attribute 'tokens'
Le champ tokens n'avait pas été ajouté à la dataclass Article dans datastructures.py.
J'ai donc ajouté tokens: list = field(default_factory=list) à la dataclass Article.

J'ai eu un autre :  KeyError: 'lemma'
Trankit ne renvoie pas toujours toutes les clés (lemma, upos…) selon le token analysé (ponctuation, tokens spéciaux…)
La solution a ete de remplacer token['lemma'] par token.get('lemma') ou de retourner None si la clé est absente.


J'ai egalement eu du mal lors du chargement du corpus avec trankit car cela prenait beaucoup de temps.
j'ai fait un test avec 10 articles selectionné que j'avais precedement de serialisé en format json en lancant la commande rss parcours.
Puis j'ai relance la commande a partir du fichier test_small.json et le resultat est stocke dans un fichier 'corpus_analyzed_small.json'



