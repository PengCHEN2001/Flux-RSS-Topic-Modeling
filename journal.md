# Journal de bord : groupe 16

# Objectifs du projet :
> 1. pouvoir lire et manipuler des données fournies au format XML (RSS)
> 2. pouvoir en extraire le texte à analyser ainsi que les métadonnées qui serviront au filtrage


| Métadonnées à extraire                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - l’identifiant (id) de l’article<br>- la source : le nom du journal, <br>- le titre de l’article<br>- le contenu de l’article<br>- la date de l’article<br>- les catégories auxquelles appartient l’article |


### Exercice 1 Découverte du RSS - traiter un unique fichier

**Branche créée :** `r1-FA`

**Branche créée :** `r2-HO`

**Branche créée :** `r3-HY` , *Tag* :  HY-s3e1r3-fin

Nous créons tout d'abord le fichier `rss_reader.py` qui servira à lire le fichier xml et qui retournera le texte et les métadonnées des items du flux RSS

Nous répartissons les rôles entre nous, chacune devra se charger de produire de le même résultat avec une méthode différente

| rôle | module                                    | tâche                                     |
| ---- | ----------------------------------------- | ----------------------------------------- |
| r1   | module **re**<br>> expressions régulières | extraire les informations des balises XML |
| r2   | module **etree**<br>> librairie python    | lire, modifier et explorer du XML |
| r3   | module **feedparser**<br>> environnement virtuel | lire et décoder des flux RSS|
Chacune de ces fonctions renverra une liste de dictionnaires


### Rôle 1 : FA

doc : https://docs.python.org/3/library/re.html / https://stackoverflow.com/questions/10250381/extracting-from-xml-using-regex / https://flapenguin.me/xml-regex

L’objectif de cette partie était d’extraire automatiquement les métadonnées d’un flux RSS au format XML (articles, titre, date, catégories, etc.) en utilisant le module `re` de Python, donc en s’appuyant uniquement sur des **expressions régulières**.

L’idée était de :
- Lire un fichier XML
- Identifier les balises `<item>`
- Extraire les informations importantes
- Structurer les résultats sous forme de dictionnaires

###### Etape 1 - lecture du fichier XML
J’ai commencé par écrire une fonction `read_file()` qui ouvre le fichier en UTF-8 et retourne son contenu sous forme de chaîne de caractères

```python
with open(file_path, "r", encoding="utf-8") as f:
    return f.read()
```

###### Etape 2 : Extraction des balises "item"
J’ai utilisé `re.findall()` pour récupérer tous les blocs `<item>...</item>`

```python
items = re.findall(r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>", xml_content, re.DOTALL)

```

- `(?:\w+:)?` → permet de gérer les namespaces (ex: `<media:item>`)
- `\b` → évite de capturer des mots comme `<itemized>`
- `[^>]*` → autorise des attributs dans la balise
- `(.*?)` → capture le contenu interne
- `re.DOTALL` → permet au `.` de capturer aussi les retours à la ligne

###### Etape 3 : Extraction des balises internes (title, link, pubDate…)

J’ai créé une fonction générique `extract_tag(content, tag)` pour éviter la répétition de code

```python
pattern = rf"<(?:\w+:)?{tag}[^>]*>(.*?)</(?:\w+:)?{tag}>"

```

J’ai opté pour créer une fonction générique d’extraction de balises afin d’éviter de réécrire une `re` différente pour chaque champ, de centraliser toute la logique d’extraction dans un seul endroit du code et rendre le programme plus clair, plus modulaire et plus facile à modifier ou à étendre par la suite

Le plus dur a été de gérer les cas où certaines balises sont absentes, comme le `guid` dans certains articles, ce qui nécessitait de prévoir des valeurs de remplacement et de nettoyer correctement les balises `CDATA` pour ne conserver que le texte utile

###### Etape 4 : gestion des CDATA

Les flux RSS contiennent parfois : 
```python
<![CDATA[ Contenu de l’article ]]>
```

- solution -> utiliser `re.sub()` pour supprimer ces marqueurs
###### Etape 5 : structure des données
Chaque article est stocké dans un dictionnaire :

