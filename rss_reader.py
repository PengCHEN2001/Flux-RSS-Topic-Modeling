"""
1ère méthode : module re - expressions régulières
Ce script lit un flux RSS en XML et extrait les articles sous forme de dictionnaires.
"""

import re
import os

def read_file(file_path):
    """Lit le contenu du fichier XML et le retourne sous forme de chaîne de caractères."""
    # On ouvre le fichier en mode lecture avec l'encodage UTF-8
    with open(file_path, "r", encoding="utf-8") as f:
        # On renvoie tout le contenu du fichier
        return f.read()

def clean_cdata(text):
    """Supprime les balises CDATA si présentes."""
    # Certaines balises XML contiennent <![CDATA[ ... ]]> pour protéger le texte
    # On enlève ces balises pour ne garder que le contenu
    if text:
        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
    return text

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
        return clean_cdata(match.group(1)).strip()
    
    # Si la balise n'existe pas, on retourne une chaîne vide
    return ""

def extract_items(xml_content, source_name):
    """Extrait les articles du flux RSS et retourne une liste de dictionnaires."""
    # On récupère tous les blocs <item>...</item>
    # Le namespace éventuel est aussi accepté
    items = re.findall(r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>", xml_content, re.DOTALL)

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

        # catégories : il peut y en avoir plusieurs
        categories = re.findall(
            r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>",
            item,
            re.DOTALL
        )
        # On nettoie chaque catégorie
        article["categories"] = [clean_cdata(c).strip() for c in categories]

        # On ajoute l’article à la liste finale
        metadonnees.append(article)

    return metadonnees

def main():
    # Chemin vers le fichier XML de test
    file_path = "./test.xml"
    
    # On récupère uniquement le nom du fichier (sans le chemin)
    source_name = os.path.basename(file_path)

    # Lecture du contenu XML
    xml_content = read_file(file_path)

    # Extraction des articles
    articles = extract_items(xml_content, source_name)

    # Affichage du nombre d’articles trouvés
    print(f"Nombre d'articles trouvés : {len(articles)}\n")

    # Affichage des métadonnées de chaque article
    for art in articles:
        print("ID :", art["id"])
        print("Source :", art["source"])
        print("Titre :", art["title"])
        print("Date :", art["date"])
        print("Contenu :", art["content"])
        print("Catégories :", art["categories"])
        print("-" * 60)

# Point d’entrée du programme
if __name__ == "__main__":
    main()