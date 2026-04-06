# Manuel utilisateur (pour les points 1 à 5 de l'exercice 2)

Ce manuel explique comment utiliser les scripts du projet pas à pas, sans connaissance du fonctionnement interne.

## Prérequis

- Python 3.10+
- Modules : `spacy`, `stanza`, `feedparser`, `python-dateutil`, `gensim`, `nltk`
- Modèle spaCy français : `python3 -m spacy download fr_core_news_sm`
- Les fichiers XML RSS sont stockés dans votre dossier de corpus 

> **Note** : les chemins contenant des espaces doivent être entourés de guillemets. 
> Exemple : `"../2026/02/10/Blast -- articles.xml"`

## 1. Lire un flux RSS — `rss_reader.py`

Lit **un seul fichier XML** RSS et affiche les articles dans le terminal.

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

## 2. Parcourir un corpus et filtrer — `rss_parcours.py`

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

> **Note** : la source correspond au chemin complet du fichier XML. Utiliser une sous-chaîne de certains fichiers.
> Exemple : `-s "Lib"` pour filtrer les fichiers Libération, `-s "Blast"` pour Blast.

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Blast
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Lib
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser -s Blast Lib
```

### Filtrer par catégorie (`-cat`)

> **Note** : le filtre catégorie fonctionne uniquement avec `-m etree` ou `-m re`. Avec `-m feedparser`, les catégories ne sont pas extraites sur certains corpus (`categories : []`).  
> La casse est importante : utiliser `Sport` et non `sport`.

```bash
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Sport
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Politique
python3 rss_parcours.py -c ~/RSS_doc/ -m etree -cat Sport Politique
```

### Sauvegarder le corpus (`--output-file`, `--output-format`)

Formats disponibles : `json`, `pickle`, `xml`

> **Note** : le format pickle génère l'extension `.pickle` (et non `.pkl`).

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

## 3. Convertir entre formats — `datastructures.py`

Convertit un corpus sérialisé d'un format vers un autre.

Formats disponibles : `json`, `pickle`, `xml`

```bash
python3 datastructures.py -in json -out pickle corpus.json
python3 datastructures.py -in json -out xml corpus.json
python3 datastructures.py -in pickle -out json corpus.pickle
python3 datastructures.py -in pickle -out xml corpus.pickle
python3 datastructures.py -in xml -out json corpus.xml
python3 datastructures.py -in xml -out pickle corpus.xml
```

> Le fichier de sortie est créé automatiquement dans le même dossier avec la nouvelle extension.

## 4. Analyser morphosyntaxiquement le corpus — `analyzers.py`

Enrichit chaque article avec des tokens (forme, lemme, POS) en utilisant un analyseur NLP.

**Analyseurs disponibles :** `spacy`, `stanza`, `trankit`
**Formats d'entrée/sortie :** `json`, `pickle`, `xml`

### Syntaxe générale

```bash
python3 analyzers.py <input> <output> --from-format <format> --to-format <format> --analyzer <outil>
```

### Avec spaCy

```bash
python3 analyzers.py corpus.json corpus_analyse.json --from-format json --to-format json --analyzer spacy
python3 analyzers.py corpus.pkl corpus_analyse.pkl --from-format pickle --to-format pickle --analyzer spacy
python3 analyzers.py corpus.pkl corpus_analyse.json --from-format pickle --to-format json --analyzer spacy
```

### Avec Stanza

```bash
python3 analyzers.py corpus.json corpus_analyse.json --from-format json --to-format json --analyzer stanza
python3 analyzers.py corpus_pour_stanza.json corpus_final.json --from-format json --to-format json --analyzer stanza
```

> Stanza est très gourmand en mémoire. Pour les grands corpus, traiter par lots de 500 articles maximum.

### Avec Trankit

```bash
python3 analyzers.py corpus.json corpus_analyse.json --from-format json --to-format json --analyzer trankit
```

> **Attention** : Trankit nécessite Python 3.10 et le serveur de modèles doit être accessible. Non installable sur Apple Silicon dans les conditions standards.

### Pipeline complète : de XML brut à corpus analysé

```bash
# Étape 1 : construire le corpus
python3 rss_parcours.py -c ~/RSS_doc/ -m feedparser --output-file corpus.json --output-format json

# Étape 2 : analyser
python3 analyzers.py corpus.json corpus_analyse.json --from-format json --to-format json --analyzer spacy
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

