#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
from pathlib import Path
from datastructures import Article
import re
import xml.etree.ElementTree as ET
import feedparser
import argparse  # Pour appeler notre fonction.
import sys
from datetime import datetime
from dateutil import parser as date_parser

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
    return ""


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
    """Extrait les articles du flux RSS et retourne une liste d'objets Article."""

    all_channels = re.findall(
        r"<(?:\w+:)?channel\b[^>]*>(.*?)</(?:\w+:)?channel>",
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
        r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>",
        channel_propre,
        re.DOTALL,
    )
    channel_categories = [clean_cdata(categ.strip()) for categ in channel_categories]

    items = re.findall(
        r"<(?:\w+:)?item\b[^>]*>(.*?)</(?:\w+:)?item>",
        xml_content,
        re.DOTALL,
    )

    metadonnees = []

    for item in items:
        guid = extract_tag(item, "guid")
        link = extract_tag(item, "link")
        article_id = guid if guid else link

        title = extract_tag(item, "title")
        content = extract_tag(item, "description")
        date = extract_tag(item, "pubDate")

        item_categories = re.findall(
            r"<(?:\w+:)?category\b[^>]*>(.*?)</(?:\w+:)?category>",
            item,
            re.DOTALL,
        )
        item_categories = [clean_cdata(categ.strip()) for categ in item_categories]

        categories = sorted(set(channel_categories + item_categories))

        article = Article(
            id=article_id,
            source=source_name,
            title=title,
            content=content,
            date=date,
            categories=categories,
        )

        metadonnees.append(article)

    return metadonnees


# r2
# Récupère le texte d'une balise.Retourne une chaîne vide si la balise est absente.
def get_text(parent, tag):
    elem = parent.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""


# Traite UN fichier RSS XML Retourne une liste d'articles
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

    channel_categories = [
        cat.text.strip() for cat in channel.findall("category") if cat.text
    ]

    for item in channel.findall("item"):

        dataid = get_text(item, "guid") or get_text(item, "link")
        title = get_text(item, "title")
        raw_content = get_text(item, "description")
        clean_content = clean_cdata(raw_content)
        pubdate = get_text(item, "pubDate")
        if not pubdate:
            pubdate = get_text(item, "lastpublished")

        categories = sorted(
            set(
                channel_categories
                + [cat.text.strip() for cat in item.findall("category") if cat.text]
            )
        )

        article = Article(
            id=dataid,
            source=os.path.basename(chemin_fichier),
            title=title,
            content=clean_content,
            date=pubdate,
            categories=categories,
        )

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


def metadonnees(fichier_xml):
    feed = feedparser.parse(fichier_xml)
    metadonnees_articles = []

    for entry in feed.entries:
        channel_categories = [
            tag.get("term") for tag in feed.feed.get("tags", []) if tag.get("term")
        ]
        item_categories = [
            tag.get("term") for tag in entry.get("tags", []) if tag.get("term")
        ]
        categories = sorted(set(channel_categories + item_categories))

        description = (
            entry.get("description")
            or entry.get("summary")
            or "No description or summary"
        )

        description_texte = clean_cdata(description)

        article = Article(
            id=entry.get("id") or entry.get("link") or "No id",
            source=fichier_xml,
            title=entry.get("title", "No title"),
            content=description_texte,
            date=entry.get("published") or entry.get("updated") or "No published or updated",
            categories=categories,
        )

        metadonnees_articles.append(article)

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
def filtrage(filtres: list, articles: list[Article]) -> list[Article]:
    """applique successivement les filtres et renvoie la liste filtrée (crée une nouvelle liste sans modifier l'ancienne)"""
    filtered_articles = []
    for article in articles:
        check_filtre = True
        for filtre in filtres:
            # On appelle la fonction filtre_date/source/cat avec l'article en argument
            if not filtre(article):
                check_filtre = False
                break
        if check_filtre:
            filtered_articles.append(article)
    return filtered_articles


# r1 : filtrage par date
def filtre_date(
    item: Article, date_start_str: str | None = None, date_end_str: str | None = None
) -> bool:
    """fonction de filtrage en fonction de la date
    Les dates doivent être parsées avec le module 'datetime'"""

    # Si l'article n'a pas de date, on le garde par défaut pour ne pas perdre d'information
    if not item.date:
        return True

    try:
        # Conversion de la date de l'article et suppression du fuseau horaire pour permettre une comparaison simple avec les entrées utilisateur
        item_date = date_parser.parse(item.date).replace(tzinfo=None)

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
def filtrage_source(article: Article, source: list[str]) -> bool:
    source_actuel = article.source.lower()
    for s in source:
        if s.lower() in source_actuel:
            return True
    return False


# r2 : dédoublonnage
def filtrage_repetition(articles: list[Article]) -> list[Article]:
    liste_article = []
    liste_ids = []
    for a in articles:
        if a.id not in liste_ids:
            liste_ids.append(a.id)
            liste_article.append(a)
    return liste_article


# r3 : filtrage par catégorie
def filtre_cat(article: Article, categories: list[str]) -> bool | None:
    """fonction de filtrage acceptant une ou plusieurs catégories indiquées dans les balises 'category' des fichiers XML."""
    check_cat = True
    article_categories = [cat.lower() for cat in article.categories]
    for category in categories:
        if not category.strip().lower() in article_categories:
            check_cat = False
            break
    return check_cat


def main():
    parser = argparse.ArgumentParser(description="Lire un fichier RSS")
    parser.add_argument(
        "filepath", help="Filepath to be analyzed, either a single file or a directory"
    )
    parser.add_argument(
        "-r",
        "--reader",
        required=True,
        choices=("re", "etree", "feedparser"),
        default="etree",
    )

    args = parser.parse_args()
    parsed_fichier= read_rss(args.reader, args.filepath )
    for article in parsed_fichier :
        for k, v in vars(article).items() :
            print(f"{k} : {v}")
        print("\n" + "-" * 40)

if __name__ == "__main__":
    main()
