# Manuel utilisateur - Projet RSS & Topic Modeling

Ce projet permet de traiter un corpus de flux RSS, depuis la lecture des fichiers XML jusqu’à la génération de visualisations de topics (LDA et BERTopic).

La pipeline complète comprend les étapes suivantes : 
1. Lecture et parsing des flux RSS
2. Filtrage du corpus (date, source, catégories)
3. Sérialisation du corpus (XML, JSON, pickle)
4. Analyse morphosyntaxique (spaCy, stanza, trankit)
5. Topic modeling (LDA, BERTopic)
6. Visualisations interactives des résultats

Ce manuel explique comment utiliser chaque étape du pipeline via des commandes en ligne pas à pas, sans connaissance du fonctionnement interne.

## Architecture Globale du Projet


```text
DEPOT_GIT_PROJET/
│
├── [Branche : main] (Code Source)
│   │   # Le cœur du programme : scripts fonctionnels et autonomes
│   ├── README.md               <-- Manuel utilisateur
│   ├── rss_reader.py           <-- Script de lecture et de parsing des flux RSS
│   ├── rss_parcours.py         <-- Script pour filtrer et sauvegarder le corpus RSS
│   ├── datastructures.py       <-- Structures de données et (dé)sérialisation du corpus
│   ├── analyzers.py            <-- Script CLI pour enrichir le corpus avec une analyse morphosyntaxique
│   ├── run_lda.py              <-- Modélisation LDA & visualisation pyLDAvis
│   └── run_bertopic.py         <-- Modélisation BERTopic & graphiques interactifs
│
└── [Branche : doc] (Documentation & Résultats)
    │   # Tout ce qui concerne l'explication et l'affichage des résultats
    ├── README.md               <--  Manuel utilisateur
    ├── journaux/               <--  Journaux de bord hebdomadaires
    ├── rapport/                <--  Rapport final
    └── page_html/              <--  Dossier contenant l’ensemble des visualisations du projet
```

## Prérequis

- Python 3.10+
- Modules : `spacy`, `stanza`, `trankit`, `feedparser`, `python-dateutil`, `gensim`, `nltk`, `bertopic`
- Modèle spaCy français : `python3 -m spacy download fr_core_news_sm`
- Les fichiers XML RSS sont stockés dans votre dossier de corpus 

> **Note** : les chemins contenant des espaces doivent être entourés de guillemets. 
> Exemple : `"../2026/02/10/Blast -- articles.xml"`



## 1. Lire un flux RSS | `rss_reader.py`

Lit **un seul fichier XML** RSS et affiche les articles dans le terminal.

**Option disponible `-r`**: méthode de parsing du fichier RSS

**Trois méthodes disponibles :** `re`, `etree`, `feedparser`

```bash
python3 rss_reader.py fichier.xml -r re
python3 rss_reader.py fichier.xml -r etree
python3 rss_reader.py fichier.xml -r feedparser
```

**Exemple concret :**
```bash
python3 rss_reader.py ~/RSS_doc/2026/02/10/Blast--articles.xml -r feedparser
```

Pour les chemins avec espaces ou caractères spéciaux :
```bash
python3 rss_reader.py ~/RSS_doc/2026/02/10/mar.10\:26/Flux\ RSS\ -\ BFM\ BUSINESS\ -\ Consommation.xml -r etree
```

## 2. Parcourir un corpus et filtrer | `rss_parcours.py`

Parcourt un **dossier entier** de fichiers XML, applique des filtres, et peut sauvegarder le résultat.

### Utilisation de base

```bash
python3 rss_parcours.py -c /chemin/vers/dossier/ -m feedparser
```

### Choix du walker (`-w`)

Trois façons de parcourir l'arborescence de fichiers :

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -w glob      # par défaut
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -w os
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -w pathlib
```

### Filtrer par date (`--start`, `--end`)

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --start "2024-01-01"
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --end "2024-12-31"
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --start "2024-01-01" --end "2024-12-31"
```

### Filtrer par source (`-s`)

> **Note** : la source correspond au nom complet du fichier XML. Utiliser une sous-chaîne de certains fichiers.
> Exemple : `-s "Lib"` pour filtrer les fichiers Libération, `-s "Blast"` pour Blast.

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Blast
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Lib
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Blast Lib
```

### Filtrer par catégorie (`-cat`)

> La casse n'est pas importante : utiliser `Sport` ou `sport`.

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Sport
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Politique
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Sport Politique
```

### Sauvegarder le corpus (`--output-file`, `--output-format`)

Formats disponibles : `json`, `pickle`, `xml`

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --output-file corpus.json --output-format json
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --output-file corpus.pickle --output-format pickle
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --output-file corpus.xml --output-format xml
```

### Charger depuis un corpus déjà sérialisé (`--input-file`, `--input-format`)

```bash
python3 rss_parcours.py --input-file corpus.json --input-format json
python3 rss_parcours.py --input-file corpus.pickle --input-format pickle
```

### Combinaisons

```bash
# Charger un corpus sérialisé et filtrer par source
python3 rss_parcours.py --input-file corpus.json --input-format json -s lemonde

# Parcourir, filtrer et sauvegarder en une commande
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -w glob \
  --start "2024-01-01" -s blast -cat politique \
  --output-file corpus_filtre.json --output-format json
