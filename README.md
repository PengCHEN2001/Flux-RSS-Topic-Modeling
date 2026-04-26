# Flux RSS Topic Modeling Pipeline


Ce dépôt présente l'aboutissement du projet mené dans le cadre du cours **"Projet Encadré 2"** du **Master 1 Plurital** . Je l'héberge ici pour archiver nos résultats et documenter les compétences en Topic Modeling suite à la clôture de l'accès GitLab.

## Collaboration tournante: 
**Passation de code dynamique** : 
* Chaque semaine, les équipes étaient redistribuées sur GitLab.
* Chaque nouveau groupe devait s'approprier, stabiliser et faire évoluer le projet hérité de l'équipe précédente.

## Contenu de ce Dépôt
Ce repo archive la **version finale et stabilisée** produite par mon équipe en fin de semestre. Il témoigne de l'ensemble du workflow NLP réalisé : de la collecte de flux RSS à la modélisation thématique (LDA & BERTopic), en passant par une analyse linguistique approfondie. 

---

## Architecture Globale du Projet
```text
DEPOT_GIT_PROJET/
│
├── [Branche : main] (Code Source)
│   │   # Le cœur du programme : scripts fonctionnels et autonomes
│   ├── README.md               <-- Manuel utilisateur
│   ├── corpus/                 <-- Échantillon du corpus RSS (Extraits bruts pour démonstration si besoin)
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

### En savoir plus
Pour une immersion totale dans les détails du projet et ses résultats :

- Documentation & Rapport : Basculez sur la branche doc pour consulter le Manuel Utilisateur détaillé (README) ainsi que notre rapport de projet.

- Démo Interactive : Vous pouvez visualiser nos résultats de modélisation directement via ce lien :
https://pengchen2001.github.io/Flux-RSS-Topic-Modeling/page-html/projet.html
