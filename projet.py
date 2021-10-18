# -*- coding: utf-8 -*-

#####################################
#           Import module           #
#####################################

import pandas as pd
import folium
import math
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pydeck as pdk
import streamlit as st
from streamlit_folium import folium_static


#################################################
#           Configuration of the page           #
#################################################

st.set_page_config(layout='wide')

st.set_option('deprecation.showPyplotGlobalUse', False)

#########################################
#           Loading a dataset           #
#########################################

folders = os.listdir('Semantic Location History')

df_all = pd.read_json(
    'Semantic Location History/2014/2014_JUNE.json')
for folder in folders:
    files = os.listdir(
        'Semantic Location History/' + folder)
    for file in files:
        df = pd.read_json(
            'Semantic Location History/' + folder + '/' + file)
        df_all = pd.concat([df_all, df])


###########################################
#           Sidebar information           #
###########################################

st.sidebar.title("Florian Meuleman")

col1, col2 = st.sidebar.columns(2)

with col1:
    photoProfil = Image.open('P1044153 (2) - Copie.png')
    st.image(photoProfil)

with col2:
    QRcode = Image.open('QRcode.png')
    st.image(QRcode)


st.sidebar.markdown("linkedin.com/in/florian-meuleman/")

st.sidebar.header("Project description")

st.sidebar.markdown(
    "The objective is to analyze and visualize all of my Google Map data")

st.sidebar.header("Select a database to visualize")

dataset = st.sidebar.radio("", ("Home", "Historique des positions.json",
                                "Semantic Location History", "Semantic Location History with update", "Display of positions on 3d diagram"))

st.markdown("<h1 style='text-align: center; color: black;'>Google Map Project</h1>",
            unsafe_allow_html=True)


####################################
#           Introduction           #
####################################

if dataset == "Home":
    st.title("List of datasets used")

    st.text("Google Map provides 2 elements :")
    st.text("- 1 folder containing a detailed list of visited place sorted by date (and since 2018 the coresponding jouney)")
    st.text("- 1 file containing all my positions")

    image = Image.open('capture.png')

    st.image(image)

    st.title("Data analysis is done in 3 parts")
    st.text("Analysis and visualization of the 'historique des positions' file")
    st.text("Analysis and visualization of the visited place from the Semantic Location Historic folder")
    st.text("Analysis and visualization of the trips from the Semantic Location Historic folder")


###############################################
#           Historique des position           #
###############################################

elif dataset == "Historique des positions.json":

    st.title("Analysis and visualization of the 'historique des positions' file")

    st.text("The file is in json so i obtain an unreadable dataframe")
    st.text("So I turned the json file into a dictionaty, save into a new dataframe only the values I need and remove all the stationaty positions")
    st.text("json file : 500 000 rows, new dataframe : 1 500 rows")

    df = pd.read_json('Historique des positions.json')

    df_sorted = pd.DataFrame(columns=[
        "latitude", "longitude", "annee", "mois", "jour", "heure", "minute", "seconde"])

    for i in range(len(df)):
        latitude = int(dict(df)["locations"][i]["latitudeE7"])/10**7
        longitude = int(dict(df)["locations"][i]["longitudeE7"])/10**7
        date = datetime.fromtimestamp(
            int(dict(df)["locations"][i]["timestampMs"])/1000)
        annee = int(date.strftime('%Y'))
        mois = int(date.strftime('%m'))
        jour = int(date.strftime('%d'))
        heure = int(date.strftime('%H'))
        minute = int(date.strftime('%M'))
        seconde = int(date.strftime('%S'))

        if len(df_sorted) == 0:
            df_sorted.loc[0] = [latitude, longitude,
                                annee, mois, jour, heure, minute, seconde]

        elif math.sqrt((latitude - df_sorted.iloc[-1]["latitude"])**2 + (longitude - df_sorted.iloc[-1]["longitude"])**2) > 0.1:
            df_sorted.loc[len(df_sorted)+1] = [latitude, longitude,
                                               annee, mois, jour, heure, minute, seconde]

    df_sorted

    my_map = folium.Map(
        location=[48.7903962, 2.3688847],
        zoom_start=6
    )

    for i in range(len(df_sorted)):
        if int(str(df_sorted["annee"].iloc[i])[:4]) <= 2015:
            couleur = "blue"
        elif int(str(df_sorted["annee"].iloc[i])[:4]) > 2015 and int(str(df_sorted["annee"].iloc[i])[:4]) <= 2020:
            couleur = "green"
        else:
            couleur = "red"

        folium.Marker(location=[df_sorted["latitude"].iloc[i], df_sorted["longitude"].iloc[i]],
                      popup=folium.Popup(folium.Html('<h>Date</h> ' + str(df_sorted["annee"].iloc[i])[:4] + '<h>/</h1>' + str(
                          df_sorted["mois"].iloc[i])[:2] + '<h>/</h1>' + str(df_sorted["jour"].iloc[i])[:2], script=True), ),
                      icon=folium.Icon(color=couleur, prefix='fa', icon='circle')).add_to(my_map)

    folium_static(my_map, 1000, 600)


