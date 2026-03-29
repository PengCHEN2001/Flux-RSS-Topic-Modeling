#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path

from gensim.corpora import Dictionary
from gensim.models import LdaModel, Phrases

from datastructures import Article, load_json, load_pickle, load_xml

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s",
    level=logging.INFO,
)

# Lemmatisations très fréquentes et peu informatives pour LDA
STOP_LEMMAS = {
    "être", "avoir", "faire", "aller", "dire", "venir", "savoir",
    "pouvoir", "falloir", "voir", "vouloir",
    "un", "une", "le", "la", "les",
    "du", "de", "des", "d’", "l’", "s’", "qu’", "c’",
    "ce", "cette", "ces", "celui", "celle",
    "et", "ou", "mais", "donc", "or", "ni", "car",
    "en", "dans", "sur", "sous", "par", "pour", "avec", "sans",
    "à", "au", "aux",
    "il", "elle", "on", "nous", "vous", "ils", "elles",
    "je", "tu", "me", "te", "se",
    "que", "qui", "quoi", "dont", "où",
    "tout", "très", "plus", "moins", "aussi",
    "son", "sa", "ses", "notre", "votre", "leur", "leurs",
    "ne", "pas", "plusieurs", "certain", "après", "depuis",
    "premier", "nouveau", "an", "année", "semaine",
    "france", "français", "paris",
    "vidéo", "décryptage", "bfm", "bfmtv"
}


def load_corpus_format(input_format: str, input_file: str | Path) -> list[Article]:
    loaders = {
        "xml": load_xml,
        "json": load_json,
        "pickle": load_pickle,
    }
    return loaders[input_format](Path(input_file))


def extract_documents(
    corpus: list[Article],
    unit: str = "lemme",
    pos_filter: set[str] | None = None,
    min_len: int = 2,
    remove_stop_lemmas: bool = True,
) -> list[list[str]]:
    """
    Transforme un corpus d'articles en liste de documents tokenisés
    pour LDA. Chaque document correspond à un article.
    """
    docs: list[list[str]] = []

    for article in corpus:
        doc_tokens: list[str] = []

        for token in article.tokens:
            if pos_filter is not None and token.pos not in pos_filter:
                continue

            value = token.lemme if unit == "lemme" else token.forme
            if value is None:
                continue

            value = value.strip().lower()
            if len(value) < min_len:
                continue
            if value.isnumeric():
                continue

            if remove_stop_lemmas and unit == "lemme" and value in STOP_LEMMAS:
                continue

            doc_tokens.append(value)

        if doc_tokens:
            docs.append(doc_tokens)

    return docs


def topic_modeling_lda(
    docs: list[list[str]],
    num_topics: int = 10,
    passes: int = 20,
    iterations: int = 400,
    chunksize: int = 2000,
    no_below: int = 2,
    no_above: float = 0.5,
    add_bigrams: bool = False,
):
    """
    Entraîne un modèle LDA sur une liste de documents tokenisés.
    """
    if not docs:
        raise ValueError("Aucun document exploitable après filtrage.")

    docs = [doc for doc in docs if doc]

    if add_bigrams:
        bigram = Phrases(docs, min_count=5, threshold=10)
        for idx in range(len(docs)):
            for token in bigram[docs[idx]]:
                if "_" in token:
                    docs[idx].append(token)

    docs = [doc for doc in docs if doc]

    if not docs:
        raise ValueError("Aucun document exploitable après ajout des bigrammes.")

    dictionary = Dictionary(docs)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)

    corpus_bow = [dictionary.doc2bow(doc) for doc in docs]
    corpus_bow = [doc for doc in corpus_bow if len(doc) > 0]

    if len(dictionary) == 0:
        raise ValueError("Le dictionnaire est vide après filtrage.")

    if not corpus_bow:
        raise ValueError(
            "Le corpus bag-of-words est vide après filtrage. "
            "Essayez de réduire no_below, augmenter no_above, "
            "ou modifier le filtrage POS."
        )

    print(f"Number of unique tokens: {len(dictionary)}")
    print(f"Number of documents: {len(corpus_bow)}")

    model = LdaModel(
        corpus=corpus_bow,
        id2word=dictionary,
        chunksize=chunksize,
        alpha="auto",
        eta="auto",
        iterations=iterations,
        num_topics=num_topics,
        passes=passes,
        eval_every=None,
    )

    top_topics = model.top_topics(corpus_bow)
    avg_topic_coherence = sum(t[1] for t in top_topics) / num_topics
    print(f"Average topic coherence: {avg_topic_coherence:.4f}")

    print("\nTopics:")
    for i, topic in model.print_topics(num_topics=num_topics, num_words=10):
        print(f"Topic {i}: {topic}")

    return model, dictionary, corpus_bow, top_topics


def main():
    parser = argparse.ArgumentParser(description="Topic modeling avec LDA")

    parser.add_argument(
        "input_file",
        help="Chemin vers le fichier de corpus en entrée.",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="input_format",
        choices=("xml", "json", "pickle"),
        default="json",
        help="Format du corpus d'entrée (défaut : json).",
    )
    parser.add_argument(
        "--unit",
        choices=("forme", "lemme"),
        default="lemme",
        help="Unité textuelle à utiliser pour LDA (défaut : lemme).",
    )
    parser.add_argument(
        "--pos",
        nargs="*",
        default=None,
        help="Filtrer sur certaines catégories grammaticales, ex: --pos NOUN VERB ADJ",
    )
    parser.add_argument(
        "--num-topics",
        type=int,
        default=10,
        help="Nombre de topics LDA (défaut : 10).",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=20,
        help="Nombre de passes d'entraînement (défaut : 20).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=400,
        help="Nombre d'itérations internes (défaut : 400).",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=2000,
        help="Taille des blocs de traitement (défaut : 2000).",
    )
    parser.add_argument(
        "--no-below",
        type=int,
        default=2,
        help="Supprime les termes présents dans moins de N documents (défaut : 2).",
    )
    parser.add_argument(
        "--no-above",
        type=float,
        default=0.5,
        help="Supprime les termes présents dans plus de cette proportion de documents (défaut : 0.5).",
    )
    parser.add_argument(
        "--bigrams",
        action="store_true",
        help="Active l'ajout de bigrammes.",
    )
    parser.add_argument(
        "--keep-stop-lemmas",
        action="store_true",
        help="Conserve les lemmes-outils fréquents au lieu de les filtrer.",
    )

    args = parser.parse_args()

    corpus = load_corpus_format(args.input_format, args.input_file)

    pos_filter = set(args.pos) if args.pos else None

    docs = extract_documents(
        corpus=corpus,
        unit=args.unit,
        pos_filter=pos_filter,
        remove_stop_lemmas=not args.keep_stop_lemmas,
    )

    topic_modeling_lda(
        docs=docs,
        num_topics=args.num_topics,
        passes=args.passes,
        iterations=args.iterations,
        chunksize=args.chunksize,
        no_below=args.no_below,
        no_above=args.no_above,
        add_bigrams=args.bigrams,
    )


if __name__ == "__main__":
    main()