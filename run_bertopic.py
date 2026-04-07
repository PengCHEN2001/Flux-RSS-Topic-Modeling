r"""
Bertopic Model

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bertopic import BERTopic
from datastructures import load_xml 


def main():
    fichier_entree = "corpus-rich.xml" 
    print(f"Chargement des données depuis : {fichier_entree}")
    
  
    articles = load_xml(fichier_entree) 
    
    docs = []
    for art in articles:
        # Extraire les lemmes (mots) de chaque phrase, en filtrant la ponctuation/nombres
        mots = [
            t.lemma for phrase in art.analysis for t in phrase 
            if len(t.lemma) > 1 and not t.lemma.isnumeric()
        ]
        if mots:
            docs.append(" ".join(mots))
    
    print(f"{len(docs)} documents prêts.")

    # Initialiser BERTopic 
    topic_model = BERTopic(language="multilingual")# ou french
    
    # Entraîner le modèle
    topics, probs = topic_model.fit_transform(docs)

    print("\nTop 10 des topics :")
    print(topic_model.get_topic_info().head(10))

    #topic_model.visualize_topics().write_html("resultat_viz.html") # pour le corpus gros 
    topic_model.visualize_barchart().write_html("resultat_viz.html") # pour le corpus petit si y a que qq topics retirés
    print("\n Terminé ! La visualisation est sauvegardée.")

if __name__ == "__main__":
    main()