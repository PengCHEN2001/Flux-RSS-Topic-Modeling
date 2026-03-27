import stanza

# 1. Initialiser le pipeline pour le français
nlp = stanza.Pipeline(lang='fr', processors='tokenize,lemma,pos')

# 2. Analyser un texte d'exemple
doc = nlp("Le chat mange la souris.")

# 3. Parcourir les résultats
for sentence in doc.sentences:
    for word in sentence.words:
        print(f"Texte: {word.text} | Lemme: {word.lemma} | POS: {word.upos}")