```

## 3. Structures de données et sérialisation | `datastructures.py`
Ce module fournit les fonctions de sérialisation et désérialisation du corpus.
Il n’est pas un programme exécutable indépendant, mais un module utilisé par les autres scripts du projet.

Il sert de couche centrale permettant de :
- représenter les articles RSS sous forme de dataclasses
- stocker les résultats d’analyse morphosyntaxique
- sauvegarder et recharger un corpus dans différents formats

Formats disponibles : `json`, `pickle`, `xml`

Ces fonctions sont utilisées est testés dans :
- rss_parcours.py (sauvegarde / chargement du corpus)
- analyzers.py (corpus enrichi)
- run_lda.py
- run_bertopic.py

## 4. Analyser morphosyntaxiquement le corpus | `analyzers.py`

Enrichit chaque article avec une analyse morphosyntaxique (forme, lemme, POS) en utilisant différents outils NLP.
Chaque article est complété par un champ `analysis` contenant des tokens organisés par phrases.

**Analyseurs disponibles :** `spacy`, `stanza`, `trankit`  
**Formats supportés :** `json`, `pickle`, `xml`


### Syntaxe générale
```bash
python3 analyzers.py <input_file> <output_file> -a <analyzer> [--shuffle]
```

### Avec spaCy

```bash
python3 analyzers.py corpus.json corpus_analyse.json -a spacy
python3 analyzers.py corpus.xml corpus_analyse.xml -a spacy
python3 analyzers.py corpus.pkl corpus_analyse.pkl -a spacy
```

### Avec Stanza

```bash
python3 analyzers.py corpus.json corpus_analyse.xml -a stanza
python3 analyzers.py corpus.pkl corpus_analyse.xml -a stanza
```
> Stanza est très gourmand en mémoire. Il est conseillé de tester sur un sous-ensemble du corpus. Pour les grands corpus, traiter par lots de 500 articles maximum.

### Avec Trankit

```bash
python3 analyzers.py corpus.json corpus_analyse.json -a trankit
```

> **Attention** : Trankit nécessite Python 3.10 et le serveur de modèles doit être accessible. Non installable sur Apple Silicon dans les conditions standards.

### Option `--shuffle`
Permet de réduire le corpus pour tester rapidement la pipeline :
```bash
python3 analyzers.py corpus.json corpus_test.json -a spacy --shuffle
```

### Pipeline complète : de XML brut à corpus analysé
```bash
# Étape 1 : construire le corpus
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --output-file corpus.json --output-format json

# Étape 2 : enrichir avec analyse morphosyntaxique
python3 analyzers.py corpus.json corpus_analyse.json -a spacy
```

## 5. Topic modeling LDA | `run_lda.py`

Effectue une modélisation thématique sur un corpus déjà analysé (tokens requis).

### Syntaxe minimale

```bash
python3 run_lda.py --input-file corpus_analyse.json --output-file topics.json
```

### Toutes les options

```bash
python3 run_lda.py \
  --input-file corpus_analyse.json \   # corpus en entrée (avec tokens)
  --output-file topics.json \          # fichier de sortie JSON
  -f json \                            # format : json, pickle ou xml (défaut : json)
  -a lemme \                           # attribut : "lemme" ou "text" (défaut : lemme)
  --pos NOUN VERB ADJ \               # filtrer par catégories grammaticales
  --num-topics 10 \                    # nombre de topics (défaut : 10)
  --passes 20 \                        # tours d'entraînement (défaut : 20)
  --iterations 400 \                   # itérations internes (défaut : 400)
  --no-below 2 \                       # supprimer termes < N documents (défaut : 2)
  --no-above 0.5 \                     # supprimer termes > X% des docs (défaut : 0.5)
  --bigrams                            # activer les bigrammes
```

### Exemples

```bash
# Sur les lemmes, nouns et verbes seulement, 15 topics
python3 run_lda.py --input-file corpus_analyse.json --output-file topics.json \
  -a lemme --pos NOUN VERB --num-topics 15

# Depuis un pickle, sortie JSON, avec bigrammes
python3 run_lda.py --input-file corpus_analyse.pickle --output-file topics.json \
  -f pickle --bigrams

# Mots-formes (non lemmatisés), tous POS
python3 run_lda.py --input-file corpus_analyse.json --output-file topics.json \
  -a text --num-topics 5 --passes 10
```

### Format de la sortie

La sortie est un fichier JSON contenant une liste de topics, chacun avec :
- `coherence_score` : score de cohérence du topic
- `topic_representation` : liste de mots avec leur probabilité (`value`, `proba`)

---

## Pipeline complète de bout en bout

```bash
# 1. Collecter le corpus depuis les XML
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -w glob \
  --output-file corpus_brut.json --output-format json

# 2. Analyser morphosyntaxiquement
python3 analyzers.py corpus_brut.json corpus_analyse.json \
  --from-format json --to-format json --analyzer spacy

# 3. Lancer le topic modeling
python3 run_lda.py --input-file corpus_analyse.json --output-file topics.json \
  -a lemme --pos NOUN VERB ADJ --num-topics 10 --bigrams

```
# Ajouter ici le manuel pour les points 6 et 7 de l'exercice de la fiche Rendu Final

# Ajouter ici le manuel pour les points 2.1, 2, 3a, b de la fiche d'introduction à BERTopic

# Commandes | Exercice 2.4 (fiche d'introduction à BERTopic)

## 4a | Choisir entre lemmes et mot-formes (`--token`)

```bash
python run_bertopic.py -f json corpus_analyse.json --token lemma
python run_bertopic.py -f json corpus_analyse.json --token form
```

## 4b | Filtrer les catégories grammaticales (`--pos`)

```bash
python run_bertopic.py -f json corpus_analyse.json --pos NOUN VERB
python run_bertopic.py -f json corpus_analyse.json --pos NOUN
```

## 4c | Combiner les deux options

```bash
python run_bertopic.py -f json corpus_analyse.json --token lemma --pos NOUN VERB -o topics.html
```

