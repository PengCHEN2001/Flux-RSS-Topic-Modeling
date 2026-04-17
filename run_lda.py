#!/usr/bin/env python3

r"""
LDA Model
=========

Introduces Gensim's LDA model and demonstrates its use.

"""

import argparse
import logging
import pyLDAvis.gensim_models as ldavis

from gensim.corpora import Dictionary
from gensim.models import LdaModel, Phrases
from pyLDAvis import save_html
from pathlib import Path
from pprint import pprint
from typing import TypeAlias

from datastructures import suffix2loader, Token

Document: TypeAlias = list[str]
DocCorpus: TypeAlias = list[Document]
BoWDocument: TypeAlias = list[tuple[int, int]]
BoWCorpus: TypeAlias = list[BoWDocument]


###############################################################################
# The purpose of this tutorial is to demonstrate how to train and tune an LDA model.
#
# In this tutorial we will:
#
# * Load input data.
# * Pre-process that data.
# * Transform documents into bag-of-words vectors.
# * Train an LDA model.
#
# This tutorial will **not**:
#
# * Explain how Latent Dirichlet Allocation works
# * Explain how the LDA model performs inference
# * Teach you all the parameters and options for Gensim's LDA implementation
#
# If you are not familiar with the LDA model or how to use it in Gensim, I (Olavur Mortensen)
# suggest you read up on that before continuing with this tutorial. Basic
# understanding of the LDA model should suffice. Examples:
#
# * `Introduction to Latent Dirichlet Allocation <http://blog.echen.me/2011/08/22/introduction-to-latent-dirichlet-allocation>`_
# * Gensim tutorial: :ref:`sphx_glr_auto_examples_core_run_topics_and_transformations.py`
# * Gensim's LDA model API docs: :py:class:`gensim.models.LdaModel`
#
# I would also encourage you to consider each step when applying the model to
# your data, instead of just blindly applying my solution. The different steps
# will depend on your data and possibly your goal with the model.
#
# Data
# ----
#


# Handle our own corpus
def load_corpus(
    file: Path, use_lemma: bool, pos_whitelist: frozenset
) -> DocCorpus:
    """
    Extract documents from a serialized corpus.
    """

    loader = suffix2loader[file.suffix]
    corpus = loader(file)
    # Use the lemma or the word-form

    def get_field(tok: Token) -> str:
        return tok.lemma if use_lemma else tok.text

    # Our data is already tokenized and lemmatized, so jump straight to a list of tokens per document
    docs = [
        [
            # Try to make this nested list comprehension slightly less confusing by abusing indentation...
            get_field(token)
            for sentence in article.analysis
            for token in sentence
            # NOTE: Skip numeric tokens and 1-character tokens, like the original code.
            if len(get_field(token)) > 1 and not get_field(token).isnumeric() and token.pos in pos_whitelist
        ]
        for article in corpus
    ]

    ###############################################################################
    # So we have a list of documents, where each document is a list of tokens.
    # Make sure it's in the expected format.
    #
    print(f"Number of documents: {len(docs)}")
    print(f"First 25 tokens of the first doc: {docs[0][:25]}")

    return docs


###############################################################################
# Pre-process and vectorize the documents
# ---------------------------------------
#
# As part of preprocessing, we will:
#
# * Compute bigrams.
# * Compute a bag-of-words representation of the data.

###############################################################################
# We find bigrams in the documents. Bigrams are sets of two adjacent words.
# Using bigrams we can get phrases like "machine_learning" in our output
# (spaces are replaced with underscores); without bigrams we would only get
# "machine" and "learning".
#
# Note that in the code below, we find bigrams and then add them to the
# original data, because we would like to keep the words "machine" and
# "learning" as well as the bigram "machine_learning".
#
# .. Important::
#     Computing n-grams of large dataset can be very computationally
#     and memory intensive.
#


# Compute bigrams.
def compute_bigrams(docs: DocCorpus, min_count: int = 20) -> None:
    """
    Enrich a DocCorpus with bigrams.
    """

    # Add bigrams to docs
    bigram = Phrases(docs, min_count=min_count)
    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if "_" in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)


###############################################################################
# We remove rare words and common words based on their *document frequency*.
# Below we remove words that appear in less than 20 documents or in more than
# 50% of the documents. Consider trying to remove words only based on their
# frequency, or maybe combining that with this approach.
#


