#!/usr/bin/env python3

r"""
Bertopic Model
"""

import argparse
from pathlib import Path
from bertopic import BERTopic
from datastructures import suffix2loader


def load_corpus(fichier: Path, format: str, token_type: str = "lemma", pos_filter: list[str] | None = None) -> tuple[list[str], list[str]]:
    """
    Charge le corpus et extrait le texte, les dates et les sources (classes).
    Retourne listes : docs, timestamps
    """
    suffix = f".{format}"
    loader = suffix2loader[suffix]
    articles = loader(fichier)
    
    docs = []
    timestamps = []
    
    for article in articles:
        mots = [
            (t.lemma if token_type == "lemma" else t.form).lower()
            for sentence in article.analysis for t in sentence 
            if len(t.lemma) > 1 and not t.lemma.isnumeric()
            and (pos_filter is None or t.pos in pos_filter)
        ]
        
        if mots:
            docs.append(" ".join(mots))
            # On récupère les métadonnées (dates)
            date_jour = " ".join(article.date.split(" ")[2:4])
            timestamps.append(date_jour)

            
    print(f"Nombre de documents extraits : {len(docs)}")
    return docs, timestamps

def train_bertopic_model(docs: list[str]) -> BERTopic:
    """
    Initialise et entraîne le modèle BERTopic.
    """
    print("L'entraînement du modèle BERTopic (modèle français)...")
    topic_model = BERTopic(language="french")
    topic_model.fit_transform(docs)
    return topic_model


def save_viz(model: BERTopic, output_path: str, chart_type: str, docs: list[str], timestamps: list[str]) -> None:
    """
    Génère et sauvegarde la visualisation demandée en HTML.
    Intègre les graphiques temporels.
    """
    print(f"\nGénération de la visualisation : {chart_type}...")
    
    try:
        if chart_type == "2d":
            fig = model.visualize_topics()
        elif chart_type == "barchart":
            fig = model.visualize_barchart()
        elif chart_type == "hierarchy":
            fig = model.visualize_hierarchy()
        elif chart_type == "heatmap":
            fig = model.visualize_heatmap()
        elif chart_type == "terms":
            fig = model.visualize_term_rank()
        elif chart_type == "over_time":
            print("Calcul de l'évolution temporelle...")
            topics_over_time = model.topics_over_time(docs, timestamps)
            fig = model.visualize_topics_over_time(topics_over_time)                     
        else:
            print(f"Type '{chart_type}' inconnu. Utilisation par défaut du barchart.")
            fig = model.visualize_barchart()
        fig.write_html(output_path)
        print(f"Succès : Visualisation sauvegardée dans '{output_path}'")

    except Exception as e:
        print(f"Échec de la visualisation '{chart_type}' : {e}")
        if chart_type != "barchart":
            print("Tentative de repli sur le 'barchart'...")
            save_viz(model, output_path, "barchart", docs, timestamps) # pour éviter le cas où le corpus est trop petit, on utilise barchart qui peut etre utilisé pour tout les cas.



def main():
    """
    Point d'entrée principal du script en ligne de commande (CLI).
    """
    parser = argparse.ArgumentParser(
        description="Lancer BERTopic sur un corpus sérialisé",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_file", type=Path, help="Chemin vers le fichier du corpus analysé")
    parser.add_argument("-f", "--format", choices=["xml", "json", "pkl"], required=True, 
                        help="Format du corpus analysé (xml, json ou pkl)")
    
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Nom du fichier de sortie pour la visualisation")
    parser.add_argument("--chart", choices=["2d", "barchart", "hierarchy", "heatmap", "terms", "over_time"], 
                        default="2d", help="Type de graphique BERTopic à générer")
# <--- ex. 4c : nouvelles options en ligne de commande --->
    # ex. 4a : --token pour choisir entre lemmes et mot-formes
    parser.add_argument("--token", choices=["lemma", "form"], default="lemma",
                        help="Type de token : lemmes ou mot-formes (défaut: lemma)")
    
    # ex. 4b : --pos pour filtrer par catégories grammaticales (nargs="+" = plusieurs valeurs possibles)
    parser.add_argument("--pos", nargs="+", default=None, metavar="CAT",
                        help="Catégories grammaticales à conserver (ex: --pos NOUN VERB). Défaut : toutes.")

    args = parser.parse_args()

    docs, timestamps= load_corpus(args.input_file, args.format, args.token, args.pos)
    if not docs:
        print("Erreur : Aucun document valide trouvé. Arrêt du script.")
        return

    model = train_bertopic_model(docs)

    print("\nTop 10 des topics :")
    print(model.get_topic_info().head(10))
    print()

    if args.output:
        # On passe toutes les listes à save_viz
        save_viz(model, args.output, args.chart, docs, timestamps)
    else:
        print("\nAucune sortie de visualisation demandée. Utilisez -o pour générer un fichier HTML si vous voulez.")

if __name__ == "__main__":
    main()