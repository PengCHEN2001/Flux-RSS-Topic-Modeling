# Objectifs du projet :
> 1. pouvoir lire et manipuler des données fournies au format XML (RSS) 
> 2. pouvoir en extraire le texte à analyser ainsi que les métadonnées qui serviront au filtrage


| Métadonnées à extraire                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - l’identifiant (id) de l’article<br>- la source : le nom du journal, <br>- le titre de l’article<br>- le contenu de l’article<br>- la date de l’article<br>- les catégories auxquelles appartient l’article |


### Exercice 1 Découverte du RSS - traiter un unique fichier

Nous créons tout d'abord le fichier `rss_reader.py` qui servira à lire le fichier xml et qui retournera le texte et les métadonnées des items du flux RSS

Nous répartissons les rôles entre nous, chacune devra se charger de produire de le même résultat avec une méthode différente

| rôle | module                                    | tâche                                     |
| ---- | ----------------------------------------- | ----------------------------------------- |
| r1   | module **re**<br>> expressions régulières | extraire les informations des balises XML |
| r2   | module **etree**<br>> librairie python    | lire, modifier et explorer du XML |
| r3   | module **feedparser**<br>> environnement virtuel | lire et décoder des flux RSS|
- chacune de ces fonctions renverra une liste de dictionnaires