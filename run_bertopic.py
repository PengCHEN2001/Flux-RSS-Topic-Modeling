#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups

# Charger les données d'exemple (corpus en anglais)
docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']

# Initialiser le modèle BERTopic
topic_model = BERTopic()

# Entraîner le modèle et extraire les topics
topics, probs = topic_model.fit_transform(docs)

# Afficher les 10 premiers topics trouvés
print("Top 10 des topics :")
print(topic_model.get_topic_info().head(10))

# Créer et sauvegarder la visualisation
fig = topic_model.visualize_topics()
fig.write_html("quickstart_viz.html")
print("\n La visualisation est sauvegardée dans quickstart_viz.html")