"""
1ère méthode : module re - expressions régulières
"""

import re
import os

def read_file(file_path):
    """Lit le contenu du fichier XML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_cdata(text):
    """Supprime les balises CDATA si présentes."""
    if text:
        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
    return text

def extract_tag(content, tag):
    """Extrait le contenu d’une balise simple."""
    # On accepte les namespaces éventuels dans le tag
    pattern = rf"<(?:\w+:)?{tag}[^>]*>(.*?)</(?:\w+:)?{tag}>"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return clean_cdata(match.group(1)).strip()
    return ""

def extract_items(xml_content, source_name):
    """Extrait les articles du flux RSS et retourne une liste de dictionnaires."""
    # On accepte les namespaces éventuels dans <item>
    items = re.findall(r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>", xml_content, re.DOTALL)

    metadonnees = []

    for item in items:
        article = {}

        # id (on prend le guid ou le lien selon les articles)
        guid = extract_tag(item, "guid")
        link = extract_tag(item, "link")
        article["id"] = guid if guid else link

        # source (nom du fichier)
        article["source"] = source_name

        # titre
        article["title"] = extract_tag(item, "title")

        # contenu
        article["content"] = extract_tag(item, "description")

        # date
        article["date"] = extract_tag(item, "pubDate")

        # catégories (peut y en avoir plusieurs)
        categories = re.findall(r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>", item, re.DOTALL)
        article["categories"] = [clean_cdata(c).strip() for c in categories]

        metadonnees.append(article)

    return metadonnees

def main():
    # Chemin vers le fichier XML de test
    file_path = "./test.html"
    source_name = os.path.basename(file_path)

    xml_content = read_file(file_path)

    articles = extract_items(xml_content, source_name)

    print(f"Nombre d'articles trouvés : {len(articles)}\n")
    for art in articles:
        print("ID :", art["id"])
        print("Source :", art["source"])
        print("Titre :", art["title"])
        print("Date :", art["date"])
        print("Contenu :", art["content"])
        print("Catégories :", art["categories"])
        print("-" * 60)

if __name__ == "__main__":
    main()
