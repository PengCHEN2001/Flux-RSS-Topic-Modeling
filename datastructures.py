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
from dataclasses import dataclass, field, asdict
from pathlib import Path

@dataclass
class Token:
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
    # pour garder une liste plate
    tokens: list[Token] = field(default_factory=list)

@dataclass
class Topic:
    coherence_score:float
    topic_representation: list[dict]
#r1
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
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

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

#r2
def save_json(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier JSON"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(art) for art in corpus], f, indent=4, ensure_ascii=False)

def load_json(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier JSON"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier JSON non trouvé: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        articles = []
        for art in data:
            tokens = [Token(**tok) for tok in art.get("tokens", [])]
            articles.append(
                Article(
                    id=art["id"],
                    source=art["source"],
                    title=art["title"],
                    content=art["content"],
                    date=art["date"],
                    categories=art.get("categories", []),
                    tokens=tokens
                )
            )
        return articles
    except json.JSONDecodeError as e:
        raise ValueError(f"Fichier JSON invalide: {e}")

#r3
def save_pickle(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier Pickle"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'wb') as f:
        pickle.dump(corpus, f)

def load_pickle(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier Pickle"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier Pickle non trouvé: {input_file}")

    try:
        with open(input_file, 'rb') as f:
            return pickle.load(f)
    except (pickle.UnpicklingError, EOFError) as e:
        raise ValueError(f"Fichier Pickle invalide: {e}")


#Mis à jour du main pour utiliser les fonctions de l'exercice 2.

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convertir des corpus entre formats (XML, JSON, Pickle)")
    parser.add_argument("input",
                        type=Path,
                        help="Fichier d'entrée")
    parser.add_argument("output",
                        type=Path,
                        help="Fichier de sortie")
    parser.add_argument("--from-format",
                        choices=["json", "pickle", "xml"],
                        required=True,
                        help="Format d'entrée")
    parser.add_argument("--to-format",
                        choices=["json", "pickle", "xml"],
                        required=True, help="Format de sortie")
    args = parser.parse_args()

    loaders = {
        "json": load_json,
        "xml": load_xml,
        "pickle": load_pickle
    }

    savers = {
        "json": save_json,
        "xml": save_xml,
        "pickle": save_pickle
    }

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
