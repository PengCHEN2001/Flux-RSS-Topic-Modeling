#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse
import json
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

@dataclass
class Article:
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)
#r1
def save_xml(corpus: list[Article], output_file: Path) -> None:
    """Sauvegarde une liste d'articles en fichier XML"""
    output_file = Path(output_file)
    # Créer le répertoire parent s'il n'existe pas
    output_file.parent.mkdir(parents=True, exist_ok=True)

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

    except ET.ParseError as e:
        raise ValueError(f"Fichier XML invalide: {e}")

#r2
def save_json(corpus: list[Article], output_file: Path) -> None:
    #sauvegarde un corpus d'article dans un json
    #corpus --> liste d'ojbets Article
    #output_file --> chemin fichier sortie

    #liste qui va contenir les articles converti en dico
    donnees= []
    
    #on parcourt tous les articles du corpus
    for article in corpus:
        #donnees.append(asdict(article))
        article_dict= {
            "id": article.id,
            "source": article.source,
            "title": article.title,
            "content": article.content,
            "date": article.date,
            "categories": article.categories
        }

        #ajouter ce dico à la liste
        données.append(article_dict) #enlevé le commentaire ici pour que tout fonctionne
    #ouvrir fichier de sortir en écriture ("w")    
    with open(output_file, "w", encoding="utf-8") as f:
        #json.dump va écrire la structure python dans json
        #ensure_ascii=False --> on garde les acccents
        #indent=2 --> rendre fichier lisible
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def load_json(input_file: Path) -> list[Article]:
    #chargement en format json 
    #input_file --> chemin vers json à lire
    #retourne --> liste d'obejts Article

    #on ouvre le fichier json
    with open(input_file, "r", encoding="utf-8") as f:
        donnees= json.load(f) #devient une liste de dico

    #liste qui va contenit les obj Article recrée    
    corpus=[]

    #on parcourt chaq dico 
    for item in donnees:
        #on recrée un obj Article avec les vaelurs du dico
        article = Article(
            id=item["id"],
            source=item["source"],
            title=item["title"],
            content=item["content"],
            date=item["date"],
            categories= item.get("categories", []),
        
        )

        #on ajoute l'article au corpus
        corpus.append(article)
        
    return corpus 



#r3
def save_pickle(corpus: list[Article], output_file: Path) -> None:
    #Sauvegarde la liste d'articles au format binaire pickle.
    with open(output_file, 'wb') as f: #wb : write binary
        pickle.dump(corpus, f)

def load_pickle(input_file: Path) -> list[Article]:
    try:#ajout gestion d'erreur
        #Charge et retourne une liste d'articles depuis un fichier pickle.
        with open(input_file, 'rb') as f: #rb : read binary
            return pickle.load(f)
    except Exception as e: #ajout gestion d'erreur
        print(f"erreur lors du chargement de pickle: {e}")
        return []





if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tester la sérialisation des corpus")
    parser.add_argument("input", type=Path, help="Fichier source")
    parser.add_argument("output", type=Path, help="Fichier cible")
    parser.add_argument("--from-format", choices=["json", "pickle", "xml"], required=True)#passer d'un format à un autre 
    parser.add_argument("--to-format", choices=["json", "pickle", "xml"], required=True)#passer d'un format à un autre 
    args = parser.parse_args()

    #charger le corpus
    if args.from_format == "json":
        corpus = load_json(args.input)
    elif args.from_format == 'pickle':
        corpus= load_pickle(args.input)
    elif args.from_format == 'xml':
        corpus = load_xml(args.input)
    else:
        raise ValueError(f'format inconnu: {args.from_format}')
    

    #sauvegarder dans le nouveau format
    if args.to_format == "json":
        save_json(corpus, args.output)
        print(f"Le corpus a bien été converti de {args.from_format} vers {args.to_format}")
    elif args.to_format == 'pickle':
        save_pickle(corpus, args.output)
        print(f"Le corpus a bien été converti de {args.from_format} vers {args.to_format}")
    elif args.to_format == 'xml':
        save_xml(corpus, args.output)
        print(f"Le corpus a bien été converti de {args.from_format} vers {args.to_format}")
    else:
        raise ValueError(f'format inconnu: {args.to_format}')

    
    


   