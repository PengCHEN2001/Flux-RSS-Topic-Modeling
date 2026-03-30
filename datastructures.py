#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if __name__ == "__main__":
    sys.modules["datastructures"] = sys.modules[__name__]

import argparse
import json
import pickle
from dataclasses import dataclass, field, asdict
import spacy
from pathlib import Path
import xml.etree.ElementTree as ET

nlp = spacy.load("fr_core_news_sm")


@dataclass
class Token:
    """Dataclass d’interface commune pour stocker les résultats des analyseurs."""

    text: str
    lemme: str
    pos: str


@dataclass
class Article:
    """Classe représentant un article RSS."""

    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)
    tokens: list[Token] = field(default_factory=list)

    @property
    def description(self) -> str:
        """Alias de compatibilité avec d'anciens fichiers."""
        return self.content


@dataclass
class Topic:
    coherence_score:float
    topic_representation: list[dict]
    
    
#r1

def article_analyzer(article: Article) -> Article:
    """retourne l'Article enrichi avec le résultat de l’analyse"""
    doc = nlp(article.content)
    article.tokens = []
    for token in doc:
        article.tokens.append(
            Token(
                text=token.text,
                lemme=token.lemma_,
                pos=token.pos_,
            )
        )
    return article


def _serialize_token(token: Token) -> dict[str, str]:
    return {
        "text": token.text,
        "lemme": token.lemme,
        "pos": token.pos,
    }


def _deserialize_token(data: object, input_file: Path) -> Token:
    if isinstance(data, Token):
        return data

    if not isinstance(data, dict):
        raise ValueError(f"Le fichier {input_file} contient un token invalide.")

    return Token(
        text=str(data.get("text", data.get("text", ""))),
        lemme=str(data.get("lemme", data.get("lemma", ""))),
        pos=str(data.get("pos", "")),
    )


def save_pickle(corpus: list[Article], output_file: Path) -> None:
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "wb") as f:
        pickle.dump(corpus, f)


def load_pickle(input_file: Path) -> list[Article]:
    input_file = Path(input_file)

    with open(input_file, "rb") as f:
        corpus = pickle.load(f)

    if not isinstance(corpus, list):
        raise ValueError(f"Le fichier {input_file} n'est pas un corpus sérialisé.")

    for article in corpus:
        if not isinstance(article, Article):
            raise ValueError(
                f"Le fichier {input_file} contient des données incompatibles."
            )
        if not isinstance(article.tokens, list):
            raise ValueError(f"Le fichier {input_file} contient des tokens invalides.")
        article.tokens = [
            _deserialize_token(token, input_file) for token in article.tokens
        ]

    return corpus


def save_json(corpus: list[Article], output_file: Path) -> None:
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = [
        {
            "id": article.id,
            "source": article.source,
            "title": article.title,
            "content": article.content,
            "date": article.date,
            "categories": article.categories,
            "tokens": [_serialize_token(token) for token in article.tokens],
        }
        for article in corpus
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(input_file: Path) -> list[Article]:
    input_file = Path(input_file)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Le fichier {input_file} n'est pas un corpus JSON valide.")

    corpus = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"Le fichier {input_file} contient des données invalides.")

        categories = item.get("categories", [])
        tokens = item.get("tokens", item.get("analysis", []))

        if not isinstance(categories, list):
            raise ValueError(
                f"Le fichier {input_file} contient des catégories invalides."
            )
        if not isinstance(tokens, list):
            raise ValueError(f"Le fichier {input_file} contient des tokens invalides.")

        content = str(item.get("content", item.get("description", "")))

        corpus.append(
            Article(
                id=str(item.get("id", "")),
                source=str(item.get("source", "")),
                title=str(item.get("title", "")),
                content=content,
                date=str(item.get("date", "")),
                categories=[str(category) for category in categories],
                tokens=[_deserialize_token(token, input_file) for token in tokens],
            )
        )

    return corpus


def save_xml(corpus: list[Article], output_file: Path) -> None:
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("corpus")

    for article in corpus:
        article_element = ET.SubElement(root, "article")
        ET.SubElement(article_element, "id").text = article.id
        ET.SubElement(article_element, "source").text = article.source
        ET.SubElement(article_element, "title").text = article.title
        ET.SubElement(article_element, "content").text = article.content
        ET.SubElement(article_element, "date").text = article.date

        categories_element = ET.SubElement(article_element, "categories")
        for category in article.categories:
            ET.SubElement(categories_element, "category").text = category

        tokens_element = ET.SubElement(article_element, "tokens")
        for token in article.tokens:
            token_element = ET.SubElement(tokens_element, "token")
            ET.SubElement(token_element, "text").text = token.text
            ET.SubElement(token_element, "lemme").text = token.lemme
            ET.SubElement(token_element, "pos").text = token.pos

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def load_xml(input_file: Path) -> list[Article]:
    input_file = Path(input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()

    if root.tag != "corpus":
        raise ValueError(f"Le fichier {input_file} n'est pas un corpus XML valide.")

    corpus = []
    for article_element in root.findall("article"):
        categories_element = article_element.find("categories")
        categories = []
        if categories_element is not None:
            categories = [
                category.text or ""
                for category in categories_element.findall("category")
            ]

        tokens = []
        tokens_element = article_element.find("tokens")
        if tokens_element is not None:
            for token_element in tokens_element.findall("token"):
                tokens.append(
                    Token(
                        text=token_element.findtext("text", default=""),
                        lemme=token_element.findtext("lemme", default=""),
                        pos=token_element.findtext("pos", default=""),
                    )
                )

        corpus.append(
            Article(
                id=article_element.findtext("id", default=""),
                source=article_element.findtext("source", default=""),
                title=article_element.findtext("title", default=""),
                content=article_element.findtext(
                    "content",
                    default=article_element.findtext("description", default=""),
                ),
                date=article_element.findtext("date", default=""),
                categories=categories,
                tokens=tokens,
            )
        )

    return corpus


def main():
    parser = argparse.ArgumentParser(
        description="Conversion d'un format à l'autre (xml, json, pickle)"
    )

    parser.add_argument(
        "-in", "--input", choices=["xml", "json", "pickle"], required=True
    )
    parser.add_argument(
        "-out", "--output", choices=["xml", "json", "pickle"], required=True
    )
    parser.add_argument("fichier")

    args = parser.parse_args()

    input_file = Path(args.fichier)
    output_file = input_file.with_suffix(f".{args.output}")

    load = {
        "xml": load_xml,
        "json": load_json,
        "pickle": load_pickle,
    }

    save = {
        "xml": save_xml,
        "json": save_json,
        "pickle": save_pickle,
    }

    corpus = load[args.input](input_file)
    save[args.output](corpus, output_file)

    print(f"Conversion terminée: {args.input} vers {args.output}")


if __name__ == "__main__":
    main()
