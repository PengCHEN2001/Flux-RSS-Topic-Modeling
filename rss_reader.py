#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#######POUR L'UTILISATEUR :
#Lancement du script : 
#1) Ouvrir un terminal et aller dans un environnement virtuel, exemple : source venvs/plurital/bin/activate.
#2) Installer feedparser sur le terminal avec la commande suivante : pip install feedparser
#3) Pour ouvrir ce script, utiliser cette commande avec ces arguments : python3 fichier.py chemin/vers/fichier.xml ou alors python3 fichier.py fichier.xml
# Exemple : python3 rss_feedparser.py "Le Figaro - Vidéos.xml"
# N.B. : Parfois, certains fichiers peuvent avoir des "espaces", il faut donc les appeler avec des guillemets (sinon, la machine va croire que ce sont des arguments : d'où l'erreur d'affichage "error: unrecognized arguments:").
# Optionnel : pour voir tous les résulats générés, on peut utiliser la commande suivante : python3 rss_feedparser.py chemin/vers/fichier_xml > fichier.txt
#######


"""
3ème méthode : un script avec le module feedparser pour générer les métadonnées de chaque lien URLs.
On retrouvera les métadonnées suivantes : 
— l’identifiant (id) de l’article
— la source : le nom du journal, qu’on peut approximer avec le nom du fichier
— le titre de l’article
— le contenu de l’article (description)
— la date de l’article
— les catégories auxquelles appartient l’article
"""
import feedparser
import argparse #Pour appeler notre fonction. 
from bs4 import BeautifulSoup #Pour nettoyer les balises dans un texte.

def metadonnees(fichier_xml) : #Pour le "fichier_xml" : sur le terminal, soit il faut taper le chemin jusqu'au fichier, soit taper le nom du fichier xml. 
    """
    Récupérer les métadonnées de chaque article du flux.
    Arguments : le dossier contenant les fichiers xml.
    Return : cette fonction retourne une liste des métadonnées de chaque article dont l'id, la source, le contenu, la date et les catégories.
    """
    feed = feedparser.parse(fichier_xml) #Pour parser un flux RSS (ou atom).
    metadonnees_articles = [] #Liste vide pour les métadonnées qu'on va récupérer dans chaque article grâce aux fichiers xml.
    
    #Extraire toutes les métadonnées pour chaque fichier xml : 
    for entry in feed.entries :
        
        #Pour les catégories : 
        #1) Récupérer les "catégorie(s)" dans les fichiers xml : 
        channel_categories = [tag.get("term") for tag in feed.feed.get("tags", [])]
        item_categories = [tag.get("term") for tag in entry.get("tags", [])]
        #2) Conditions pour l'extraction des catégories et du résultats qu'il retourne (soit une ou plusieurs catégories, soit rien).
        if channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Figaro".
            categories = item_categories + channel_categories
        else : 
            if channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Flux RSS".
                categories = channel_categories
            else : 
                if not channel_categories and item_categories : #Afficher les catégories pour les fichiers xml "Bast" et "ELucid".
                    categories = item_categories
                if not channel_categories and not item_categories : #Afficher les catégories pour les fichiers xml "Libération".
                    categories = []
       
        #Pour la description - nettoyage de la description :
        description = (
            entry.get("description") 
            or entry.get("summary")
            or "No description or summary"
            )
        if description : #Condition pour supprimer les balises présentes dans la description de certains fichiers xml. On veut garder que du texte. Module utilisé "BeautifulSoup" : 
            nettoyer_description = BeautifulSoup(description, "html.parser" )
            description_texte = nettoyer_description.get_text(" ", strip=True)
        
            
        #Extraire les metadonnées qu'on cherche pour chaque article et les ajouter aux metadonnees_articles :
        metadonnees_articles.append({
            "id" : (
                entry.get("id")
                or entry.get("link")
                or "No id"
                ), #Si la donnée n'apparaît pas dans le fichier xml, alors on notera "No id" pour absence d'identifiant.
            "source" : fichier_xml,
            "title" : entry.get("title", "No title"),
            "description" : description_texte,
            "date" : ( 
                entry.get("published")
                or entry.get("updated")
                or "No published or updated"
                ), 
            "categories" : categories
        })
        
    return metadonnees_articles 
    
 
if __name__ == "__main__" : 
    parser = argparse.ArgumentParser(description = "Extraire les métadonnées d'un flux RSS.")
    parser.add_argument("fichier_xml", help = "Mettre le chemin vers le fichier xml ou le nom du fichier xml.")
    args = parser.parse_args()
    resultats_fichier_xml = metadonnees(args.fichier_xml)

    for article in resultats_fichier_xml : 
        for key, value in article.items() :
            print(key, ":", value)
        print()
        