```python
article = {
    "id": ...,
    "source": ...,
    "title": ...,
    "content": ...,
    "date": ...,
    "categories": [...]
}
```

- format JSON -> facilement exploitable, structure claire

###### Limite de la méthode des `re` et conclusion

Utiliser des **expressions régulières** pour parser du XML, est une méthode assez fragile. Elle fonctionne tant que la structure du flux RSS est simple et régulière, mais au moindre changement dans l’ordre des balises, leur format ou la présence ou non d’attributs supplémentaires, les expressions régulières peuvent ne plus correspondre. Le code devient alors très dépendant d’un format précis et perd en souplesse. J’ai aussi constaté que dès que le XML devient un peu plus complexe, avec des balises imbriquées ou des namespaces différents, les regex deviennent longues, difficiles à lire et compliquées à maintenir.

Cette approche est peu robuste face aux erreurs de format. Si une balise est mal fermée ou si le contenu contient des caractères inattendus, les `re` peuvent échouer ou retourner des résultats incorrects sans signaler clairement l’erreur. Enfin, comme tout le fichier est traité en une seule fois, cette méthode n’est pas idéale pour des fichiers volumineux ou pour un grand nombre de flux RSS.


### Rôle 2 : HO
##Exercice 1
Dans cet exercice, j’étais en charge de l’implémentation de la méthode utilisant le module xml.etree.ElementTree (r2). L’objectif était d’écrire une fonction capable de lire un flux RSS XML et d’en extraire les métadonnées des items sous forme d’une liste de dictionnaires. 
1. Compréhension initiale et première difficulté : le corpus
Au début, une confusion est apparue concernant les fichiers fournis. Un premier dossier contenait des fichiers .txt qui semblaient correspondre au corpus RSS. J’ai tenté de les analyser avec ElementTree, ce qui a provoqué des erreurs de type :
xml.etree.ElementTree.ParseError: syntax error
Après vérification, il s’est avéré que ces fichiers .txt correspondaient en réalité à des sorties d’exemple (formatées en texte) et non à des flux RSS XML bruts. Ils ne pouvaient donc pas être parsés avec ET.parse().
La solution a consisté à identifier le bon dossier contenant de véritables fichiers .xml représentant les flux RSS bruts. Une fois ces fichiers utilisés, le parsing a fonctionné correctement.

2. Gestion des erreurs XML
Certains fichiers XML présents dans le dossier étaient invalides (fichiers mal formés, tronqués ou ne contenant pas un vrai flux RSS). Sans gestion d’erreur, le script s’arrêtait dès le premier fichier invalide.
Pour rendre le script robuste, un bloc try/except a été ajouté :

try:
    tree = ET.parse(chemin_fichier)
except ET.ParseError:
    print(f"Fichier XML invalide : {chemin_fichier}")
    return articles
    
Cela permet :
    • d’ignorer les fichiers invalides,
    • de continuer le traitement des autres fichiers,
    • d’éviter l’arrêt brutal du programme.
    
3. Nettoyage du contenu HTML
Le champ description contenait des balises HTML (<br/>, <img>, etc.), ce qui rendait l’affichage peu lisible.
Pour améliorer la lisibilité, un nettoyage simple a été ajouté à l’aide du module re :
clean_content = re.sub(r"<[^>]+>", "", raw_content)
Un oubli d’import du module re a provoqué une erreur :
NameError: name 're' is not defined
La solution a été d’ajouter :
import re
en haut du fichier.

4. Problème de portabilité (chemin absolu)
Au départ, le chemin du fichier XML était codé en dur :
dossier = "/home/hulya/Téléchargements/..."
Ce choix rendait le script inutilisable sur les autres machines du groupe.
Pour rendre le script portable, le chemin a été passé en argument via argparse :
parser = argparse.ArgumentParser(...)
parser.add_argument("fichier_xml", help="Chemin vers le fichier XML RSS")
args = parser.parse_args()
main(args.fichier_xml)
Le script se lance désormais ainsi :
python3 rss_reader.py chemin/vers/fichier.xml
Cela garantit :
    • l’absence de chemin personnel,
    • la compatibilité sur tous les postes,
    • un lancement propre depuis le terminal.
    
