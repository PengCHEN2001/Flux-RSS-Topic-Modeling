import xml.etree.ElementTree as ET
import os
import re
import argparse

#Récupère le texte d'une balise.Retourne une chaîne vide si la balise est absente.
def get_text(parent, tag):
    elem = parent.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""

#Traite UN fichier RSS XML Retourne une liste de dictionnaires (articles)
    
def module_etree(chemin_fichier):   
    articles = []

    try:
        tree = ET.parse(chemin_fichier)
    except ET.ParseError:
        print(f"Fichier XML invalide : {chemin_fichier}")
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


def main(chemin_fichier):
    articles = module_etree(chemin_fichier)

    print("Nombre total d'articles :", len(articles))

    for i, article in enumerate(articles, start=1):
        print(f"\nARTICLE {i}")
        print("-" * 40)
        for cle, valeur in article.items():
            print(f"{cle} : {valeur}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extraction des métadonnées d'un flux RSS"
    )
    parser.add_argument(
        "fichier_xml",
        help="Chemin vers le fichier XML RSS"
    )

    args = parser.parse_args()

    main(args.fichier_xml)

