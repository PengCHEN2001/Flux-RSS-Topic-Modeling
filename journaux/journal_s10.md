# Journal de Bord - Introduction à BERTopic
#### Note： @ozenhulya72 -> arrêter le travail (absent)
**Groupe 16 :** Peng CHEN, Myriam,

**Date :** 10 Avril 2026 

Répartition du travail de ce TP:
- Peng fait la 1e correction du code précédent et l'exo2.1 - 2.3 
- Myriam fait l'exo 2.4 
- On se relit ce qu'on fait.

---
## Exercice 1 : Lecture et correction du code précédent
### Corrections - Peng CHEN: 
- J’ai repris et restructuré une grande partie du code, notamment dans analyzers.py, datastructures.py et run_lda.py. En m’inspirant du style de la correction fournie par le professeur, j’ai supprimé du code et des classes superflus afin de rendre l’architecture plus claire et lisible.
- Dans la version précédente, dans la classe Article, le champ token était utilisé comme clé, avec un type limité à list[Token]. J’ai modifié cette structure pour adopter une représentation plus adaptée —— analysis: list[list[Token]] = field(default_factory=list) Cela a nécessité une série d’ajustements cohérents dans le reste du code.
- Au passage, j’ai corrigé un bug dans la fonction load_xml de datastructures.py. L’ancienne version écrasait certaines variables (conflit de noms) et ciblait incorrectement les balises XML, ce qui produisait des listes vides. Ce problème est désormais corrigé en quelques lignes, et la désérialisation remplit correctement la structure list[list[Token]].
- Le code est désormais plus propre, plus cohérent et plus proche de standards professionnels, ce qui nous fournit une base solide pour la suite du TP.

## Exercice 2 : Topic Modeling
Utiliser la librairie BERTopic https://maartengr.github.io/BERTopic/
index.html pour effectuer du topic modeling.Suivre le quick start et appréhender la documentation fournie sur la page. Regarderer notamment l’API détaillée pour configurer les paramètres de BERTopic, appeler les fonctions correctement et faire des entraînement (fit) et des prédictions (transform).



### Peng CHEN - exo 2.1 ~ 2.3
#### Tâche :
1. essayez de créer un script qui fait tourner le quick start tel quel en suivant les instructions ;
2. le faire tourner sur vos données "en bricolant" le script. (on pourra choisir le format de données sérialisées
entre json, xml et pickle) ;
3. transformez ce script en une commande autonome :
(a) repérez les paramètres (les variables) du script qui mériteraient d’être des options de la commande
(b) rajoutez une option pour choisir le format d’un corpus qu’on donnera en argument
(ex : python run_bertopic.py -f xml Outputs/corpusA.xml)

#### Ce que j'ai fait: 
- exo 2.1 : Exécution réussie du script pour le quick start
- exo2.2 J'ai adapté du script pour charger notre propre données en frnaçais. 
- - Mais y a une problème rencontré : Lors de la génération de la visualisation 2D (`visualize_topics()`), le programme a planté (erreur UMAP) car le corpus de test était trop petit pour générer suffisamment de topics. 
- - Du coup j'ai basculé sur `visualize_barchart()` qui fonctionne parfaitement même avec peu de topics.
- - Observation clé : Il y a des résultats qui ont montré que les topics étaient saturés de mots vides ("le", "de", "et"). Cela confirme la nécessité d'un filtrage syntaxique pour la suite.(exo2.4)
- exo2.3 : J’ai refactorisé le script afin d’éliminer les valeurs codées en dur, et, en m’inspirant du style LDA, j’ai structuré le code par fonctionnalités, par exemple en fonctions suivante:
- - load_corpus() qui recevoit le corpus analysé sous format xml, json et pkl 
- - train_bertopic_model() qui entraine le moèdele
- - save_viz() pour sauvegarder le resultat de la visualisation.
- - Dans def main(): avec `argparse`, j'ai ajouté arguments pour lire le corpus analysé et spécifier son format avec l'option `-f` (xml, json, pkl).
- - Puis, création d'une option `-o` (optionnelle) pour sauvegarder le graphique HTML uniquement si l'utilisateur le demande.
- - Robustesse : avec try/except dans save_viz(), le script tente de générer la vue 2D par défaut, mais si la machine détecte un échec lié à un corpus trop petit, il bascule automatiquement sur la génération d'un barchart sans faire planter l'application.
- - Au final, le script `run_bertopic.py` est désormais un outil de traitement en ligne de commande robuste et modulaire. Il est prêt à recevoir les options de filtrage linguistique (Exo2.4).

---


