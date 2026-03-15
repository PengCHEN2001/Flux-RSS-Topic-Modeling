

import json
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path

@dataclass
class Article:
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)

def save_xml(corpus: list[Article], output_file: Path) -> None:
    root = ET.Element("corpus")
    for art in corpus:
        item = ET.SubElement(root, "item")
        for key, value in asdict(art).items():
            child = ET.SubElement(item, key)
            if isinstance(value, list):
                child.text = "|".join(value)
            else:
                child.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def load_xml(input_file: Path) -> list[Article]:
    tree = ET.parse(input_file)
    root = tree.getroot()
    articles = []
    for item in root.findall("item"):
        cats_raw = item.findtext("categories", "")
        cats_list = cats_raw.split("|") if cats_raw else []
        articles.append(Article(
            id=item.findtext("id", ""),
            source=item.findtext("source", ""),
            title=item.findtext("title", ""),
            content=item.findtext("content", ""),
            date=item.findtext("date", ""),
            categories=[c for c in cats_list if c]
        ))
    return articles

def save_json(corpus: list[Article], output_file: Path) -> None:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(art) for art in corpus], f, indent=4, ensure_ascii=False)

def load_json(input_file: Path) -> list[Article]:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Article(**art) for art in data]

def save_pickle(corpus: list[Article], output_file: Path) -> None:
    with open(output_file, 'wb') as f:
        pickle.dump(corpus, f)

def load_pickle(input_file: Path) -> list[Article]:
    with open(input_file, 'rb') as f:
        return pickle.load(f)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tester la sérialisation des corpus")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--from-format", choices=["json", "pickle", "xml"], required=True)
    parser.add_argument("--to-format", choices=["json", "pickle", "xml"], required=True)
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

    corpus = loaders[args.from_format](args.input)
    savers[args.to_format](corpus, args.output)