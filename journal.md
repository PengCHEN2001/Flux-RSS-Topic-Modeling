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




### Rôle 2 : HO






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