5. Affichage et volume des données
Lors des tests sur un dossier complet, le nombre d’articles extraits dépassait 4000. L’affichage intégral rendait la sortie illisible.
Un affichage structuré a été conservé pour un seul fichier XML, avec :
    • le nombre total d’articles,
    • l’affichage détaillé des métadonnées.
    
Cela permet de vérifier le bon fonctionnement sans saturer le terminal.
6. Problème de version non poussée
Une difficulté importante a été rencontrée lors du travail sur les branches : une version intermédiaire du script (avant relecture) n’a pas été poussée sur le dépôt. Après modifications locales, certaines corrections n’étaient pas visibles sur le dépôt distant.
Cela a entraîné :
    • un décalage entre la version locale et la version sur GitLab,
    • une confusion lors des tests et de la relecture.
La situation a été corrigée en :
    • vérifiant la branche active,
    • contrôlant l’état avec git status,
    • s’assurant que les commits étaient bien réalisés,
    • poussant explicitement la branch

Voici la version du script que je n’ai finalement pas pu pousser sur le dépôt. Il s’agissait de ma version initiale, avant les remarques et corrections de ma camarade. Cette première version fonctionnait en local, mais elle ne respectait pas complètement la consigne.

import xml.etree.ElementTree as ET
import os
import re
import argparse

def get_text(parent, tag):
    elem = parent.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""

def module_etree(chemin_fichier):
    articles = []
    try:
        tree = ET.parse(chemin_fichier)
    except ET.ParseError:
        print(f"Fichier XML invalide ignoré : {chemin_fichier}")
        return articles
    root = tree.getroot()
    channel = root.find(".//channel")
    if channel is None:
        return articles
    for item in channel.findall("item"):
        raw_content = get_text(item, "description")
        clean_content = re.sub(r"<[^>]+>", "", raw_content)
        article = {
            "id": get_text(item, "guid") or get_text(item, "link"),
            "source": os.path.basename(chemin_fichier),
            "title": get_text(item, "title"),
            "content": clean_content,
            "date": get_text(item, "pubDate"),
            "categories": [
                cat.text.strip()
                for cat in item.findall("category")
                if cat.text
            ]
        }
        articles.append(article)
    return articles

def main(dossier):
    tous_les_articles = []
    for nom_fichier in os.listdir(dossier):
        if nom_fichier.endswith(".xml"):
            chemin_fichier = os.path.join(dossier, nom_fichier)
            articles = module_etree(chemin_fichier)
            tous_les_articles.extend(articles)
    print("Nombre total d'articles :", len(tous_les_articles))
    for i, article in enumerate(tous_les_articles, start=1):
        print(f"\nARTICLE {i}")
        print("-" * 40)
        for cle, valeur in article.items():
            print(f"{cle} : {valeur}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extraction des métadonnées de flux RSS"
    )
    parser.add_argument(
        "dossier_xml",
        help="Chemin vers le dossier contenant les fichiers XML"
    )
    args = parser.parse_args()
    main(args.dossier_xml)
    
    
Après échange avec HY, elle m’a conseillé de relire attentivement l’énoncé. Je me suis alors rendu compte que mon script ne traitait pas un seul fichier XML comme demandé, mais parcourait tout un dossier. De plus, le chemin vers les fichiers était codé en dur avec mon chemin personnel (/home/...), ce qui empêchait le script de fonctionner sur d’autres machines.
J’ai donc corrigé ces deux points :
    • le script prend désormais en argument le chemin vers un seul fichier XML, conformément à l’exercice 1 ;
    • le chemin n’est plus dépendant de mon ordinateur, ce qui permet au programme de fonctionner sur n’importe quel poste.

Concernant la relecture de son script, honnêtement je n’avais pas beaucoup d’éléments à ajouter. J’ai testé son programme et il fonctionnait correctement. Nous avons simplement discuté de l’ordre de traitement de certains fichiers : notamment, les fichiers Elucid n’étaient pas positionnés de manière cohérente par rapport aux autres sources. Il s’agissait davantage d’un point d’organisation que d’un problème technique.

