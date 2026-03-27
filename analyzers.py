#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
import stanza

# On importe les structures de données définies ensemble dans datastructures.py [cite: 42, 43]
from datastructures import Article, Token, load_json, save_json, load_xml, save_xml, load_pickle, save_pickle

def get_stanza_pipeline():
    #Initialise et charge en mémoire le modèle linguistique Stanza
    return stanza.Pipeline(lang='fr', processors='tokenize,lemma,pos', use_gpu=False)

def analyze_with_stanza(article: Article, nlp) -> Article:
    #Prend un objet Article, analyse son texte brut, et remplit sa liste de tokens
    #Arguments :article (Article) : L'objet contenant le texte à analyser. nlp : Le pipeline Stanza déjà chargé (pour éviter de le recharger 100 fois).
    #Retourne :Article : L'objet enrichi avec une liste d'objets Token[cite: 40].
    # Sécurité : si l'article est vide, on ne fait rien
    if not article.content:
        return article

    # Lancement de l'analyse Stanza sur le contenu de l'article
    doc = nlp(article.content)

    # Liste temporaire pour stocker nos objets Token unifiés
    enriched_tokens = []

    # Stanza organise le résultat en phrases (sentences), puis en mots (words)
    for sentence in doc.sentences:
        for word in sentence.words:
            # Création d'une instance de la dataclass Token commune au groupe
            # word.text  -> Forme originale du mot (ex: "mangeait")
            # word.lemma -> Forme canonique (ex: "manger")
            # word.upos  -> Catégorie grammaticale universelle (ex: "VERB")
            new_token = Token(
                form=word.text,
                lemma=word.lemma,
                pos=word.upos
            )
            enriched_tokens.append(new_token)

    # On injecte la liste de tokens dans l'attribut prévu de l'article
    article.tokens = enriched_tokens
    return article

def main():

    #Usage : python analyzers.py input.json output.json --format json

    parser = argparse.ArgumentParser(description="Enrichissement morphosyntaxique avec Stanza (Rôle 2)")
    parser.add_argument("input", type=Path, help="Chemin du fichier corpus d'entrée")
    parser.add_argument("output", type=Path, help="Chemin du fichier de sortie enrichi")
    parser.add_argument("--format", choices=["json", "xml", "pickle"], default="json",
                        help="Format de sérialisation utilisé")

    args = parser.parse_args()

    # Mapping des fonctions de chargement/sauvegarde de datastructures.py [cite: 45]
    loaders = {"json": load_json, "xml": load_xml, "pickle": load_pickle}
    savers = {"json": save_json, "xml": save_xml, "pickle": save_pickle}

    try:
        # 1. Chargement des données brutes
        print(f"[*] Lecture du fichier {args.input}...")
        corpus = loaders[args.format](args.input)

        # 2. Préparation de l'analyseur
        print("[*] Chargement du modèle Stanza (Français)...")
        nlp = get_stanza_pipeline()

        # 3. Boucle de traitement sur tous les articles du corpus [cite: 44]
        print(f"[*] Analyse morphosyntaxique de {len(corpus)} articles en cours...")
        for article in corpus:
            analyze_with_stanza(article, nlp)

        # 4. Exportation du corpus enrichi (incluant les nouveaux tokens) [cite: 8]
        print(f"[*] Sauvegarde des résultats vers {args.output}...")
        savers[args.format](corpus, args.output)
        print("[+] Succès : Le corpus a été enrichi et sauvegardé.")

    except Exception as e:
        # Gestion d'erreur basique pour le débogage
        print(f"[!] Erreur critique : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
