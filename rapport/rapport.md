## Rapport 

**Groupe 16** — Myriam, Peng, Hulya 
**Date** : 6 avril 2026

## Myriam BEN HADJ SGHAIER : Rapport sur l'ensemble des fonctionnalités attendues pour les points 1 à 5 de l'exercice 2

## Répartition des tâches de rédaction

Ce rapport a été rédigé après test effectif de l'ensemble de la pipeline sur un corpus RSS personnel (`donnees/`). Chaque point a été testé individuellement et les résultats observés sont décrits ci-dessous.

## Point 1| Lire un flux RSS unique (re, etree, feedparser)

**Attendu** : le script `rss_reader.py` doit pouvoir lire un fichier XML RSS selon trois méthodes au choix : expressions régulières (`re`), parsing XML (`etree`) et bibliothèque dédiée (`feedparser`). Pour chaque article, les champs suivants doivent être extraits : identifiant, source, titre, contenu, date, catégories.

**Obtenu** : les trois méthodes sont implémentées et fonctionnelles. La commande `-r` permet de sélectionner la méthode. Les articles sont correctement extraits avec tous les champs attendus.

Une différence de comportement est à noter avec `re`, le champ contenu s'affiche sous la clé `description` au lieu de `content`. Il s'agit d'un alias de compatibilité défini dans la dataclass `Article` (`@property description`), non d'un bug.

**Conclusion** : objectif atteint ici.

## Point 2 | Parcourir une arborescence et appliquer des filtres

**Attendu** : le script `rss_parcours.py` doit parcourir un dossier contenant des fichiers XML RSS selon trois méthodes (`os`, `pathlib`, `glob`), puis permettre de filtrer les articles par date (`--start`, `--end`), par source (`-s`) et par catégorie (`-cat`). Il doit également permettre de sauvegarder et de charger un corpus sérialisé.

**Obtenu** : le parcours d'arborescence fonctionne avec les trois walkers. La sérialisation et la désérialisation sont opérationnelles. Les filtres par date et par source fonctionnent correctement.

Deux points de vigilance ont été identifiés lors des tests :

- **Filtre par source** : la valeur du champ `source` correspond au chemin complet du fichier XML (ex : `/Users/.../Libération - Sports.xml`). Le filtre fonctionne par sous-chaîne, donc `-s "Lib"` fonctionne mais `-s "Libération"` échoue si la casse ne correspond pas exactement. Ce comportement n'est pas documenté et peut induire l'utilisateur en erreur.

- **Filtre par catégorie** : avec la méthode `feedparser`, les catégories ne sont pas extraites sur ce corpus (`categories : []`), rendant le filtre `-cat` non operationnel. Le filtre fonctionne correctement avec `-m etree` ou `-m re`, à condition de respecter la casse des catégories telles qu'elles apparaissent dans les fichiers XML (ex : `Sport` et non `sport`). Ce comportement dépend du corpus et de la méthode choisie, et mériterait d'être signalé à l'utilisateur.

- **Extension pickle** : le format pickle génère l'extension `.pickle` et non `.pkl`. Les commandes du manuel doivent en tenir compte.

**Conclusion** : objectif majoritairement atteint. Les filtres par date et source fonctionnent. Le filtre par catégorie est conditionné au choix de la méthode et à la casse. Ces limitations ne constituent pas des bugs mais des comportements à impérativement documenter. 

## Point 3 | Sérialiser et désérialiser selon trois formats

**Attendu** : le script `datastructures.py` doit permettre de convertir un corpus entre les formats `json`, `pickle` et `xml` dans les deux sens.

**Obtenu** : les six conversions possibles ont été testées et fonctionnent toutes correctement. Les dataclasses `Article` et `Token` sont correctement sérialisées et reconstruites.

Un point mineur : l'extension générée pour le format pickle est `.pickle` et non `.pkl`. Ce n'est pas un bug mais il faut en être informé pour enchaîner les commandes correctement.

**Conclusion** : objectif atteint. 

## Point 4 | Analyse morphosyntaxique (spaCy, stanza, trankit)

**Attendu** : le script `analyzers.py` doit enrichir les articles du corpus avec une analyse morphosyntaxique (forme, lemme, POS) en utilisant au choix spaCy, stanza ou trankit.

**Obtenu** :

- **spaCy** : fonctionne parfaitement. 3 469 articles analysés en quelques secondes avec le modèle `fr_core_news_sm`. Les tokens sont correctement stockés dans les objets `Article`. 

- **stanza** : fonctionne correctement. Le pipeline `tokenize, mwt, pos, lemma` est chargé automatiquement pour le français. L'analyse est plus lente que spaCy et plus gourmande en mémoire (738 Mo observés), mais les résultats sont de meilleure qualité linguistique. 

- **trankit** : le code est implémenté et structurellement correct dans `analyzers.py`. Cependant, trankit n'a pas pu être installé dans de bonnes conditions : le serveur hébergeant les modèles pré-entraînés était inaccessible au moment des tests, rendant l'installation impossible sur Apple Silicon. 

**Conclusion** : objectif atteint pour spaCy et stanza. Trankit est implémenté mais non testable en raison d'un problème idépendant du code.

## Point 5 | Topic modeling LDA (gensim)

**Attendu** : le script `run_lda.py` doit effectuer une modélisation thématique LDA sur un corpus préalablement analysé, avec des options configurables (nombre de topics, passes, filtrage POS, bigrammes, etc.) et produire une sortie JSON structurée.

**Obtenu** : le script fonctionne correctement. Deux configurations ont été testées :

- **Sans filtrage POS** : 10 topics, 20 passes, sur les lemmes. Cohérence moyenne : -3.31. Les topics contiennent encore beaucoup de mots grammaticaux (être, avoir, en, et…), ce qui reflète l'absence de filtrage.

- **Avec filtrage POS (NOUN, VERB, ADJ) et bigrammes** : cohérence moyenne : -7.34. La qualité des topics est moins bonne avec cette configuration sur ce corpus, ce qui est attendu : le filtrage POS réduit le vocabulaire disponible et les bigrammes introduisent du bruit sur un corpus de taille modeste (3 464 documents).

La sortie JSON est bien structurée avec `coherence_score` et `topic_representation` (liste de paires mot/probabilité) pour chaque topic, conformément à la dataclass `Topic` définie dans `datastructures.py`.

**Conclusion** : objectif atteint. 

## Bilan général

| Point | Objectif | Statut |
|-------|----------|--------|
| 1 | Lecture RSS (re, etree, feedparser) | OK |
| 2 | Arborescence + filtres | OK (comportements à documenter) |
| 3 | Sérialisation xml / pickle / json | OK |
| 4 | Analyse morphosyntaxique | spaCy + stanza / /!\ trankit (externe) |
| 5 | Topic modeling LDA | OK |

Le rapport actuel couvre l'ensemble des fonctionnalités attendues pour les points 1 à 5. Les limitations identifiées (comportement du filtre source, catégories avec feedparser, trankit) ne constituent pas un bug bloquant.

## Points d'amélioration suggérés

- Normaliser la valeur du champ `source` pour n'afficher que le nom du fichier et non le chemin complet, ce qui rendrait le filtre `-s` plus intuitif.
- Ajouter un avertissement explicite lorsque feedparser ne récupère pas de catégories, plutôt que de retourner silencieusement une liste vide.
- Documenter l'extension `.pickle` générée par le format pickle dans les messages d'aide des scripts.
