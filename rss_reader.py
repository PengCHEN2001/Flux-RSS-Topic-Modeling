#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# IMPORT

import os.path
from pathlib import Path

import re  # r1
import xml.etree.ElementTree as ET  # r2
import feedparser  # r3
import argparse  # Pour appeler notre fonction.
from bs4 import BeautifulSoup  # Pour nettoyer les balises dans un texte.
import sys

# FONCTIONS
# ----------------Semaines 1 & 2


# Correction ajoutée ultérieurement pour que le script puisse lire un corpus (et non un seul fichier XML)
def walk_os(sample: str) -> list[str]:
    if os.path.isfile(sample):
        if sample.endswith(".xml"):
            return [sample]
        else:
            return []

    files = sorted(os.path.join(sample, file) for file in os.listdir(sample))

    if len(files) == 0:
        return []

    found_files = []
    for file in files:
        if os.path.isfile(file):
            if file.endswith(".xml"):
                found_files.append(file)
        elif os.path.isdir(file):
            found_files.extend(walk_os(file))

    return found_files


def walk_pathlib(sample: str) -> list[str]:
    root = Path(sample)

    def parcours(current: Path) -> list[str]:
        result = []
        if current.is_file() and current.suffix.lower() == ".xml":
            result.append(str(current.resolve()))
        elif current.is_dir():
            for item in current.iterdir():
                result.extend(parcours(item))
        return result

    return parcours(root)


def walk_glob(sample: str) -> list[str]:
    path = Path(sample)

    if path.is_file() and path.suffix.lower() == ".xml":
        return [str(path.resolve())]

    if path.is_dir():
        return sorted(str(p.resolve()) for p in path.rglob("*.xml"))

    return []


# r1
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
        # Supprimer le CDATA :
        text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
        # Supprimer les balises (dans la description) :
        text = re.sub(r"<[^>]+>", "", text, flags=re.DOTALL)
        # Pour les caractères accentuées et éviter les problèmes d'encodages comme "&#xE9;" pour le "é". Utiliser le module HTML :
        text = re.sub(
            r"&#x([0-9A-Za-z]+);",
            lambda m: chr(
                int(m.group(1), 16)
            ),  # Créer une variable aléatoire "m" qui servira à traduire correctement le caractère qui pose problème, exemple "é" qui est traduit par &#xE9.
            text,
        )
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)

        if not text:
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
        if tag == "description":
            texte = clean_cdata(texte)
        return texte
    # Si la balise n'existe pas, on retourne une chaîne vide
    return ""


def extract_items(xml_content, source_name):
    """Extrait les articles du flux RSS et retourne une liste de dictionnaires."""

    # Extraire les catégories dans channel :
    all_channels = re.findall(
        r"<(?:\w+:)?channel\b[^>]*>(.*?)</(?:\w+:)?channel>",  # Chercher toutes les channels (s'il y en a plusieurs).
        xml_content,
        re.DOTALL,
    )
    channel_content = all_channels[0] if all_channels else ""
    channel_propre = re.sub(
        r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
        "",
        channel_content,
        flags=re.DOTALL,
    )
    channel_categories = re.findall(
        r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>",  # Trouver les catégories dans channel.
        channel_propre,
        re.DOTALL,
    )
    channel_categories = [clean_cdata(categ.strip()) for categ in channel_categories]

    # On récupère tous les blocs <item>...</item>
    # Le namespace éventuel est aussi accepté
    items = re.findall(
        r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>", xml_content, re.DOTALL
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

        # Extraire les catégories dans items :
        item_categories = re.findall(
            r"<(?:\w+:)?(?:category)\b[^>]*>(.*?)</(?:\w+:)?(?:category)>",
            item,
            re.DOTALL,
        )
        item_categories = [clean_cdata(categ.strip()) for categ in item_categories]

        article["categories"] = sorted(channel_categories + item_categories)

        # On ajoute l’article à la liste finale
        metadonnees.append(article)

    return metadonnees


# r2
# Récupère le texte d'une balise.Retourne une chaîne vide si la balise est absente.
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
        print(f"Fichier XML invalide : {chemin_fichier}")
        return articles

    root = tree.getroot()

    channel = root.find(".//channel")
    channel_categories = [
        cat.text.strip() for cat in channel.findall("category") if cat.text
    ]
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
            "categories": sorted(
                set(
                    channel_categories
                    + [cat.text.strip() for cat in item.findall("category") if cat.text]
                )
            ),
        }

        articles.append(article)

    return articles


