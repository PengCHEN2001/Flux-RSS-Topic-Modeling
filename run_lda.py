import logging
import json
import argparse
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from pprint import pprint

# On garde le logging du script original pour voir l'entraînement
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

###############################################################################
# Data Loading (Exercice 2.2 & 3)
###############################################################################

def load_from_json(path, use_lemma=True, allowed_pos=['NOUN', 'ADJ']):
    """Charge le JSON et extrait les mots selon les critères (Ex 4.a & 4.b)."""
    with open(path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    docs = []
    for art in articles:
        # On extrait soit le lemme, soit la forme selon l'option choisie
        # On ne garde que les catégories grammaticales demandées
        words = [
            t['lemma'] if use_lemma else t['form']
            for t in art['tokens']
            if t['pos'] in allowed_pos
        ]
        # On n'ajoute le document que s'il n'est pas vide après filtrage
        if words:
            docs.append(words)
    return docs

# --- Configuration des options en ligne de commande (Exercice 3 & 4.c) ---
parser = argparse.ArgumentParser(description="Analyse de thématiques LDA sur corpus JSON")
parser.add_argument("input", help="Chemin du fichier JSON (ex: corpus_final.json)")
parser.add_argument("-n", "--num-topics", type=int, default=10, help="Nombre de thèmes à trouver")
parser.add_argument("--mode", choices=['lemme', 'forme'], default='lemme', help="Utiliser le lemme ou la forme brute")
parser.add_argument("--pos", nargs='+', default=['NOUN', 'ADJ'], help="Filtre POS (ex: NOUN ADJ VERB)")

args = parser.parse_args()

# Chargement effectif des données
is_lemma = (args.mode == 'lemme')
docs = load_from_json(args.input, use_lemma=is_lemma, allowed_pos=args.pos)

print(f"Number of documents loaded: {len(docs)}")

###############################################################################
# Pre-process and vectorize (Gensim Logic)
###############################################################################

# Create a dictionary representation of the documents.
dictionary = Dictionary(docs)

# Filter out words that occur in less than 5 documents, or more than 50% of the documents.
# On baisse 'no_below' car ton corpus est plus petit que celui de NIPS.
dictionary.filter_extremes(no_below=5, no_above=0.5)

# Bag-of-words representation of the documents.
corpus = [dictionary.doc2bow(doc) for doc in docs]

print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus))

###############################################################################
# Training LDA Model
###############################################################################

# Set training parameters from arguments.
num_topics = args.num_topics
chunksize = 2000
passes = 20
iterations = 400
eval_every = None

# Make an index to word dictionary.
temp = dictionary[0]
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

###############################################################################
# Results Output
###############################################################################

top_topics = model.top_topics(corpus)

# Average topic coherence
avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
print('Average topic coherence: %.4f.' % avg_topic_coherence)

# Affichage propre des thèmes trouvés
pprint(top_topics)
