# datastructures.py

from dataclasses import dataclass, field
import pickle
from pathlib import Path
import argparse

@dataclass
class Article:
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)

#Exercice 2 : Fonctions R3 (Pickle)

def save_pickle(corpus: list[Article], output_file: Path) -> None:
    #Sauvegarde la liste d'articles au format binaire pickle.
    with open(output_file, 'wb') as f: #wb : write binary
        pickle.dump(corpus, f)

def load_pickle(input_file: Path) -> list[Article]:
    #Charge et retourne une liste d'articles depuis un fichier pickle.
    with open(input_file, 'rb') as f: #rb : read binary
        return pickle.load(f)


#Mis à jour du main pour utiliser les fonctions de l'exercice 2.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertir un corpus d'un format à un autre.")
    
    # On utilise type=Path pour que argparse convertisse directement les strings en objets Path
    parser.add_argument("input_file", type=Path, help="Fichier source")
    parser.add_argument("output_file", type=Path, help="Fichier cible")
    
    parser.add_argument("--format-in", choices=["xml", "json", "pickle"], required=True, help="Format du fichier source")
    parser.add_argument("--format-out", choices=["xml", "json", "pickle"], required=True, help="Format du fichier cible")

    args = parser.parse_args()

    # 1. Chargement du corpus
    corpus = []
    if args.format_in == "pickle":
        corpus = load_pickle(args.input_file)
    elif args.format_in == "json":
        pass # r2: Appeler load_json(args.input_file)
    elif args.format_in == "xml":
        pass # r1: Appeler load_xml(args.input_file)

    # 2. Sauvegarde du corpus
    if args.format_out == "pickle":
        save_pickle(corpus, args.output_file)
    elif args.format_out == "json":
        pass # r2: Appeler save_json(corpus, args.output_file)
    elif args.format_out == "xml":
        pass # r1: Appeler save_xml(corpus, args.output_file)

    print(f"Conversion terminée : {args.input_file} ({args.format_in}) -> {args.output_file} ({args.format_out})")