# 3
"""
3ème méthode : un script avec le module feedparser pour générer les métadonnées de chaque lien URLs.
On retrouvera les métadonnées suivantes :
— l’identifiant (id) de l’article
— la source : le nom du journal, qu’on peut approximer avec le nom du fichier
— le titre de l’article
— le contenu de l’article (description)
— la date de l’article
— les catégories auxquelles appartient l’article
"""


def metadonnees(
    fichier_xml,
):  # Pour le "fichier_xml" : sur le terminal, soit il faut taper le chemin jusqu'au fichier, soit taper le nom du fichier xml.
    """
    Récupérer les métadonnées de chaque article du flux.
    Arguments : le dossier contenant les fichiers xml.
    Return : cette fonction retourne une liste des métadonnées de chaque article dont l'id, la source, le contenu, la date et les catégories.
    """
    feed = feedparser.parse(fichier_xml)  # Pour parser un flux RSS (ou atom).
    metadonnees_articles = (
        []
    )  # Liste vide pour les métadonnées qu'on va récupérer dans chaque article grâce aux fichiers xml.

    # Extraire toutes les métadonnées pour chaque fichier xml :
    for entry in feed.entries:

        # Pour les catégories :
        # 1) Récupérer les "catégorie(s)" dans les fichiers xml :
        channel_categories = [tag.get("term") for tag in feed.feed.get("tags", [])]
        item_categories = [tag.get("term") for tag in entry.get("tags", [])]
        categories = sorted(set(channel_categories + item_categories))
        """
        #2) Conditions pour l'extraction des catégories et du résultats qu'il retourne (soit une ou plusieurs catégories, soit rien).
        if channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Figaro".
            categories = item_categories + channel_categories
        else :
            if channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Flux RSS".
                categories = channel_categories
            else :
                if not channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Bast" et "ELucid".
                    categories = item_categories
                if not channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Libération".
                    categories = []
       """
        # Pour la description - nettoyage de la description :
        description = (
            entry.get("description")
            or entry.get("summary")
            or "No description or summary"
        )
        if (
            description
        ):  # Condition pour supprimer les balises présentes dans la description de certains fichiers xml. On veut garder que du texte. Module utilisé "BeautifulSoup" :
            nettoyer_description = BeautifulSoup(description, "html.parser")
            description_texte = nettoyer_description.get_text(" ", strip=True)

        # Extraire les metadonnées qu'on cherche pour chaque article et les ajouter aux metadonnees_articles :
        metadonnees_articles.append(
            {
                "id": (
                    entry.get("id") or entry.get("link") or "No id"
                ),  # Si la donnée n'apparaît pas dans le fichier xml, alors on notera "No id" pour absence d'identifiant.
                "source": fichier_xml,
                "title": entry.get("title", "No title"),
                "content": description_texte,
                "date": (
                    entry.get("published")
                    or entry.get("updated")
                    or "No published or updated"
                ),
                "categories": categories,
            }
        )

    return metadonnees_articles


# Choix de l'utilisateur pour lancer le programme à partir de trois méthodes :
def read_rss(method, path):
    """
    3 méthodes proposées pour lancer le programme.
    Arguments : le fichier xml.
    Return : cette fonction retourne une liste des métadonnées de chaque article dont l'id, la source, le contenu, la date et les catégories.

    """
    if method == "re":
        return extract_items(read_file(path), os.path.basename(path))
    elif method == "etree":
        return module_etree(path)
    elif method == "feedparser":
        return metadonnees(path)
    else:
        print("Méthode non existante pour lancer ce programme. Veuillez recommencer.")
        sys.exit(1)


# -------------Semaine 3
def filtrage(filtres: list, articles: list[dict]) -> list[dict]:
    """applique successivement les filtres et qui renvoie la liste filtrée (crée une nouvelle liste sans modifier l'ancienne)."""
    filtered_articles = []
    for article in articles:
        check_filtre = True
        for filtre in filtres:
            if not filtre(article):
                check_filtre = False
                break
        if check_filtre:
            filtered_articles.append(article)
    return filtered_articles


