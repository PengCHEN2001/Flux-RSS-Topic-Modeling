# Journal de Bord - Introduction à BERTopic
**Groupe 16 :** Peng CHEN, Myriam,Hulya

**Date :** 10 Avril 2026 

---
## Exercice 1 : Lecture et correction du code précédent
### Corrections - Peng CHEN: 
- Pour cette étape, j'ai fait la première correction pour les code des dernière séances et laissé mes collègues à verifier et tester. 
- J’ai repris et restructuré une grande partie du code, notamment dans analyzers.py, datastructures.py et run_lda.py. En m’inspirant du style de la correction fournie par le professeur, j’ai supprimé du code et des classes superflus afin de rendre l’architecture plus claire et lisible.
- Dans la version précédente, dans la classe Article, le champ token était utilisé comme clé, avec un type limité à list[Token]. J’ai modifié cette structure pour adopter une représentation plus adaptée —— analysis: list[list[Token]] = field(default_factory=list) Cela a nécessité une série d’ajustements cohérents dans le reste du code.
- Au passage, j’ai corrigé un bug dans la fonction load_xml de datastructures.py. L’ancienne version écrasait certaines variables (conflit de noms) et ciblait incorrectement les balises XML, ce qui produisait des listes vides. Ce problème est désormais corrigé en quelques lignes, et la désérialisation remplit correctement la structure list[list[Token]].
- Le code est désormais plus propre, plus cohérent et plus proche de standards professionnels, ce qui nous fournit une base solide pour la suite du TP.

## Exercice 2 : Topic Modeling
### Peng CHEN - exo 2.1  2.3


