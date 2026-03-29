#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

import stanza

from datastructures import Token, Article, load_json, load_pickle, load_xml, save_json, save_pickle, save_xml


#spacy
def analyzer_spacy(article: Article) -> Article:
    raise NotImplementedError("Analyseur spaCy non implémenté")


#stanza
_stanza_pipeline = None

def get_stanza_pipeline():
    global _stanza_pipeline
    if _stanza_pipeline is None:
        _stanza_pipeline = stanza.Pipeline(lang='fr', processors='tokenize,lemma,pos', use_gpu=False)
    return _stanza_pipeline

def analyzer_stanza(article: Article) -> Article:
    if not article.content:
        return article

    nlp = get_stanza_pipeline()
    doc = nlp(article.content)

    enriched_tokens = []

    for sentence in doc.sentences:
        for word in sentence.words:
            new_token = Token(
                forme=word.text,
                lemme=word.lemma,
                pos=word.upos
            )
            enriched_tokens.append(new_token)

    article.tokens = enriched_tokens
    return article


#trankit
_trankit_pipeline = None

def get_trankit_pipeline():
    global _trankit_pipeline
    if _trankit_pipeline is None:
        from trankit import Pipeline
        _trankit_pipeline = Pipeline('french')
    return _trankit_pipeline

def analyzer_trankit(article: Article) -> Article:
    if not article.content:
        return article

    p = get_trankit_pipeline()
    article.tokens = []

    for sentence in p(article.content)['sentences']:
        for token in sentence['tokens']:
            tok = Token(
                forme=token.get('text'),
                lemme=token.get('lemma'),
                pos=token.get('upos'),
            )
            article.tokens.append(tok)
    return article


#main
def main():
    parser = argparse.ArgumentParser(description="Analyse d'un corpus")
    parser.add_argument("input",
                        type=Path,
                        help="Fichier corpus en entrée")
    parser.add_argument("output",
                        type=Path,
                        help="Fichier corpus en sortie")
    parser.add_argument("--from-format",
                        choices=["json", "pickle", "xml"],
                        required=True)
    parser.add_argument("--to-format",
                        choices=["json", "pickle", "xml"],
                        required=True)
    parser.add_argument("--analyzer",
                        choices=["spacy", "stanza", "trankit"],
                        required=True)
    args = parser.parse_args()

    loaders = {"json": load_json, "xml": load_xml, "pickle": load_pickle}
    savers  = {"json": save_json, "xml": save_xml, "pickle": save_pickle}
    analyzers = {
        "spacy": analyzer_spacy,
        "stanza": analyzer_stanza,
        "trankit": analyzer_trankit
    }

    print(f"Chargement depuis {args.input}...")
    corpus = loaders[args.from_format](args.input)
    print(f"{len(corpus)} articles chargés.")

    print("Analyse en cours...")
    corpus_analyse = [analyzers[args.analyzer](article) for article in corpus]
    print("Analyse terminée.")

    print(f"Sauvegarde vers {args.output}...")
    savers[args.to_format](corpus_analyse, args.output)
    print("Fait !")


if __name__ == "__main__":
    main()
