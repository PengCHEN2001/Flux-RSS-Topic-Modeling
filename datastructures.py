#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from pathlib import Path

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
    #proposera les fonctions de sauvegarde  utilisera le format json (
    pass

def load_json(input_file: Path) -> list[Article]:
    #chargement en format json 
    pass


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
    parser.add_argument("input", help="Fichier source")
    parser.add_argument("output", help="Fichier cible")
    parser.add_argument("--from-format", choices=["json", "pickle", "xml"], required=True)#passer d'un format à un autre 
    parser.add_argument("--to-format", choices=["json", "pickle", "xml"], required=True)#passer d'un format à un autre 
    args = parser.parse_args()

    #charger le corpus
    #TODO appeler la fonction load correspondante
    corpus = []

    #sauvegarder dans le nouveau format
    #TODO:appelé la fonction save correspondante
    pass

   