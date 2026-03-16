#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    #proposera les fonctions de sauvegarde 
    pass

def load_xml(input_file: Path) -> list[Article]:
    #chargement en XML (on peut utiliser etree pour le créer)
    pass

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
    ##proposera les fonctions de sauvegarde 
    pass

def load_pickle(input_file: Path) -> list[Article]:
    #chargement en format pickle
    pass





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

    
    


   