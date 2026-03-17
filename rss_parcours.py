#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from datetime import datetime
from dateutil import parser as date_parser

from rss_reader import read_rss
from datastructures import Article


def walk_glob(sample: str):

    path = Path(sample)

    if path.is_file() and path.suffix == ".xml":
        return [path]

    if path.is_dir():
        return list(path.rglob("*.xml"))

    return []


def filtre_date(article: Article, start=None, end=None):
    if not article.date:
        return True
    try:
        item_date = date_parser.parse(article.date).replace(tzinfo=None)

        if start:
            start_date = date_parser.parse(start).replace(tzinfo=None)
            if item_date < start_date:
                return False

        if end:
            end_date = date_parser.parse(end).replace(tzinfo=None)
            if item_date > end_date:
                return False

    except Exception:
        return True

    return True


def filtre_source(article: Article, sources):
    for s in sources:
        if s.lower() in article.source.lower():
            return True

    return False


def filtre_categorie(article: Article, categories):
    article_categories = [c.lower() for c in article.categories]

    for c in categories:
        if c.lower() not in article_categories:
            return False

    return True


def dedoublonnage(articles):

    seen = set()
    unique = []

    for a in articles:
        if a.id not in seen:
            seen.add(a.id)
            unique.append(a)

    return unique


def main():

    parser = argparse.ArgumentParser(
        description="Parcourir un dossier RSS"
    )

    parser.add_argument(
        "path",
        help="Fichier ou dossier contenant des RSS"
    )

    parser.add_argument(
        "-m",
        "--method",
        choices=("etree", "feedparser"),
        default="feedparser",
    )

    parser.add_argument("-s", "--source", nargs="+")
    parser.add_argument("-c", "--categories", nargs="+")
    parser.add_argument("--start")
    parser.add_argument("--end")

    args = parser.parse_args()

    files = walk_glob(args.path)

    if not files:
        print("Aucun fichier XML trouvé")
        return

    articles = []

    for f in files:
        articles.extend(read_rss(args.method, str(f)))

    articles = dedoublonnage(articles)

    filtres = []

    if args.source:
        filtres.append(lambda a: filtre_source(a, args.source))

    if args.categories:
        filtres.append(lambda a: filtre_categorie(a, args.categories))

    if args.start or args.end:
        filtres.append(lambda a: filtre_date(a, args.start, args.end))

    filtered = []

    for a in articles:
        ok = True
        for f in filtres:
            if not f(a):
                ok = False
                break
        if ok:
            filtered.append(a)

    print(f"Articles trouvés : {len(filtered)}\n")

    for a in filtered:
        print(a)
        print()


if __name__ == "__main__":
    main()