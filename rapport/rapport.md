## Myriam BEN HADJ SGHAIER : Rapport sur l'ensemble des fonctionnalités attendues pour les points 1 à 5 de l'exercice 2

**Groupe 16** — Myriam, Peng, Hulya (absente)

**Date** : 6 avril 2026

## Répartition des tâches et conventions 

Ce rapport a été rédigé après test effectif par Myriam BHS (points 1 à 5) de l'ensemble de la pipeline sur un corpus RSS personnel (`donnees/`). Chaque point a été testé individuellement et les résultats observés sont décrits ci-dessous.

**Les membres du groupe se sont organisés de la manière suivante :**
- Répartition des points par exercice 
- Création d'une branche NP-exN-sN (Np = initiales Nom-Prénom)
- Message de commit à chaque partie pushée
- Création d'un tag-fin : nous nous sommes mis d'accord pour que chacun fasse plusieurs points d'un exercice (ex2 1,2,3 par exemple), en sachant que nous n'étions que deux. Une fois les points finis, un tag Np-ex-fin est crée. Si un membre fini les derniers points du dernier exercice de la fiche, il met un tag-fiche-fin directement. 
- Chacun relit le code de l'autre et crée un tag ex-relu après la relecture.
- Une fois la fiche terminée et le code relu, la personne ayant fait les derniers exercices se charge de merge vers le main et de créer le tag de fin de la fiche.

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


############### PENG ################ EX 2 POINTS 1, 2, 3a, b


## Myriam BEN HADJ SGHAIER : Rapport sur les fonctionnalités BERTopic — Exercice 2 (points 6 et 7)

**Groupe 16** — Myriam, Peng, Hulya (absente)

**Date** : 17 avril 2026

## Point 4 | Amélioration du script — options `--token` et `--pos` (2.4)

**Attendu** : améliorer `run_bertopic.py` pour pouvoir choisir entre les mots-formes et les lemmes, filtrer sur les catégories grammaticales et déclarer ces deux options en ligne de commande.

**Obtenu** :

### 4a | Choix entre lemmes et mots-formes (`--token`)

Dans `load_corpus()`, la construction de chaque document s'est faite par une expression conditionnelle sur chaque token :

```python
(t.lemma if token_type == "lemma" else t.form)
for sentence in article.analysis for t in sentence
```

L'option `--token` est déclarée dans le parseur avec deux valeurs possibles :

```python
parser.add_argument("--token", choices=["lemma", "form"], default="lemma",
                    help="Type de token : lemmes ou mot-formes (défaut: lemma)")
```

Utilisation :

```
python run_bertopic.py -f json corpus_analyse.json --token lemma
python run_bertopic.py -f json corpus_analyse.json --token form
```

### 4b | Filtrage par catégories grammaticales (`--pos`)

Le filtre POS est intégré dans la même compréhension de liste que le choix du token, via une condition supplémentaire :

```python
and (pos_filter is None or t.pos in pos_filter)
```

Quand `--pos` n'est pas spécifié, `pos_filter` vaut `None` et tous les tokens sont conservés. L'option accepte plusieurs valeurs grâce à `nargs="+"` :

```python
parser.add_argument("--pos", nargs="+", default=None, metavar="CAT",
                    help="Catégories grammaticales à conserver (ex: --pos NOUN VERB). Défaut : toutes.")
```

Utilisation :

```
python run_bertopic.py -f json corpus_analyse.json --pos NOUN VERB
python run_bertopic.py -f json corpus_analyse.json --pos NOUN
```

### 4c | Combinaison des deux options en ligne de commande

Les deux options étant indépendantes dans `argparse` et transmises ensemble à `load_corpus()`, elles peuvent être utilisées simultanément :

```
python run_bertopic.py -f json corpus_analyse.json --token lemma --pos NOUN VERB -o topics.html
```

Testé sur `corpus_analyse.json` (3 207 documents) — fonctionne correctement.

## Bilan

| Sous-point | Objectif | Statut |
|------------|----------|--------|
| 4a | Option `--token` (lemma / form) dans `load_corpus()` et argparse | OK |
| 4b | Option `--pos` avec `nargs="+"` et filtre dans la compréhension de liste | OK |
| 4c | Combinaison des deux options en CLI | OK |

**Conclusion** : objectif atteint. Les deux options sont implémentées de manière concise dans la fonction `load_corpus()`, dans une seule compréhension de liste, et exposées en ligne de commande via `argparse`.