#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Callable
import os.path
import sys
import argparse
from pathlib import Path
from dateutil import parser as date_parser
from rss_reader import read_rss
from datastructures import  Article,load_json, load_pickle, load_xml, save_json, save_pickle, save_xml

def walk_os(corpus: str) -> list[str]:
    if os.path.isfile(corpus):
        if corpus.endswith(".xml"):
            return [corpus]
        else:
            return []

    files = sorted(os.path.join(corpus, file) for file in os.listdir(corpus))

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


def walk_pathlib(corpus: str) -> list[str]:
    root = Path(corpus)

    def parcours(current: Path) -> list[str]:
        result = []
        if current.is_file() and current.suffix.lower() == ".xml":
            result.append(str(current.resolve()))
        elif current.is_dir():
            for item in current.iterdir():
                result.extend(parcours(item))
        return result

    return parcours(root)


def walk_glob(corpus: str) -> list[str]:
    path = Path(corpus)

    if path.is_file() and path.suffix.lower() == ".xml":
        return [str(path.resolve())]

    if path.is_dir():
        return sorted(str(p.resolve()) for p in path.rglob("*.xml"))

    return []


def filtre_start_date(start: str) -> Callable[[Article], bool]:
    def filtre(article: Article) -> bool:
        if not article.date:
            return False
        try:
            article_date = date_parser.parse(article.date).replace(tzinfo=None)
            start_date = date_parser.parse(start).replace(tzinfo=None)
            return article_date >= start_date
        except Exception:
            return False

    return filtre


def filtre_end_date(end: str) -> Callable[[Article], bool]:
    def filtre(article: Article) -> bool:
        if not article.date:
            return False
        try:
            article_date = date_parser.parse(article.date).replace(tzinfo=None)
            end_date = date_parser.parse(end).replace(tzinfo=None)
            return article_date <= end_date
        except Exception:
            return False

    return filtre


def filtre_par_source(sources: list[str]) -> Callable[[Article], bool]:
    def filtre(article: Article) -> bool:
        for source in sources:
            if source.lower() in article.source.lower():
                return True
        return False

    return filtre


def filtre_par_categories(categories: list[str]):
    cat_set = set(c.lower() for c in categories)

    def filtre(article: Article):
        article_set = set(c.lower() for c in article.categories)
        return len(cat_set & article_set) > 0  

    return filtre

def apply_filters(
    articles: list[Article], filtres: list[Callable[[Article], bool]]
) -> list[Article]:
    result = []
    for article in articles:
        if all(f(article) for f in filtres):
            result.append(article)
    return result


def dedoublonnage(articles: list[Article]) -> list[Article]:
    seen = set()
    unique = []

    for article in articles:
        if article.id not in seen:
            seen.add(article.id)
            unique.append(article)

    return unique


def filtrage(articles: list[Article], args: argparse.Namespace) -> list[Article]:
    filtres = []

    if args.start:
        filtres.append(filtre_start_date(args.start))
    if args.end:
        filtres.append(filtre_end_date(args.end))
    if args.categories:
        filtres.append(filtre_par_categories(args.categories))
    if args.source:
        filtres.append(filtre_par_source(args.source))

    return apply_filters(articles, filtres)


def charger_corpus_serialise(input_format: str, input_file: Path) -> list[Article]:
    fonctions_load = {
        "xml": load_xml,
        "json": load_json,
        "pickle": load_pickle,
    }
    return fonctions_load[input_format](input_file)


def sauvegarder_corpus_serialise(
    corpus: list[Article], output_format: str, output_file: Path
) -> None:
    fonctions_save = {
        "xml": save_xml,
        "json": save_json,
        "pickle": save_pickle,
    }
    fonctions_save[output_format](corpus, output_file)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lire un fichier XML RSS ou parcourir un dossier de fichiers XML RSS."
    )

    parser.add_argument(
        "-c",
        "--corpus", help="Fichier XML ou dossier contenant des fichiers XML RSS."
    )

    parser.add_argument(
        "-w",
        "--directory-walker",
        choices=("os", "pathlib", "glob"),
        default="glob",
        help="Méthode utilisée pour parcourir les fichiers XML.",
    )

    parser.add_argument(
        "-m",
        "--method",
        choices=("re", "etree", "feedparser"),
        default="feedparser",
        help="Méthode de lecture à utiliser.",
    )

    parser.add_argument(
        "-s", "--source", nargs="+", help="Filtrer par une ou plusieurs sources."
    )

    parser.add_argument(
        "-cat", "--categories", nargs="+", help="Filtrer par une ou plusieurs catégories."
    )

    parser.add_argument("--start", help="Date de début pour le filtrage.")

    parser.add_argument("--end", help="Date de fin pour le filtrage.")

    parser.add_argument(
        "--input-file", type=Path, help="Chemin vers un corpus deja sérialisé"
    )
    parser.add_argument(
        "--input-format",
        choices=["xml", "json", "pickle"],
        help="Format du corpus sérialisé en entree",
    )
    parser.add_argument(
        "--output-file", type=Path, help="Chemin de sortie pour sauvegarder le corpus"
    )
    parser.add_argument(
        "--output-format",
        choices=["xml", "json", "pickle"],
        help="Format du corpus sérialisé en sortie",
    )

    args = parser.parse_args()


    # Chargement des articles depuis un corpus sérialisé ou depuis les fichiers XML
    if args.input_file:
        articles = charger_corpus_serialise(args.input_format, args.input_file)
    else:
        name2walker = {
            "os": walk_os,
            "pathlib": walk_pathlib,
            "glob": walk_glob,
        }
        walker = name2walker[args.directory_walker]
        corpus = walker(args.corpus)

        if not corpus:
            print("Aucun fichier XML trouvé.")
            sys.exit(1)

        articles = []
        for rss_feed in corpus:
            articles.extend(read_rss(args.method, rss_feed))
    
    articles = dedoublonnage(articles)
    articles = filtrage(articles, args)

    if args.output_file:
        sauvegarder_corpus_serialise(articles, args.output_format, args.output_file)

    for article in articles:
        print(f"id : {article.id}")
        print(f"source : {article.source}")
        print(f"title : {article.title}")
        print(f"description : {article.content}")
        print(f"date : {article.date}")
        print(f"categories : {article.categories}")
        print()
        
    print (f"Articles trouvés : {len(articles)}\n")

if __name__ == "__main__":
    main()
