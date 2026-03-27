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
    """Classe représentant un token enrichi (Ex 3)"""
    form: str
    lemma: str
    pos: str

@dataclass
class Article:
    """Classe représentant un article RSS"""
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)
    # Champ ajouté pour l'Exercice 3 : liste de tokens (vide par défaut)
    tokens: list[Token] = field(default_factory=list)

#r1
def save_xml(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier XML (mis à jour Ex 3)"""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    root = ET.Element("corpus")
    for art in corpus:
        item = ET.SubElement(root, "item")
        # Transformation en dictionnaire pour itérer
        art_dict = asdict(art)
        for key, value in art_dict.items():
            child = ET.SubElement(item, key)
            if key == "tokens" and value:
                # Structure spécifique pour les tokens en XML
                for t in value:
                    t_elem = ET.SubElement(child, "token")
                    t_elem.set("form", t["form"])
                    t_elem.set("lemma", t["lemma"])
                    t_elem.set("pos", t["pos"])
            elif isinstance(value, list):
                child.text = "|".join(value)
            else:
                child.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def load_xml(input_file: Path) -> list[Article]:
    """Charge une liste d'articles depuis un fichier XML (mis à jour Ex 3)"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier XML non trouvé: {input_file}")

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        articles = []
        for item in root.findall("item"):
            cats_raw = item.findtext("categories", "")
            cats_list = cats_raw.split("|") if cats_raw else []

            # Reconstruction des tokens
            tokens_list = []
            tokens_node = item.find("tokens")
            if tokens_node is not None:
                for t_node in tokens_node.findall("token"):
                    tokens_list.append(Token(
                        form=t_node.get("form", ""),
                        lemma=t_node.get("lemma", ""),
                        pos=t_node.get("pos", "")
                    ))

            articles.append(Article(
                id=item.findtext("id", ""),
                source=item.findtext("source", ""),
                title=item.findtext("title", ""),
                content=item.findtext("content", ""),
                date=item.findtext("date", ""),
                categories=[c for c in cats_list if c],
                tokens=tokens_list
            ))
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
    """Charge une liste d'articles depuis un fichier JSON (mis à jour Ex 3)"""
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Fichier JSON non trouvé: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles = []
            for art_data in data:
                # Gérer la conversion des dictionnaires de tokens en objets Token
                if "tokens" in art_data:
                    art_data["tokens"] = [Token(**t) for t in art_data["tokens"]]
                articles.append(Article(**art_data))
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


# Main reste identique pour la conversion de formats.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertir des corpus entre formats (XML, JSON, Pickle)")
    parser.add_argument("input", type=Path, help="Fichier d'entrée")
    parser.add_argument("output", type=Path, help="Fichier de sortie")
    parser.add_argument("--from-format", choices=["json", "pickle", "xml"], required=True, help="Format d'entrée")
    parser.add_argument("--to-format", choices=["json", "pickle", "xml"], required=True, help="Format de sortie")
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
