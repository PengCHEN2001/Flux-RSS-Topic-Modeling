# Goupe16 : Salma, Catalina, Lydia

Récuperation  du code du groupe précedent.
le script ne fonctionnait pas, il y a eu plusieurs corrections qui ont ete entrpris.


## Corection_s8: 
Rss_reader : il a ete modifié de sorte à ce que l'utilisateur saisisse un fichier et non pas une arborescence. 
Et dans le def  main nous avons retirer les autres args.parse car cela ne nous interesse pas pour le moment .
Rss_parcours nous avons modifier 'sample ' en corpus afin que ce soit plus comprehensible , et nous avons modifier cet argument afin qu'il soit optionnel, comme ca l'utilisateur a le choix entre saisir un dossier ou directement un inputfil qui contient le chemin vers un fichier.






## R3 Salma :


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



