#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import pickle
from dataclasses import dataclass, field, asdict
from pathlib import Path
import xml.etree.ElementTree as ET



@dataclass
class Token:
    """Dataclass d’interface commune pour stocker les résultats des analyseurs."""

    text: str
    lemma: str
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
    analysis: list[list[Token]] = field(default_factory=list)

    @property
    def description(self) -> str:
        """Alias de compatibilité avec d'anciens fichiers."""
        return self.content

    
  
def save_json(corpus: list[Article], output_file: Path) -> None:
    output_file.write_text(json.dumps(list(map(asdict, corpus)), ensure_ascii=False))


def load_json(input_file: Path) -> list[Article]:
    corpus = [Article(**a) for a in json.loads(input_file.read_text())]
    for a in corpus:
        a.analysis = [[Token(**t) for sentence in a.analysis for t in sentence]]
    return corpus



def save_pickle(corpus: list[Article], output_file: Path) -> None:
    output_file.write_bytes(pickle.dumps(corpus))


def load_pickle(input_file: Path) -> list[Article]:
    return pickle.loads(input_file.read_bytes())


def save_xml(corpus: list[Article], output_file: Path) -> None:
    root = ET.Element("corpus")
    for a in corpus:
        attribs = {
            'artid': a.id,
            'source': a.source,
            'date': a.date
        }
        art = ET.SubElement(root, "article", attrib=attribs)
        title = ET.SubElement(art, "title")
        title.text = a.title
        description = ET.SubElement(art, "description")
        description.text = a.description
        for cat in a.categories:
            category = ET.SubElement(art, "category")
            category.text = cat
        if a.analysis:
            analysis_e = ET.SubElement(art, "analysis")
            for sentence in a.analysis: 
                sent_e = ET.SubElement(analysis_e, "sentence")
                for token in sentence:
                    token_e = ET.SubElement(sent_e, "token")
                    text_e = ET.SubElement(token_e, "text").text = token.text
                    lemma_e = ET.SubElement(token_e, "lemma").text = token.lemma
                    pos_e = ET.SubElement(token_e, "pos").text = token.pos
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8")

def load_xml(input_file: Path) -> list[Article]:
    articles: list[Article] = []
    tree = ET.parse(input_file)
    root = tree.getroot()
    for a in root.findall("article"):
        categories = [c.text for c in a.findall("category") if c.text]

        analysis = []
        for sent_node in list(a.find("analysis") or []):  
            sentence = []
            for token in list(sent_node):  
                sentence.append(Token(token.find("text").text, token.find("lemma").text, token.find("pos").text))
            analysis.append(sentence)

        articles.append(
            Article(
                a.attrib['artid'],
                a.attrib['source'],
                a.findtext("title", default=""),
                a.findtext("description", default=""),
                a.attrib['date'],
                categories,
                analysis
            )
        )
    return articles


suffix2loader = {".json": load_json, ".pkl": load_pickle, ".xml": load_xml}
suffix2writer = {".json": save_json, ".pkl": save_pickle, ".xml": save_xml}

