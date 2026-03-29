#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module datastructures - Gestion des Articles et sérialisation multi-formats
Supporte: XML, JSON, Pickle
"""

import sys
import argparse
import json
import pickle
import xml.etree.ElementTree as ET
import spacy
from dataclasses import dataclass, field, asdict
from pathlib import Path


_spacy_nlp = None

def get_spacy_model():
    global _spacy_nlp
    if _spacy_nlp is None:
        _spacy_nlp = spacy.load("fr_core_news_sm")
    return _spacy_nlp


@dataclass
class Token:
    """Classe représentant un token enrichi (Ex 3)"""
    forme: str
    lemme: str | None
    pos: str | None


@dataclass
class Article:
    """Classe représentant un article RSS"""
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)
    tokens: list[Token] = field(default_factory=list)


def article_analyzer(article: Article) -> Article:
    """Retourne l'Article enrichi avec le résultat de l’analyse spaCy."""
    if not article.content:
        return article

    nlp = get_spacy_model()
    doc = nlp(article.content)
    article.tokens = []

    for token in doc:
        article.tokens.append(
            Token(
                forme=token.text,
                lemme=token.lemma_,
                pos=token.pos_,
            )
        )

    return article


# r1
def save_xml(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier XML"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("corpus")
    for art in corpus:
        item = ET.SubElement(root, "item")

        ET.SubElement(item, "id").text = art.id
        ET.SubElement(item, "source").text = art.source
        ET.SubElement(item, "title").text = art.title
        ET.SubElement(item, "content").text = art.content
        ET.SubElement(item, "date").text = art.date
        ET.SubElement(item, "categories").text = "|".join(art.categories)

        tokens_elem = ET.SubElement(item, "tokens")
        for tok in art.tokens:
            tok_elem = ET.SubElement(tokens_elem, "token")
            ET.SubElement(tok_elem, "forme").text = tok.forme or ""
            ET.SubElement(tok_elem, "lemme").text = tok.lemme or ""
            ET.SubElement(tok_elem, "pos").text = tok.pos or ""

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def load_xml(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier XML"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier XML non trouvé: {input_file}")

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        articles = []
        for item in root.findall("item"):
            cats_raw = item.findtext("categories", "")
            categories = cats_raw.split("|") if cats_raw else []

            tokens = []
            tokens_elem = item.find("tokens")
            if tokens_elem is not None:
                for tok_elem in tokens_elem.findall("token"):
                    tokens.append(
                        Token(
                            forme=tok_elem.findtext("forme", ""),
                            lemme=tok_elem.findtext("lemme", ""),
                            pos=tok_elem.findtext("pos", "")
                        )
                    )

            articles.append(
                Article(
                    id=item.findtext("id", ""),
                    source=item.findtext("source", ""),
                    title=item.findtext("title", ""),
                    content=item.findtext("content", ""),
                    date=item.findtext("date", ""),
                    categories=[c for c in categories if c],
                    tokens=tokens
                )
            )
        return articles

    except ET.ParseError as e:
        raise ValueError(f"Fichier XML invalide: {e}")


# r2
def save_json(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier JSON"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([asdict(art) for art in corpus], f, indent=4, ensure_ascii=False)


def load_json(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier JSON"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier JSON non trouvé: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = []
        for art_data in data:
            tokens = [Token(**t) for t in art_data.get("tokens", [])]
            articles.append(
                Article(
                    id=art_data["id"],
                    source=art_data["source"],
                    title=art_data["title"],
                    content=art_data["content"],
                    date=art_data["date"],
                    categories=art_data.get("categories", []),
                    tokens=tokens
                )
            )
        return articles

    except json.JSONDecodeError as e:
        raise ValueError(f"Fichier JSON invalide: {e}")


# r3
def save_pickle(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier Pickle"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "wb") as f:
        pickle.dump(corpus, f)


def load_pickle(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier Pickle"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier Pickle non trouvé: {input_file}")

    try:
        with open(input_file, "rb") as f:
            return pickle.load(f)
    except (pickle.UnpicklingError, EOFError) as e:
        raise ValueError(f"Fichier Pickle invalide: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertir des corpus entre formats (XML, JSON, Pickle)")
    parser.add_argument("input", type=Path, help="Fichier d'entrée")
    parser.add_argument("output", type=Path, help="Fichier de sortie")
    parser.add_argument(
        "--from-format",
        choices=["json", "pickle", "xml"],
        required=True,
        help="Format d'entrée",
    )
    parser.add_argument(
        "--to-format",
        choices=["json", "pickle", "xml"],
        required=True,
        help="Format de sortie",
    )
    args = parser.parse_args()

    loaders = {"json": load_json, "xml": load_xml, "pickle": load_pickle}
    savers = {"json": save_json, "xml": save_xml, "pickle": save_pickle}

    try:
        print(f"Chargement depuis {args.from_format}...", end=" ", flush=True)
        if not args.input.exists():
            raise FileNotFoundError(f"Le fichier {args.input} n'existe pas.")

        corpus = loaders[args.from_format](args.input)
        print(f"({len(corpus)} articles)")

        print(f"Sauvegarde en {args.to_format}...", end=" ", flush=True)
        savers[args.to_format](corpus, args.output)
        print(f"Conversion réussie: {args.input} → {args.output}")

    except FileNotFoundError as e:
        print(f"Erreur de fichier: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")
        sys.exit(1)
