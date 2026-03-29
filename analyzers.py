'''écrivez une fonction qui prend en argument un Article et le
retourne, enrichi avec le résultat de l’analyse.
Chaque analyseur pourra avoir sa propre fonction d’analyse.
Vous pourrez avoir besoin d’écrire des fonctions annexes (par exemple pour charger le modèle), et de modifier le
fichier datastructures.py, en particulier de modifier et d’ajouter des dataclasses.
On attend notamment une dataclass Token qui servira d’interface commune pour stocker les résultats différents analyseurs (chaque token
ne stocke qu’une analyse, mais on doit pouvoir utiliser le type Token avec chaque outil).
Proposez une fonction principale (main) dans le fichier analyzers.py afin que celui-ci puisse être utilisé comme
une commande bash qui charge un corpus précédemment sauvegardé, l’analyse avec votre outils et sauvegarde
le résultat.
Les fonctions de (dé)sérialisation devront être mises à jour pour intégrer les analyses (les lire ou les
écrire quand elles sont présentes)'''
import sys
import argparse
from pathlib import Path
from datastructures import Token, Article,load_json, load_pickle, load_xml, save_json, save_pickle, save_xml
from trankit import Pipeline


#spacy
def analyzer_spacy(article: Article) -> Article:
    raise NotImplementedError("Analyseur spaCy non implémenté")






#stanza

def analyzer_stanza(article: Article) -> Article:
    raise NotImplementedError("Analyseur stanza non implémenté")







#trankit
p = Pipeline('french')

def analyzer_trankit(article: Article) -> Article:
    for sentence in p(article.content)['sentences']:
        tokens_phrase = []
        for token in sentence['tokens']:
            tok = Token(
                forme = token.get('text'),
                lemme = token.get('lemma'),
                pos   = token.get('upos'),
            )
            tokens_phrase.append(tok)
        article.tokens.extend(tokens_phrase)
    return article




#main


def main():
    parser = argparse.ArgumentParser(description="Analyse d'un corpus")
    parser.add_argument("input",
                        type=Path,
                        help="Fichier corpus en entrée")
    parser.add_argument("output",
                        type=Path,
                        help="Fichier corpus en sortie")
    parser.add_argument("--from-format",
                        choices=["json", "pickle", "xml"] ,
                        required=True)
    parser.add_argument("--to-format",
                        choices=["json", "pickle", "xml"],
                        required=True)
    # Ajout arg --analyzer
    parser.add_argument("--analyzer",
                        choices=["spacy", "stanza", "trankit"],
                        required=True)
    args = parser.parse_args()

    # 1. Chargement fichier json xml pickle
    loaders = {"json": load_json, "xml": load_xml, "pickle": load_pickle}
    savers  = {"json": save_json, "xml": save_xml, "pickle": save_pickle}
    # Ajout dic analysers
    analyzers = {
        "spacy": analyzer_spacy,
        "stanza": analyzer_stanza,
        "trankit": analyzer_trankit
    }

    print(f"Chargement depuis {args.input}...")
    corpus = loaders[args.from_format](args.input)
    print(f"{len(corpus)} articles chargés.")

    # 2. Analyse morpho syntaxique
    print("Analyse en cours...")
    corpus_analyse = [analyzers[args.analyzer](article) for article in corpus]
    print("Analyse terminée.")

    # 3. Sauvegarde dans un nouveau fichier
    print(f"Sauvegarde vers {args.output}...")
    savers[args.to_format](corpus_analyse, args.output)
    print("Fait !")


if __name__ == "__main__":
    main()