#################################################
#           Semantic Location History           #
#################################################

elif dataset == "Semantic Location History":

    df_sorted = pd.DataFrame(columns=["latitude", "longitude", "endTime",
                                      "startTime", "date debut", "date fin", "duree", "lieux"])

    for i in range(len(df_all)):
        try:
            latitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["centerLatE7"])/10**7
            longitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["centerLngE7"])/10**7
            endTime = int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["duration"]["endTimestampMs"])
            startTime = int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["duration"]["startTimestampMs"])
            dateDebut = datetime.fromtimestamp(int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["duration"]["startTimestampMs"])/1000)
            dateFin = datetime.fromtimestamp(int(dict(df_all.iloc[i])[
                "timelineObjects"]["placeVisit"]["duration"]["endTimestampMs"])/1000)
            duree = (endTime - startTime)/1000/60/60
            try:
                lieux = dict(df_all.iloc[i])[
                    "timelineObjects"]["placeVisit"]["location"]["name"]
            except:
                lieux = "unknown"
            df_sorted.loc[i] = [latitude, longitude, endTime,
                                startTime, dateDebut, dateFin, duree, lieux]
        except:
            pass

    st.title("Analysis and visualization of the visited place from the Semantic Location Historic folder")

    df_sorted

    my_map = folium.Map(
        location=[48.7903962, 2.3688847],
        zoom_start=6
    )

    for i in range(len(df_sorted)):
        if math.ceil(df_sorted["duree"].iloc[i]) <= 2:
            couleur = "blue"
        elif math.ceil(df_sorted["duree"].iloc[i]) > 2 and math.ceil(df_sorted["duree"].iloc[i]) <= 6:
            couleur = "green"
        else:
            couleur = "red"
        folium.Marker(location=[df_sorted["latitude"].iloc[i], df_sorted["longitude"].iloc[i]],
                      popup=folium.Popup(folium.Html('<h>Date : </h> ' + str(df_sorted["date debut"].iloc[i])[:10] + '<br> <h>Duree : </h1>' + str(math.ceil(
                          df_sorted["duree"].iloc[i])) + "<h>h</h>" + "<br> <h>Lieux : </h>" + str(df_sorted["lieux"].iloc[i]), script=True), max_width=500, ),
                      icon=folium.Icon(color=couleur, prefix='fa', icon='circle')).add_to(my_map)

    folium_static(my_map, 1000, 600)

    st.text("Dataframe sort by time spent at a location")

    df_lieux = df_sorted[["duree", "lieux"]].groupby(
        ["lieux"]).sum().sort_values(by='duree', ascending=False)

    df_lieux

    plt.figure(figsize=(35, 8))
    plt.bar(df_lieux.index[:8], df_lieux["duree"][:8])
    plt.title("Sum of the time in h depending place")

    plt.show()

    st.pyplot()


#############################################################
#           Semantic Location History with update           #
#############################################################

