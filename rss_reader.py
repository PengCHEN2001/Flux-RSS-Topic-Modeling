<<<<<<< rss_reader.py
"""
1ère méthode : module re - expressions régulières
Ce script lit un flux RSS en XML et extrait les articles sous forme de dictionnaires.
"""

import re
from pathlib import Path
import argparse

def read_file(file_path):
    """Lit le contenu du fichier XML et le retourne sous forme de chaîne de caractères."""
    # On ouvre le fichier en mode lecture avec l'encodage UTF-8
    with open(file_path, "r", encoding="utf-8") as f:
        # On renvoie tout le contenu du fichier
        return f.read()

def clean_cdata(text):
    """Supprime les balises CDATA si présentes et les balises."""
    # Certaines balises XML contiennent <![CDATA[ ... ]]> pour protéger le texte
    # On enlève ces balises pour ne garder que le contenu
    if text:
        #Supprimer le CDATA : 
        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
        #Supprimer les balises (dans la description) :
        text = re.sub(r"<[^>]+>", "", text, flags=re.DOTALL)
        #Pour les caractères accentuées et éviter les problèmes d'encodages comme "&#xE9;" pour le "é". Utiliser le module HTML : 
        text = re.sub(
            r"&#x([0-9A-Za-z]+);",
            lambda m : chr(int(m.group(1), 16)), #Créer une variable aléatoire "m" qui servira à traduire correctement le caractère qui pose problème, exemple "é" qui est traduit par &#xE9.
            text
            )
        text = re.sub(
            r"&#(\d+);",
            lambda m : chr(int(m.group(1))),
            text
            )
         
        if not text : 
            return ""
        return text.strip()

def extract_tag(content, tag):
    """Extrait le contenu d’une balise simple."""
    # On construit une expression régulière qui accepte :
    # - <tag>...</tag>
    # - <ns:tag>...</ns:tag> (avec namespace éventuel)
    pattern = rf"<(?:\w+:)?{tag}[^>]*>(.*?)</(?:\w+:)?{tag}>"
    
    # On cherche la première occurrence de cette balise
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # On nettoie les CDATA et on supprime les espaces en début et fin
        texte = clean_cdata(match.group(1))
        if tag == "description" : 
            texte = clean_cdata(texte)
        return texte
    # Si la balise n'existe pas, on retourne une chaîne vide
    return ""

def extract_items(xml_content, source_name):
    """Extrait les articles du flux RSS et retourne une liste de dictionnaires."""
    
    #Extraire les catégories dans channel : 
    all_channels = re.findall(
        r"<(?:\w+:)?channel\b[^>]*>(.*?)</(?:\w+:)?channel>", #Chercher toutes les channels (s'il y en a plusieurs).
        xml_content,
        re.DOTALL
        )
    channel_content = all_channels[0] if all_channels else "" 
    channel_propre = re.sub(
        r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
        "",
        channel_content,
        flags=re.DOTALL
        ) 
    channel_categories = re.findall(
        r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>", #Trouver les catégories dans channel.
        channel_propre,
        re.DOTALL
        )       
    channel_categories = [clean_cdata(categ.strip()) for categ in channel_categories]

    # On récupère tous les blocs <item>...</item>
    # Le namespace éventuel est aussi accepté
    items = re.findall(
        r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
        xml_content,
        re.DOTALL
        )
   
    # Liste qui contiendra les métadonnées de chaque article
    metadonnees = []

    # On traite chaque article séparément
    for item in items:
        article = {}

        # id : on prend le guid s’il existe, sinon le lien
        guid = extract_tag(item, "guid")
        link = extract_tag(item, "link")
        article["id"] = guid if guid else link

        # source : nom du fichier XML
        article["source"] = source_name

        # titre de l’article
        article["title"] = extract_tag(item, "title")

        # contenu (description du RSS)
        article["content"] = extract_tag(item, "description")

        # date de publication
        article["date"] = extract_tag(item, "pubDate")
        
        #Extraire les catégories dans items : 
        item_categories = re.findall(
            r"<(?:\w+:)?(?:category)\b[^>]*>(.*?)</(?:\w+:)?(?:category)>",
            item,
            re.DOTALL
            )
        item_categories = [clean_cdata(categ.strip()) for categ in item_categories]        
        
        article["categories"] = sorted(channel_categories + item_categories)
        
        # On ajoute l’article à la liste finale
        metadonnees.append(article)

    return metadonnees


