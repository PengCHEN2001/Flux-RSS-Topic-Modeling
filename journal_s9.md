# Topic modeling avec LDA

## groupe 16 : Catalina,  Lydia, Salma

# This is a Heading h1
## Exercice 2.1, 2.2: 
*Ces deux exercies concerne la prise en main de l'outil lda par les trois membres du groupes individuellement.*
###### This is a Heading h6

## Exercice 2.3, 2.4


*La partie 2.3 a ete realisé individuellement, et la partie 2.4 la repartition des tache est la suivante: R1: Catalina 
                       R2: Lydia 
                       R3: Salma *  


**R1**  
(a) pour pouvoir choisir entre les mot-formes ou les lemmes





**R2**
b) pour pouvoir filtrer sur les catégories grammaticales (ex : ne prendre que les noms et les verbes)





**R3**
c) faire en sorte que le tout soit configurable via des options de la ligne de commande

J'ai reorganisé le script run lda en retirant la partie tokeniztion car nous l'avons deja realisé dans l'exercice precedent analyzers.py.
Pour cette exercice et de faire en sorte qu'il soit configurable, j'ai ajouté les arguments suivant : --num-topics= Nombre de topics
   input-file="Chemin vers un corpus deja sérialisé ( articles incluant tokens), 
   --passes= Nombre de tour d'entrainement _" how often we train the model on the entire corpus"_
   --input-format"=Format du corpus sérialisé en pickle, json ou xml. 
   --output-file"="Chemin du fichier de sortie apres topic modelling . 
   Apres avoir defini quel arguement je voulais rendre configurable. 
   Il faut definir une fonction run_lda qui va me permettre qu'a partir de ma liste d'arciles, un nombre de topic et de passes me retourne un des topic.
   
J'ai ajouté dans datastructure une class Topic qui comprend le score de coherence ( _Topic representations are distributions of words, represented as a list of pairs of word IDs and their probabilities._) et topic represenation.

A l'origine le script affichait dans le terminal le resultat sous la forme d'une (liste de tuple). Pour ameliorer la mise en forme la focntion run lda retounera donc une liste de topic : 
```
formated_topic=[]

    #
    for topic in top_topics:
        topic_representation=[{'value':word[1], 'proba': float(word[0])} for word in topic[0]]
        formated_topic.append(
            Topic(coherence_score= float(topic[1]),
            topic_representation= topic_representation
            ))
    return formated_topic

```

Et l'output file de cette liste de Topic est sous le format json 
```
  with open(args.output_file,'w', encoding='utf-8') as f:
         json.dump([asdict(topic) for topic in topics],f,indent=4)
```

J'ai ensuite merge la branche de Lydia dans dev, pour ensuite merge dev dans ma branche et regler les conflit, une tois tout cela reglé et testé,  j'ai pu merge ma branche dans dev.