# r1 : filtrage par date
# r1 : filtrage par date
def filtre_date(item: dict, date_start_str: str = None, date_end_str: str = None) -> bool:

    from dateutil import parser as date_parser
    from datetime import datetime

    # Si l'article n'a pas de date, on le garde par défaut pour ne pas perdre d'information
    if not item.get("date"):
        return True

    try:
        # Conversion de la date de l'article et suppression du fuseau horaire pour permettre une comparaison simple avec les entrées utilisateur
        item_date = date_parser.parse(item["date"]).replace(tzinfo=None)

        # Filtrage par date de début
        if date_start_str:
            d_start = date_parser.parse(date_start_str).replace(tzinfo=None)
            if item_date < d_start:
                return False

        # Filtrage par date de fin
        if date_end_str:
            d_end = date_parser.parse(date_end_str).replace(tzinfo=None)
            if item_date > d_end:
                return False

    except (ValueError, TypeError):
        # En cas d'erreur de lecture de la date, on conserve l'article par sécurité
        return True

    return True


# r2 : filtrage par source
def filtre_source(item: dict) -> bool:
    """fonction de filtrage en fonction de la ou des sources (nom du journal).
    1) filtrage des sources
    2) garantir l'unicité des articles"""
    return True


# r3 : filtrage par catégorie
def filtre_cat(item: dict) -> bool:
    """fonction de filtrage acceptant une ou plusieurs catégories indiquées dans les balises 'category' des fichiers XML."""
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Lire un fichier xml (flux RSS) avec une méthode à choisir"
    )

    parser.add_argument(
        "-w", "--directory-walker", choices=("os", "pathlib", "glob"), default="glob"
    )

    parser.add_argument(
        "methode",
        choices=["re", "etree", "feedparser"],
        help="Méthode à utiliser : re, etree ou feedparser",
    )

    parser.add_argument(
        "fichier_xml", help="Chemin vers un fichier XML ou un dossier contenant des XML"
    )

    # r1 : filtrage par date
    parser.add_argument("--start", help="Date de début pour le filtrage (AAAA-MM-JJ)")
    parser.add_argument("--end", help="Date de fin pour le filtrage (AAAA-MM-JJ)")

    args = parser.parse_args()

    # Sélection du walker
    if args.directory_walker == "os":
        files = walk_os(args.fichier_xml)
    elif args.directory_walker == "pathlib":
        files = walk_pathlib(args.fichier_xml)
    elif args.directory_walker == "glob":
        files = walk_glob(args.fichier_xml)
    else:
        raise KeyError(f"Unknown walker: {args.directory_walker}")

    if not files:
        print("Aucun fichier XML trouvé.")
        sys.exit(1)

    all_articles = []

    for f in files:
        articles = read_rss(args.methode, f)
        all_articles.extend(articles)

    print(f"\nNombre total d'articles : {len(all_articles)}\n")

    # TODO
    filtres = []

    if args.start or args.end: # Si l'utilisateur a saisi une date de début ou de fin, on active le filtre r1
        filtres.append(lambda item: filtre_date(item, args.start, args.end))

    all_articles = filtrage(filtres, all_articles)

    for article in all_articles:
        for key, value in article.items():
            print(key, ":", value)
        print()


if __name__ == "__main__":
    main()


####### POUR L'UTILISATEUR :
# Lancement du script :
# 1) Ouvrir un terminal et aller dans un environnement virtuel, exemple : source venvs/plurital/bin/activate.
# Sans un environnement virtuel, l'utilisation du module feedparser pour la méthode r3 ne fonctionnera pas.
# 2) Installer feedparser sur le terminal avec la commande suivante : pip install feedparser
# 3) Pour ouvrir ce script, utiliser cette commande avec ces arguments : python3 fichier.py methode chemin/vers/fichier.xml
# Pour lancer plusieur fichier faire python3 rss_reader.py -w glob re Corpus/
# Apres -w mettre glob, pathlib ou os
# Exemple : python3 rss_feedparser.py r3 "Le Figaro - Vidéos.xml"
# N.B. : Parfois, certains fichiers peuvent avoir des "espaces", il faut donc les appeller avec des guillemets (sinon, la machine va croire que ce sont des arguments : d'où l'erreur d'affichage "error: unrecognized arguments:").


#######