# Remove rare and common tokens.
def trim_corpus(
    docs: DocCorpus, no_below: int = 5, no_above: float = 0.5
) -> tuple[BoWCorpus, Dictionary]:
    """
    Remove rare and common tokens from the corpus
    """

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur in less than `no_below` documents, or in more than `no_above`% of the documents.
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)

    ###############################################################################
    # Finally, we transform the documents to a vectorized form. We simply compute
    # the frequency of each word, including the bigrams.
    #

    # Bag-of-words representation of the documents.
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    ###############################################################################
    # Let's see how many tokens and documents we have to train on.
    #

    print(f"Number of unique tokens: {len(dictionary)}")
    print(f"Number of documents: {len(corpus)}")

    return corpus, dictionary


###############################################################################
# Training]d
# --------
#
# We are ready to train the LDA model. We will first discuss how to set some of
# the training parameters.
#
# First of all, the elephant in the room: how many topics do I need? There is
# really no easy answer for this, it will depend on both your data and your
# application. I have used 10 topics here because I wanted to have a few topics
# that I could interpret and "label", and because that turned out to give me
# reasonably good results. You might not need to interpret all your topics, so
# you could use a large number of topics, for example 100.
#
# ``chunksize`` controls how many documents are processed at a time in the
# training algorithm. Increasing chunksize will speed up training, at least as
# long as the chunk of documents easily fit into memory. I've set ``chunksize =
# 2000``, which is more than the amount of documents, so I process all the
# data in one go. Chunksize can however influence the quality of the model, as
# discussed in Hoffman and co-authors [2], but the difference was not
# substantial in this case.
#
# ``passes`` controls how often we train the model on the entire corpus.
# Another word for passes might be "epochs". ``iterations`` is somewhat
# technical, but essentially it controls how often we repeat a particular loop
# over each document. It is important to set the number of "passes" and
# "iterations" high enough.
#
# I suggest the following way to choose iterations and passes. First, enable
# logging (as described in many Gensim tutorials), and set ``eval_every = 1``
# in ``LdaModel``. When training the model look for a line in the log that
# looks something like this::
#
#    2016-06-21 15:40:06,753 - gensim.models.ldamodel - DEBUG - 68/1566 documents converged within 400 iterations
#
# If you set ``passes = 20`` you will see this line 20 times. Make sure that by
# the final passes, most of the documents have converged. So you want to choose
# both passes and iterations to be high enough for this to happen.
#
# We set ``alpha = 'auto'`` and ``eta = 'auto'``. Again this is somewhat
# technical, but essentially we are automatically learning two parameters in
# the model that we usually would have to specify explicitly.
#


# Train LDA model.
def train_lda_model(
    corpus: BoWCorpus, dictionary: Dictionary, hyperparameters: dict[str, int | None]
) -> LdaModel:
    """
    Train an LDA model
    """

    # Make an index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    return LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=hyperparameters["chunksize"],
        alpha="auto",
        eta="auto",
        iterations=hyperparameters["iterations"],
        num_topics=hyperparameters["num_topics"],
        passes=hyperparameters["passes"],
        eval_every=hyperparameters["eval_every"],
    )


###############################################################################
# We can compute the topic coherence of each topic. Below we display the
# average topic coherence and print the topics in order of topic coherence.
#
# Note that we use the "Umass" topic coherence measure here (see
# :py:func:`gensim.models.ldamodel.LdaModel.top_topics`), Gensim has recently
# obtained an implementation of the "AKSW" topic coherence measure (see
# accompanying blog post, https://rare-technologies.com/what-is-topic-coherence/).
#
# If you are familiar with the subject of the articles in this dataset, you can
# see that the topics below make a lot of sense. However, they are not without
# flaws. We can see that there is substantial overlap between some topics,
# others are hard to interpret, and most of them have at least some terms that
# seem out of place. If you were able to do better, feel free to share your
# methods on the blog at https://rare-technologies.com/lda-training-tips/ !
#


def print_topic_coherence(corpus: BoWCorpus, model: LdaModel) -> None:
    """
    Print topic coherence data on the console
    """

    top_topics = model.top_topics(corpus)

    # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t[1] for t in top_topics]) / model.num_topics
    print(f"Average topic coherence: {avg_topic_coherence:.4f}.")
    pprint(top_topics)


