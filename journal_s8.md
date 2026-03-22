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


> Stanza


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



