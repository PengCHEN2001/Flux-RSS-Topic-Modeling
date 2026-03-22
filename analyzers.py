import argparse
from pathlib import Path

from datastructures import (
    Article,
    article_analyzer,
    load_json,
    load_pickle,
    load_xml,
    save_json,
    save_pickle,
    save_xml,
)


def analyze_corpus(corpus: list[Article]) -> list[Article]:
    return [article_analyzer(article) for article in corpus]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Charge un corpus, l'analyse avec spaCy et sauvegarde le resultat."
    )
    parser.add_argument(
        "--from-format",
        choices=["json", "pickle", "xml"],
        required=True,
        help="Format du fichier d'entree.",
    )
    parser.add_argument(
        "--to-format",
        choices=["json", "pickle", "xml"],
        help="Format du fichier de sortie. Par defaut: meme format que l'entree.",
    )
    parser.add_argument("input", type=Path, help="Fichier d'entree")
    parser.add_argument("output", type=Path, help="Fichier de sortie")

    args = parser.parse_args()

    loaders = {
        "xml": load_xml,
        "json": load_json,
        "pickle": load_pickle,
    }
    savers = {
        "xml": save_xml,
        "json": save_json,
        "pickle": save_pickle,
    }

    output_format = args.to_format or args.from_format

    corpus = loaders[args.from_format](args.input)
    corpus = analyze_corpus(corpus)
    for article in corpus[:5]:
        print(f"id : {article.id}")
        print(f"source : {article.source}")
        print(f"title : {article.title}")
        print(f"description : {article.content}")
        print(f"date : {article.date}")
        print(f"categories : {article.categories}")
        print(f"tokens : {article.tokens}")
        print()
    savers[output_format](corpus, args.output)

    print(f"Corpus charge : {len(corpus)} article(s)")
    print(f"Corpus analyse et sauvegarde dans : {args.output}")


if __name__ == "__main__":
    main()