def save_html_viz(output: Path, lda: LdaModel, corpus: BoWCorpus, dictionary: Dictionary) -> None:
    """Dump pyLDAvis HTML visualization to disk"""

    vis_data = ldavis.prepare(lda, corpus, dictionary)
    save_html(vis_data, output.as_posix())
    print(f"Succès : Visualisation sauvegardée dans '{output}'")


###############################################################################
# Things to experiment with
# -------------------------
#
# * ``no_above`` and ``no_below`` parameters in ``filter_extremes`` method.
# * Adding trigrams or even higher order n-grams.
# * Consider whether using a hold-out set or cross-validation is the way to go for you.
# * Try other datasets.
#
# Where to go from here
# ---------------------
#
# * Check out a RaRe blog post on the AKSW topic coherence measure (https://rare-technologies.com/what-is-topic-coherence/).
# * pyLDAvis (https://pyldavis.readthedocs.io/en/latest/index.html).
# * Read some more Gensim tutorials (https://github.com/RaRe-Technologies/gensim/blob/develop/tutorials.md#tutorials).
# * If you haven't already, read [1] and [2] (see references).
#
# References
# ----------
#
# 1. "Latent Dirichlet Allocation", Blei et al. 2003.
# 2. "Online Learning for Latent Dirichlet Allocation", Hoffman et al. 2010.
#


def main():
    """
    Main CLI entry point
    """

    parser = argparse.ArgumentParser(
        "Run an LDA model on a serialized RSS corpus",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("input_file", type=Path, help="Serialized input corpus")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--use-lemma",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use lemmatized words instead of word-forms",
    )
    parser.add_argument(
        "--pos",
        nargs="*",
        choices=UPOS,
        help="Only select the specified POS tags",
    )
    # For compute_bigrams
    parser.add_argument(
        "--bigrams",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Compute and append bigrams to the token list",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=20,
        help="Ignore all words and bigrams with total collected count lower than this value.",
    )
    # For trim_corpus
    parser.add_argument(
        "--no-below",
        type=int,
        default=5,
        help="Filter out words that occur in less this amount of documents",
    )
    parser.add_argument(
        "--no-above",
        type=float,
        default=0.5,
        help="Filter out words that occur in more than this percentage of documents",
    )
    # For train_lda_model
    parser.add_argument(
        "--num-topics",
        type=int,
        default=10,
        help="The number of requested latent topics to be extracted from the training corpus",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=2000,
        help="Number of documents to be used in each training chunk",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=20,
        help="Number of passes through the corpus during training",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=400,
        help="Maximum number of iterations through the corpus when inferring the topic distribution of a corpus",
    )
    parser.add_argument(
        "--eval_every",
        type=int,
        help="Log perplexity is estimated every that many updates. Setting this to one slows down training by ~2x",
    )
    parser.add_argument(
        "-c", "--chart", 
        type=Path, 
        help="Chemin et nom du fichier pour sauvegarder la visualisation HTML (ex: lda_viz.html)"
    )

    args = parser.parse_args()

    # Setup logging facilities
    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    # Shove hyperparams in a dict to keep the sig sane...
    params = ["num_topics", "chunksize", "passes", "iterations", "eval_every"]
    hyperparameters = {param: getattr(args, param) for param in params}

    # Load the corpus data
    docs = load_corpus(
        args.input_file,
        args.use_lemma,
        frozenset(args.pos or UPOS),
    )

    # Data cleanup
    if args.bigrams:
        compute_bigrams(docs, args.min_count)
    corpus, dictionary = trim_corpus(docs, args.no_below, args.no_above)

    # Train the model
    model = train_lda_model(corpus, dictionary, hyperparameters)

    # Display raw results
    print_topic_coherence(corpus, model)
    if args.chart:
        save_html_viz(args.chart, model, corpus, dictionary)



UPOS = frozenset(
    {
        "ADJ",
        "ADP",
        "ADP+DET",  # MWT, c.f., analyzers.py
        "ADP+PRON",  # Ditto
        "ADV",
        "AUX",
        "CONJ",
        "CCONJ",
        "DET",
        "INTJ",
        "NOUN",
        "NUM",
        "PART",
        "PRON",
        "PROPN",
        "PUNCT",
        "SCONJ",
        "SYM",
        "VERB",
        "X",
    }
)

if __name__ == "__main__":
    main()