def main():
    #Module argparse :
    parser = argparse.ArgumentParser(description = "Extraire un ou des articles")
    parser.add_argument("fichier_xml", help = "Chemin vers le fichier xml")
    args = parser.parse_args()
    file_path = args.fichier_xml
    
    # On récupère uniquement le nom du fichier (sans le chemin)
    source_name = Path(file_path).name
    
    # Lecture du contenu XML
    xml_content = read_file(file_path)

    # Extraction des articles
    articles = extract_items(xml_content, source_name)

    # Affichage du nombre d’articles trouvés
    print(f"Nombre d'articles trouvés : {len(articles)}\n")

    # Affichage des métadonnées de chaque article
    for art in articles:
        print("id :", art["id"])
        print("source :", art["source"])
        print("title :", art["title"])
        print("description :", art["content"])
        print("date :", art["date"])
        print("categories :", art["categories"])
        print("-" * 60)

# Point d’entrée du programme
if __name__ == "__main__":
    main()

    
##########RELECTURE PAR R3 : 
#Problème 1 :
#Dans la fonction "def main()", la variable "file_path" contient un nom de fichier appelé "test.xml". Donc le script se lancera si ce script python est dans le même dossier où se trouve le fichier nommé "test.xml".
#Pour lancer le script, il faut utiliser la commande suivante : python3 rss_feedparser.py
#J’utilise le module argparse pour utiliser la commande sur le terminal (faire le lien entre bash et python). 
#Je modifie aussi la variable "file_path" : je remplace "./test.xml" par "args.fichier_xml".
#AVANT : 
#    def main():
#        # Chemin vers le fichier XML de test
#        file_path = "./test.xml"
#CORRIGE (APRES) : avec le module argparse et le script (voir le script ajouté dans la fonction "def main()".)
#Problème 2 : 
#Les catégories n’apparaissent pas touts dans les fichiers xml comme les fichiers “Flux RSS” et “Figaro".
#AVANT : 
#def extract_items(xml_content, source_name):
#   """Extrait les articles du flux RSS et retourne une liste de dictionnaires."""
#  # On récupère tous les blocs <item>...</item>
#  # Le namespace éventuel est aussi accepté
#    items = re.findall(r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>", xml_content, re.DOTALL)
#...
# catégories : il peut y en avoir plusieurs
#       categories = re.findall(
#           r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>",
#           item,
#           re.DOTALL
#       )
#       # On nettoie chaque catégorie
#       article["categories"] = [clean_cdata(c).strip() for c in categories]
#APRES :
# #Extraire les catégories dans channel : 
# all_channels = re.findall(
#     r"<(?:\w+:)?channel\b[^>]*>(.*?)</(?:\w+:)?channel>", #Chercher toutes les channels (s'il y en a plusieurs).
#     xml_content,
#     re.DOTALL
#     )
# channel_content = all_channels[0] if all_channels else "" 
# channel_propre = re.sub(
#     r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
#     "",
#     channel_content,
#     flags=re.DOTALL
#     ) 
# channel_categories = re.findall(
#     r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>", #Trouver les catégories dans channel.
#     channel_propre,
#     re.DOTALL
#     )       
# channel_categories = [clean_cdata(categ.strip()) for categ in channel_categories]
#
# # On récupère tous les blocs <item>...</item>
# # Le namespace éventuel est aussi accepté
# items = re.findall(
#     r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
#     xml_content,
#     re.DOTALL
#     )
# article["categories"] = sorted(channel_categories + item_categories)
#Problème 3 : 
#Il ya encore des balises dans certains contenu appartenant à la description :
#Solution 3 :
#Supprimer les balises manquantes.
#AVANT :
#    def clean_cdata(text):
#    """Supprime les balises CDATA si présentes."""
#    # Certaines balises XML contiennent <![CDATA[ ... ]]> pour protéger le texte
#    # On enlève ces balises pour ne garder que le contenu
#    if text:
#        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
#    return text
#APRES : 
#def clean_cdata(text):
#    """Supprime les balises CDATA si présentes et les balises."""
#    # Certaines balises XML contiennent <![CDATA[ ... ]]> pour protéger le texte
#    # On enlève ces balises pour ne garder que le contenu
#    if text:
#        #Supprimer le CDATA : 
#        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
#        #Supprimer les balises (dans la description) :
#        text = re.sub(r"<[^>]+>", "", text, flags=re.DOTALL)
#        #Pour les caractères accentuées et éviter les problèmes d'encodages comme "&#xE9;" pour le "é". Utiliser le module HTML : 
#        text = re.sub(
#            r"&#x([0-9A-Za-z]+);",
#            lambda m : chr(int(m.group(1), 16)), #Créer une variable aléatoire "m" qui servira à traduire correctement le caractère qui pose problème, exemple "é" qui est traduit par &#xE9.
#            text
#            )
#        text = re.sub(
#            r"&#(\d+);",
#            lambda m : chr(int(m.group(1))),
#            text
#            )
#         
#        if not text : 
#            return ""
#        return text.strip()
#    ...    
#    texte = clean_cdata(match.group(1))
#Problème 4 : 
#On a des lettres qui sont remplacées par des caractères comme : &#xE9; => pour l'accent “é” ou encore “&#039;” pour l’apostrophe “ ‘ “. On peut importer le module HTML ou ne faire qu'avec des regex mais si certains caractères ne sont pas définis dans le script, le programme peut s'arrêter...
#Solution : cf. solution 3.