elif dataset == "Semantic Location History with update":

    df_sorted = pd.DataFrame(columns=["activityType", "probability", "distance", "endTimestampMs", "startTimestampMs", "date fin",
                                      "date debut", "duree", "speed", "endLocationLatitude", "endLocationLongitude", "startLocationLatitude", "startLocationLongitude"])

    for i in range(len(df_all)):
        try:
            activityType = dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["activities"][0]["activityType"]
            probability = dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["activities"][0]["probability"]
            distance = dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["distance"]
            endTime = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["duration"]["endTimestampMs"])
            startTime = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["duration"]["startTimestampMs"])
            dateFin = datetime.fromtimestamp(int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["duration"]["endTimestampMs"])/1000)
            dateDebut = datetime.fromtimestamp(int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["duration"]["startTimestampMs"])/1000)
            duree = (endTime - startTime)/1000/60/60
            endLocationLatitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["endLocation"]["latitudeE7"])/10**7
            speed = (distance/1000)/duree
            endLocationLongitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["endLocation"]["longitudeE7"])/10**7
            startLocationLatitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["startLocation"]["latitudeE7"])/10**7
            startLocationLongitude = int(dict(df_all.iloc[i])[
                "timelineObjects"]["activitySegment"]["startLocation"]["longitudeE7"])/10**7

            df_sorted.loc[i] = [activityType, probability, distance, endTime, startTime, dateFin, dateDebut,
                                duree, speed, endLocationLatitude, endLocationLongitude, startLocationLatitude, startLocationLongitude]
        except:
            pass

    st.title(
        "Analysis and visualization of the trips from the Semantic Location Historic folder")

    df_sorted

    my_map = folium.Map(
        location=[48.7903962, 2.3688847],
        zoom_start=6
    )

    for i in range(len(df_sorted)):
        couleurs = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
                    'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

        couleur = couleurs[i % 19]

        folium.Marker(location=[df_sorted["startLocationLatitude"].iloc[i], df_sorted["startLocationLongitude"].iloc[i]],
                      popup=folium.Popup(folium.Html('<h>Date : </h> ' + str(df_sorted["date debut"].iloc[i])[:10] + '<br> <h>Moyen de transport : </h> ' + str(df_sorted["activityType"].iloc[i]) + '<br> <h>Duree : </h1>' + str(math.ceil(
                          df_sorted["duree"].iloc[i])) + "<h>h</h>" + "<br> <h>Distance : </h>" + str(df_sorted["distance"].iloc[i]/1000) + "<h> km</h>", script=True), max_width=500, ),
                      icon=folium.Icon(color=couleur, prefix='fa')).add_to(my_map)

        folium.Marker(location=[df_sorted["endLocationLatitude"].iloc[i], df_sorted["endLocationLongitude"].iloc[i]],
                      popup=folium.Popup(folium.Html('<h>Date : </h> ' + str(df_sorted["date debut"].iloc[i])[:10] + '<br> <h>Moyen de transport : </h> ' + str(df_sorted["activityType"].iloc[i]) + '<br> <h>Duree : </h1>' + str(math.ceil(
                          df_sorted["duree"].iloc[i])) + "<h>h</h>" + "<br> <h>Distance : </h>" + str(df_sorted["distance"].iloc[i]/1000) + "<h> km</h>", script=True), max_width=500, ),
                      icon=folium.Icon(color=couleur, prefix='fa',)).add_to(my_map)

        points = [(df_sorted["startLocationLatitude"].iloc[i], df_sorted["startLocationLongitude"].iloc[i]),
                  (df_sorted["endLocationLatitude"].iloc[i], df_sorted["endLocationLongitude"].iloc[i])]

        folium.PolyLine(points, color=couleur, weight=2.5,
                        opacity=0.85).add_to(my_map)

    folium_static(my_map, 1000, 600)

    moyenne = df_sorted.groupby(["activityType"]).mean()[["duree", "speed"]]

    moyenne

    plt.figure(figsize=(25, 8))
    plt.bar(moyenne.index, moyenne["duree"])
    plt.title("Average journey time in hours depending on the activity type")

    plt.show()

    st.pyplot()

    plt.figure(figsize=(25, 8))
    plt.bar(moyenne.index, moyenne["speed"])
    plt.title("Average speed in km/h depending on the activity type")

    plt.show()

    st.pyplot()

else:

    anneeChoisie = st.sidebar.slider('', 2013, 2021, 2013, 1)

    df_positions = pd.read_csv("positions.txt")

    # Define a layer to display on a map
    layer = pdk.Layer(
        "HexagonLayer",
        df_positions[df_positions["annee"] <= anneeChoisie],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        elevation_scale=500,
        pickable=True,
        elevation_range=[0, 300],
        extruded=True,
        coverage=1,
    )

    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=2.3688847, latitude=48.7903962, zoom=6, min_zoom=5, max_zoom=15, pitch=40.5, bearing=-27.36,
    )

    st.header("Display Display of positions on 3d diagram")
    # Render
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
