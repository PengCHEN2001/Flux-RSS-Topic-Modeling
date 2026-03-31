r"""
LDA Model
=========

Introduces Gensim's LDA model and demonstrates its use on a serialized corpus.
"""
import json
import argparse
import logging
from pathlib import Path

from datastructures import (
    Article,
    load_json,
    load_pickle,
    load_xml,
)

from gensim.corpora import Dictionary
from gensim.models import LdaModel, Phrases
from dataclasses import asdict
from nltk.stem.wordnet import WordNetLemmatizer
from datastructures import Topic  # ajouter Topic à l'import existant

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)


def load_corpus_format(input_format: str, input_file: str | Path) -> list[Article]:
    fonctions_load = {
        "xml": load_xml,
        "json": load_json,
        "pickle": load_pickle,
    }
    return fonctions_load[input_format](Path(input_file))


def build_docs(
    corpus: list[Article],
    attr: str,
    allowed_pos: set[str] | None = None,
) -> list[list[str]]:
    docs = []

    for article in corpus:
        article_doc = []

        for token in article.tokens:
            if allowed_pos is not None and token.pos not in allowed_pos:
                continue

            value = getattr(token, attr, "")
            if not value:
                continue

            value = value.strip().lower()

            # Remove words that are only one character.
            if len(value) <= 1:
                continue

            # Remove numbers, but not words that contain numbers.
            if value.isnumeric():
                continue

            article_doc.append(value)

        if article_doc:
            docs.append(article_doc)

    return docs


def topic_modeling_lda(
    corpus: list[Article],
    attr: str,
    allowed_pos: set[str] | None = None,
    num_topics: int = 10,
    chunksize: int = 2000,
    passes: int = 20,
    iterations: int = 400,
    no_below: int = 2,
    no_above: float = 0.5,
    use_bigrams: bool = False,
) -> list[Topic]:
    docs = build_docs(
        corpus=corpus,
        attr=attr,
        allowed_pos=allowed_pos,
    )
    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]
    if not docs:
        raise ValueError("Aucun document exploitable après filtrage.")

    if use_bigrams:
        bigram = Phrases(docs)
        for idx in range(len(docs)):
            for token in bigram[docs[idx]]:
                if "_" in token:
                    docs[idx].append(token)

    dictionary = Dictionary(docs)

    # Filter out words that occur less than no_below documents,
    # or more than no_above fraction of documents.
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)

    corpus_bow = [dictionary.doc2bow(doc) for doc in docs]
    corpus_bow = [doc for doc in corpus_bow if len(doc) > 0]

    if len(dictionary) == 0 or not corpus_bow:
        raise ValueError(
            "Le dictionnaire ou le corpus vectorisé est vide après filtrage."
        )

    print("Number of unique tokens: %d" % len(dictionary))
    print("Number of documents: %d" % len(corpus_bow))

    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    model = LdaModel(corpus=corpus_bow, id2word=dictionary, chunksize=chunksize, alpha="auto", eta="auto", iterations=iterations, num_topics=num_topics,passes=passes, eval_every=eval_every)

    top_topics = model.top_topics(corpus_bow)
    formated_topic = []

    for topic in top_topics:
        topic_representation = [{'value': word[1], 'proba': float(word[0])} for word in topic[0]]
        formated_topic.append(
        Topic(
            coherence_score=float(topic[1]),
            topic_representation=topic_representation
        )
    )
    return formated_topic


def main():
    parser = argparse.ArgumentParser(description="Topic modeling avec LDA")

    parser.add_argument(
    "--input-file", type=Path,
    help="Chemin vers le fichier de corpus en entrée.",
)
    parser.add_argument(
    "--output-file", type=Path,
    help="Chemin du fichier de sortie après topic modelling",
)
    parser.add_argument(
        "-f",
        "--format",
        dest="input_format",
        choices=("xml", "json", "pickle"),
        default="json",
        metavar="FORMAT",
        help="Format du corpus d'entrée : xml, json ou pickle (défaut : json).",
    )
    parser.add_argument(
        "-a",
        "--attribut",
        dest="attr",
        choices=("text", "lemme"),
        default="lemme",
        metavar="ATTRIBUT",
        help="Choisir entre les mot-formes ('text') ou les lemmes ('lemme').",
    )
    parser.add_argument(
        "--pos",
        nargs="*",
        default=None,
        help="Filtrer sur certaines catégories grammaticales, ex : --pos NOUN VERB ADJ",
    )
    parser.add_argument(
        "--num-topics",
        type=int,
        default=10,
        help="Nombre de topics (défaut : 10).",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=2000,
        help="Taille des blocs de traitement (défaut : 2000).",
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

    args = parser.parse_args()

    corpus = load_corpus_format(args.input_format, args.input_file)
    allowed_pos = set(args.pos) if args.pos else None

    topics = topic_modeling_lda(
        corpus=corpus,
        attr=args.attr,
        allowed_pos=allowed_pos,
        num_topics=args.num_topics,
        chunksize=args.chunksize,
        passes=args.passes,
        iterations=args.iterations,
        no_below=args.no_below,
        no_above=args.no_above,
        use_bigrams=args.bigrams,
    )

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(topic) for topic in topics], f, indent=4)

    avg_topic_coherence = sum([t.coherence_score for t in topics]) / args.num_topics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)

if __name__ == "__main__":
    main()