import xml.etree.ElementTree as ET
import os
import re
import argparse
from pathlib import Path

# Récupère le texte d'une balise. Retourne une chaîne vide si la balise est absente.
def get_text(parent, tag):
    elem = parent.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""

# Traite UN fichier RSS XML Retourne une liste de dictionnaires (articles)
def module_etree(chemin_fichier):
    articles = []

    try:
        tree = ET.parse(chemin_fichier)
    except ET.ParseError:
        return articles

    root = tree.getroot()

    channel = root.find(".//channel")
    if channel is None:
        return articles

    # >>>>> SUGGESTION R1 : la liste de catégories n'est pas triée, on pourrait utiliser sorted() pour avoir un ordre stable
    channel_categories = [
        cat.text.strip()
        for cat in channel.findall("category")
        if cat.text
    ]

    for item in channel.findall("item"):

        raw_content = get_text(item, "description")
        clean_content = re.sub(r"<[^>]+>", "", raw_content)

     # >>>>> SUGGESTION R1 : la liste de catégories n'est pas triée, on pourrait utiliser sorted() pour avoir un ordre stable
        categories = sorted([
            cat.text.strip()
            for cat in item.findall("category")
            if cat.text
        ])

        article = {
            "id": get_text(item, "guid") or get_text(item, "link"),
            "source": os.path.basename(chemin_fichier),
            "title": get_text(item, "title"),
            "content": clean_content,
            "date": get_text(item, "pubDate"),
            "categories": categories,
            "channel_categories": channel_categories
        }

        articles.append(article)

    return articles


def main(dossier):
    tous_les_articles = []
    chemin = Path(dossier)

    # Parcours récursif des fichiers XML
    for fichier in chemin.glob("**/*.xml"):
        print("Trouvé :", fichier)
        articles = module_etree(fichier)
        tous_les_articles.extend(articles)

    print("Nombre total d'articles :", len(tous_les_articles))
    
    for i, article in enumerate(tous_les_articles, start=1):
        print(f"\nARTICLE {i}")
        print("-" * 40)
        for cle, valeur in article.items():
            print(f"{cle} : {valeur}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extraction des métadonnées d'un flux RSS"
    )
    parser.add_argument(
        "dossier",
        help="Chemin vers le dossier contenant les fichiers XML"
    )

    args = parser.parse_args()

    main(args.dossier)
>>>>>>> rss_reader.py
