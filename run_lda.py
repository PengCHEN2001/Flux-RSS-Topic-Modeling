import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import io
import os.path
import re
import tarfile
import json
import smart_open
import argparse
from datastructures import Topic, Token, Article,load_json, load_pickle, load_xml, save_json, save_pickle, save_xml
from pathlib import Path
from dataclasses import asdict
# Lemmatize the documents.
from nltk.stem.wordnet import WordNetLemmatizer

# Compute bigrams.
from gensim.models import Phrases

# Remove rare and common tokens.
from gensim.corpora import Dictionary

# Train LDA model.
from gensim.models import LdaModel

# Download the WordNet data
from nltk import download
# download('wordnet')

# Set training parameters.

def run_lda(articles:list[Article], num_topics:int, passes:int) ->list[Topic]:
    docs= [[token.lemme for token in article.tokens if token.lemme is not None] for article in articles]

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 1] for doc in docs]

    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    bigram = Phrases(docs, min_count=20)
    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=20, no_above=0.5)

    # Bag-of-words representation of the documents.
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    chunksize = 2000
    iterations = 400
    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    # Make an index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=chunksize,
        alpha='auto',
        eta='auto',
        iterations=iterations,
        num_topics=num_topics,
        passes=passes,
        eval_every=eval_every
    )

    top_topics = model.top_topics(corpus)
    formated_topic=[]

    #
    for topic in top_topics:
        topic_representation=[{'value':word[1], 'proba': float(word[0])} for word in topic[0]]
        formated_topic.append(
            Topic(coherence_score= float(topic[1]),
            topic_representation= topic_representation
            ))
    return formated_topic

def filter_pos(articles:list[Article], use_lemma=True, allowed_pos=['NOUN', 'ADJ']):

    docs = []
    for art in articles:
        # On extrait soit le lemme, soit la forme selon l'option choisie
        # On ne garde que les catégories grammaticales demandées
        words = [
            t.lemme if use_lemma else t.form
            for t in art.tokens
            if t.pos in allowed_pos
        ]
        # On n'ajoute le document que s'il n'est pas vide après filtrage
        if words:
            docs.append(words)
    return docs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lire un fichier sérialisé et les regroupes par topic."
    )
    parser.add_argument(
        "--num-topics", type=int, help="Nombre de topics  "
    )
    parser.add_argument(
        "--input-file", type=Path, help="Chemin vers un corpus deja sérialisé ( articles incluant tokens)"
    )
    parser.add_argument(
        "--passes", type=int, help=""
    )
    parser.add_argument(
        "--input-format",
        choices=["xml", "json", "pickle"],
        help="Format du corpus sérialisé en entree",
    )
    parser.add_argument(
        "--output-file", type=Path,
        help="Chemin du fichier de sortie apres topic modelling "
    )
    parser.add_argument("--mode",
        choices=['lemme','forme'],
        default='lemme', help="Utiliser le lemme ou la forme brute"
    )
    parser.add_argument("--pos",
        nargs='+', default=['NOUN', 'ADJ'],
        help="Filtre POS (ex: NOUN ADJ VERB)"
    )

    args = parser.parse_args()
    if args.input_format == 'json':
        articles=load_json(args.input_file)
    elif args.input_format == 'xml':
         articles=load_xml(args.input_file)
    elif args.input_format == 'pickle':
         articles=load_pickle(args.input_file)
    is_lemme = (args.mode == 'lemme')
    docs = filter_pos(articles, use_lemma=is_lemme, allowed_pos=args.pos)
    topics= run_lda(articles, args.num_topics, args.passes)
    with open(args.output_file,'w', encoding='utf-8') as f:
         json.dump([asdict(topic) for topic in topics],f,indent=4)

# Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t.coherence_score for t in topics]) / args.num_topics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)



if __name__ == "__main__":
    main()