J’ai reçu deux remarques sur mon script : le positionnement de la source Elucid n’était pas cohérent par rapport aux autres sources et la catégorie « Selection vidéos » semblait manquer dans l’extraction.
Concernant Elucid, la différence observée concernait son affichage ou son organisation par rapport aux autres flux. Après vérification, le script extrayait correctement les informations présentes dans le fichier XML. Le décalage provenait davantage de la structure spécifique de ce flux que d’une erreur de parsing. Corriger ce point aurait impliqué d’ajouter un traitement particulier pour cette source, ce qui aurait rendu le code moins générique.
Pour la catégorie « Selection vidéos », j’ai constaté qu’elle pouvait apparaître au niveau du channel et non uniquement au niveau des item. L’intégrer systématiquement aurait nécessité de modifier la logique d’extraction des catégories. Toutefois, le script fonctionnait déjà correctement pour les métadonnées principales.
À ce stade, j’ai choisi de ne pas modifier davantage le code. Après plusieurs corrections techniques précédentes, j’ai préféré ne pas introduire de changements supplémentaires qui auraient pu casser un script déjà stable. Mon objectif était de conserver une version fonctionnelle et portable plutôt que d’ajouter des ajustements risquant de fragiliser l’ensemble.



##Exercice 2 : Traiter une arborescence de fichiers (r2)
Pour l’exercice 2, l’objectif était d’adapter le script de l’exercice 1 afin de ne plus traiter un seul fichier RSS, mais l’ensemble des fichiers XML contenus dans une arborescence de dossier. En tant que r2, j’ai choisi d’utiliser le module pathlib avec sa fonction glob(), conformément à la consigne.
Choix technique
J’ai importé Path depuis pathlib et modifié la fonction main() pour qu’elle prenne en argument un dossier au lieu d’un fichier unique. J’ai ensuite utilisé :
chemin = Path(dossier)
for fichier in chemin.glob("**/*.xml"):
Ce choix permet un parcours récursif de tous les fichiers .xml présents dans le dossier et ses sous-dossiers. Pour chaque fichier trouvé, j’appelle la fonction module_etree() déjà définie dans l’exercice 1, puis j’ajoute les articles extraits dans une liste globale tous_les_articles.
Ce choix présente deux avantages :
    • Il réutilise entièrement la logique de traitement d’un fichier individuel.
    • Il sépare clairement la lecture de l’arborescence (niveau dossier) et l’extraction XML (niveau fichier).
Problèmes rencontrés

1. Confusion entre fichier unique et dossier
Au début, j’avais gardé une logique proche de l’exercice 1, ce qui posait problème car le script attendait un fichier XML et non un dossier. Il a donc fallu modifier l’argument argparse pour accepter un dossier, et adapter la signature de main().

2. Chemins dépendants de ma machine
Dans une version intermédiaire, j’utilisais des chemins absolus vers mon dossier personnel. Cela rendait le script inutilisable sur les machines des autres membres du groupe. J’ai corrigé ce point en utilisant uniquement l’argument fourni en ligne de commande :
python3 rss_reader.py /chemin/vers/dossier
Cela rend le script portable et indépendant de mon environnement local.

3. Fichiers XML invalides
Certains fichiers du corpus provoquaient des erreurs ET.ParseError. Pour éviter que tout le programme s’arrête à cause d’un seul fichier mal formé, j’ai conservé un bloc try/except dans module_etree(). En cas d’erreur, le fichier est simplement ignoré et la liste vide est retournée.
Cela permet au script de continuer à traiter le reste de l’arborescence sans interruption.

4. Vérification du parcours
Pour vérifier que le parcours fonctionnait réellement, j’ai temporairement ajouté :
print("Trouvé :", fichier)
Cela m’a permis de confirmer que les fichiers étaient bien détectés récursivement et que le problème ne venait pas du glob.
Résultat final
Le script :
    • Parcourt récursivement tous les fichiers .xml d’un dossier.
    • Applique la fonction d’extraction à chacun.
    • Agrège tous les articles dans une seule liste.
    • Affiche le nombre total d’articles et leur contenu structuré.
