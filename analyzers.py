from random import shuffle
from pathlib import Path
from datastructures import Token, Article, suffix2loader, suffix2writer

import sys


def load_spacy():
    import spacy
    return spacy.load("fr_core_news_md")


def load_stanza():
    import stanza
    stanza.download("fr")  # téléchargé qu'une fois, peut se commenter
    return stanza.Pipeline("fr", processors="tokenize,pos,lemma")


def load_trankit():
    import trankit
    return trankit.Pipeline('french', gpu=False)


def analyze_spacy(parser, article: Article) -> Article:
    result = parser( (article.title or "" ) + "\n" + (article.description or ""))
    output = []
    for sentence in result.sents:
        output.append([])
        for token in sentence:
            if token.text.strip():
                output[-1].append(Token(token.text, token.lemma_, token.pos_))
    article.analysis = output
    return article


def analyze_stanza(parser, article: Article) -> Article:
    result = parser( (article.title or "" ) + "\n" + (article.description or ""))
    output = []
    for sent in result.sentences:
        output.append([])
        for token in sent.words:
            output[-1].append(Token(token.text, token.lemma, token.upos))
    article.analysis = output
    return article


def analyze_trankit(parser, article: Article) -> Article:
    result = parser( (article.title or "" ) + "\n" + (article.description or ""))
    output = []
    for sentence in result['sentences']:
        output.append([])
        for token in sentence['tokens']:
            if 'expanded' not in token.keys():
                token['expanded'] = [token]
            for w in token['expanded']:
                output[-1].append(Token(w['text'], w['lemma'], w['upos']))
    article.analysis = output
    return article



name_to_analyzer = {
    "spacy": (load_spacy, analyze_spacy),
    "stanza": (load_stanza, analyze_stanza),
    "trankit": (load_trankit, analyze_trankit),
}


def main(input_file, output_file, analyzer=None, do_shuffle=False):
    #DEMO_HARD_LIMIT = 100 # pour faire une démonstration au besoin
    #print(f"WARNING: this is a demo with {DEMO_HARD_LIMIT} documents only", file=sys.stderr)

    input_file = Path(input_file)
    output_file = Path(output_file)

    load_corpus = suffix2loader[input_file.suffix]
    save_corpus = suffix2writer[output_file.suffix]
    load_model, analyze = name_to_analyzer[analyzer]

    print(f"Chargement depuis {input_file}...")
    corpus = load_corpus(input_file)
    print(f"{len(corpus)} articles chargés.")

    corpus = load_corpus(input_file)
    model = load_model()

    if do_shuffle:
        indices = [9440, 7443, 6777, 4201, 27678, 8816, 13747, 21223, 16438, 14424, 29111, 16457, 11620, 1360, 18719, 23975, 27716, 24301, 31779, 26076, 24047, 6282, 17214, 30185, 30482, 11391, 29680, 15543, 5218, 26781, 27536, 28199, 28653, 20726, 28965, 7976, 17580, 18785, 13406, 10468, 13095, 30955, 1890, 6362, 27698, 19690, 30977, 182, 792, 26501, 27039, 18459, 28985, 10159, 4149, 20056, 10738, 5422, 4710, 24151, 25087, 11675, 11602, 30911, 5480, 17311, 30567, 7862, 26436, 27145, 7156, 18832, 24464, 24447, 20451, 91, 4070, 12184, 14475, 5257, 17306, 22670, 24046, 23664, 32058, 30927, 1795, 1017, 19171, 30362, 12847, 27614, 16614, 5995, 29633, 15548, 12485, 11045, 21034, 23628]
        corpus = [corpus[idx] for idx in indices]
    #corpus = corpus[:DEMO_HARD_LIMIT]  # commenter pour traiter tout le corpus
    print(f"Analyse en cours avec {analyzer}...")
    corpus = [analyze(model, item) for item in corpus]
    print("Analyse terminée.")

    print(f"Sauvegarde vers {output_file}...")
    save_corpus(corpus, output_file)
    print("Fait !")



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input file, a serialized corpus.")
    parser.add_argument("output_file", help="Output file")
    parser.add_argument("-a", "--analyzer", choices=sorted(name_to_analyzer.keys()))
    parser.add_argument("--shuffle", action="store_true")

    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_file=args.output_file,
        analyzer=args.analyzer,
        do_shuffle=args.shuffle
    )

