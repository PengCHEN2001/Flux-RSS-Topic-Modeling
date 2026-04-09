#!/usr/bin/env python3

r"""
Bertopic Model
"""

import argparse
from pathlib import Path
from bertopic import BERTopic
from datastructures import suffix2loader

def load_corpus(fichier: Path, format: str, token_type: str = "lemma", pos_filter: list[str] | None = None) -> list[str]:
    """
    Charge et prépare le corpus pour BERTopic.
    Convertit les objets Article en une liste de chaînes de caractères.
    """
    
    suffix = f".{format}"
    loader = suffix2loader[suffix]
    articles = loader(fichier)
    
    docs = []
    for article in articles:
        # Extraction basique des lemmes

        # ex. 4a : choix entre lemme (t.lemma) et mot-forme (t.form)
        mots = [
            (t.lemma if token_type == "lemma" else t.form)
            for sentence in article.analysis for t in sentence 
            if len(t.lemma) > 1 and not t.lemma.isnumeric()
        # ex. 4b : filtre sur les catégories grammaticales (None = tout garder) 
            and (pos_filter is None or t.pos in pos_filter)
        ]
        if mots:
            docs.append(" ".join(mots))
            
    print(f"Nombre de documents extraits : {len(docs)}")
    return docs

def train_bertopic_model(docs: list[str]) -> BERTopic:
    """
    Initialise et entraîne le modèle BERTopic sur les documents fournis.
    """
    print("L'entraînement du modèle BERTopic (modèle français)...")
    topic_model = BERTopic(language="french")
    topics, probs = topic_model.fit_transform(docs)
    return topic_model

def save_viz(model: BERTopic, output_path: str, chart_type: str) -> None:
    """
    Génère et sauvegarde la visualisation en HTML.
    Si chart_type est '2d' mais échoue (corpus trop petit), on passe au barchart.
    """
    print(f"\nGénération de la visualisation (Type demandé : {chart_type})...")
    
    if chart_type == "barchart":
        fig = model.visualize_barchart()
        print("💡 Succès : Diagramme en barres (barchart) généré.")
        
    else:
        try:
            fig = model.visualize_topics()
            print("Succès : Vue 2D générée.")
        except Exception:
            print("Échec : Impossible de générer la vue 2D (corpus probablement trop petit / pas assez de topics).")
            print("Basculement automatique sur le diagramme en barres...")
            fig = model.visualize_barchart()
            
    fig.write_html(output_path)
    print(f"Sauvegarde de la visualisation dans : {output_path}")

def main():
    """
    Point d'entrée principal du script en ligne de commande (CLI).
    """
    parser = argparse.ArgumentParser(
        description="Lancer BERTopic sur un corpus sérialisé",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # --- Exercice 2.3 : Options de la commande ---
    parser.add_argument("input_file", type=Path, help="Chemin vers le fichier du corpus analysé")
    parser.add_argument("-f", "--format", choices=["xml", "json", "pkl"], required=True, 
                        help="Format du corpus analysé (xml, json ou pkl)")
    
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Nom du fichier de sortie pour la visualisation")
    
    parser.add_argument("--chart", choices=["2d", "barchart"], default="2d",
                        help="Type de visualisation (défaut: 2d). Si '2d' échoue, repli sur 'barchart'.")

# <--- ex. 4c : nouvelles options en ligne de commande --->
    # ex. 4a : --token pour choisir entre lemmes et mot-formes
    
    parser.add_argument("--token", choices=["lemma", "form"], default="lemma",
                        help="Type de token : lemmes ou mot-formes (défaut: lemma)")
    
    # ex. 4b : --pos pour filtrer par catégories grammaticales (nargs="+" = plusieurs valeurs possibles)
    parser.add_argument("--pos", nargs="+", default=None, metavar="CAT",
                        help="Catégories grammaticales à conserver (ex: --pos NOUN VERB). Défaut : toutes.")

    args = parser.parse_args()


    docs = load_corpus(args.input_file, args.format, args.token, args.pos)

    if not docs:
        print("Erreur : Aucun document valide trouvé. Arrêt du script.")
        return

    model = train_bertopic_model(docs)

    print()
    print("Top 10 des topics :")
    print(model.get_topic_info().head(10))
    print()

    if args.output:
        save_viz(model, str(args.output), args.chart)
    else:
        print("\n Aucune visualisation demandée. Vous pouvez utiliser '-o xxx.html' pour générer un graphe.")


if __name__ == "__main__":
    main()