Le découpage en deux niveaux (lecture arborescence / extraction XML) rend le code plus modulaire et cohérent avec l’architecture demandée.
Difficultés principales
La principale difficulté n’a pas été technique mais structurelle : comprendre comment adapter proprement un script conçu pour un seul fichier vers un traitement global, sans casser la logique précédente.
Il a fallu :
    • Modifier l’interface du programme (argparse),
    • Repenser la fonction main(),
    • Tester progressivement pour éviter les erreurs silencieuses.


..........................................................

### Rôle 3 : HY
Ex1.2. Création d'un fichier rss_reader.py : foncyion qui lit le fichier xml dont le chemin est donné en argument et qui retourne une liste de dictionnaires qui comporte des métadonnées des items du flux RSS et du texte.

####3ème méthode : avec le module feedparser (rôle 3)

D'après la documentation (cf. https://feedparser.readthedocs.io/en/latest/ , https://pythonhosted.org/feedparser/basic-existence.html#testing-if-elements-are-present ; https://youtu.be/BOfjtZXQmZg?si=cxw_cer2oMxhXFKe ; https://tekipaki.hypotheses.org/628), il faut tester s'il y a bien l'existence ou non des éléments qu'on recherche, ici on cherchera à extraire des métadonnées pour chaque article à partir d'un fichier xml. Dans mon script, j'ajoute "No title" pour indiquer que le "title" est absent dans un article :

Extrait du script :

```
...
    articles.append({
        "id" : entry["id", "No id"],
        "source" : fichier_xml,
        "title" : entry["title", "No title"],
...
```
**Problème 1 :** Mais en lançant mon script sur le terminal, j'obtiens un message d'erreur :
```Traceback (most recent call last):
    File /chemin/vers/fichier.py, line xx, in <module>
        "id" : entry["id", "No id"],
        ...
   KeyError: ('id', 'No id')
```

**Solution 1 :** J'ai utilisé "get()" pour récupérer une valeur dans les dictionnaires. Je pense qu'on pouvait également utiliser "if" et "else" en tant que condition pour extraire les informations dans les fichiers xml mais, je ne les ai pas encore testé.

```
...
    ...
        "id" : entry.get["id", "No id"]
        ),
...
```
En lançant le script de nouveau :

**Problème 2 :** J'ai remarqué que "description" fonctionnait pour certains fichiers xml et d'autres fonctionnait avec "summary". J'ai donc ajouté les différents noms pour la même balise, par exemple pour extraire la "description", on peut rechercher dans `description` ou `summary` (cf. Solution 3).

**Problème 3 :** get() ne prend que 2 arguments et pas plus.

**Solution 3 :** J'ai répéter "entry.ge()" pour chaque information recherchée en ajoutant un "or" car je veux soit trouver la "description", soit le "summary" et si on ne trouve aucun des deux, on affichera "No description or summary". Les termes "summary" et "description" sont des noms de balises qui peuvent être utilisés dans les fichiers xml et contiennent du texte (cf. https://feedparser.readthedocs.io/en/latest/ , https://youtu.be/BOfjtZXQmZg?si=Ch9Vmt5NTrYDe5Ty):
```
...
   ...
        "description" : (
            entry.get("description")
            or entry.get("summary")
            or "No description or summary"
        ),
...
```
J'ai relancé le script et ai rencontré plusieurs problèmes :

**Problème 4 :** Le résultat devait retourner les catégories pour les fichiers xml hormi les fichiers "Libération".

**Solution 4 :** Comparer les fichiers entre eux. J'ai pris un fichier de "Libération", de "Blast", d'"Elucid", de "Flux RSS" et de "Figaro". J'ai constaté qu'il y a deux balises "channel" et "item" qui contiennent ou pas des catégories :

- pour "Blast" : il n'y a pas de catégories sauf dans item.
- pour "Elucid" : je n'ai aussi pas de catégories dans channel sauf dans item.
- pour "Libération" : aucune catégories dans channel et item.
- pour "FLux RSS" : on a une catégorie dans channel et elle se répète pour chaque article dans le fichier xml.
- pour "Figaro" : on a des catégories pour item et une catégorie dans channel.

J'ai donc ajouté le script suivant avec des conditions pour extraire les catégories :

*AVANT :*

```
    ...
        "categories" : (
            [tag.get("term") for tag in entry.get("tags", [])]
        )
    ...
```

*APRES :*

```
...
    #Récupération des métadonnées "catégorie(s)" dans les fichiers xml :
        channel_categories = [tag.get("term") for tag in feed.feed.get("tags", [])]
        item_categories = [tag.get("term") for tag in entry.get("tags", [])]

    #Conditions pour l'extraction des catégories et du résultats qu'il retourne (soit une ou plusieurs catégories, soit rien).
        if channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Figaro".
            categories = channel_categories + item_categories
        else :
            if channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Flux RSS".
                categories = channel_categories
            else :
                if not channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Bast" et "ELucid".
                    categories = item_categories
                if not channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Libération".
                    categories = []
...
```

**Problème 5 :** Il faut aussi mettre dans l'ordre les catégories pour les fichiers xml "Figaro" et "Elucid". Pour "Blast", "Flus RSS" et "Libération", c'est correct.

**Solution 5 :** J'ai interchangé "channel_categories" avec "item_categories" :

*AVANT :*

```
...
 if channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Figaro".
            categories = channel_catégories + item_categories
...
```

*APRES :*

```
...
if channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Figaro".
            categories = item_categories + channel_categories
...
```

Ressources utilisées en plus : https://www.geeksforgeeks.org/python/python-if-with-not-operator/

**Problème 6 :** Il y a des balises qui apparaissent dans "description".

**Solution 6 :** Utiliser un module pour supprimer les balises dans les textes. Le module BeautifulSoup :

```
...
   #Pour la description :
        #Nettoyage de la descritpion : condition pour supprimer les balises dans la description de certains fichiers xml afin de ne garder que du texte - Module utilisé "BeautifulSoup" :
        description = (
            entry.get("description")
            or entry.get("summary")
            or "No description or summary"
            )
        if description :
            nettoyer_description = BeautifulSoup(description, "html.parser" )
            description_texte = nettoyer_description.get_text(" ", strip=True)
...
```
et dans la boucle où l’on récupère les métadonnées de chaque article, j'ajoute :  ```"description" : description_texte, ```.

**Autres problèmes rencontrées :** quand je lance le script et donne l’argument "Blast – article.xml" dans le terminal, le script ne fonctionne pas. Il met un message d’erreur :

```
$ python3 rss_reader.py Blast -- articles.xml
usage: rss_reader.py [-h] fichier_xml
rss_reader.py: error: unrecognized arguments: articles.xml

```

**Solution :** Il faut mettre l'argument entre guillemets quand on a des noms de fichiers avec des espaces. Exemple :

```
$ python3 rss_reader.py "Blast -- articles.xml"

```

Ressources en plus :
https://blog.stephane-robert.info/docs/developper/programmation/python/traitement-texte/ ; https://youtu.be/XVv6mJpFOb0?si=-vsrmdDkG7OMrCOZ

***Commandes pour l'utilisateur - lancement du script :***

- 1) Ouvrir un terminal et aller dans un environnement virtuel, exemple : `source venvs/plurital/bin/activate`.
- 2) Installer feedparser sur le terminal avec la commande suivante : `pip install feedparser`
- 3) Pour ouvrir ce script, utiliser cette commande avec ces arguments : `python3 fichier.py chemin/vers/fichier.xml` ou alors `python3 fichier.py fichier.xml`

>Exemple : `python3 rss_feedparser.py "Le Figaro - Vidéos.xml"`

>N.B. : Parfois, certains fichiers peuvent avoir des "espaces", il faut donc les appeller avec des guillemets (sinon, la machine va croire que ce sont des arguments : d'où l'erreur d'affichage `error: unrecognized arguments:`).

- Optionnel : pour voir tous les résulats générés, on peut utiliser la commande suivante : `python3 rss_feedparser.py chemin/vers/fichier_xml > fichier.txt`








