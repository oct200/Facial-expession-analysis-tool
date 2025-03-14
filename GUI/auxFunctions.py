import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import cv2
import os
import copy
import numpy as np

import dataBase
import aiModel

def threadEmotie(frame,sharedBool,frameCount,lista):
    result = aiModel.prelucrareImage(frame)
    if result!=6:
        lista.append({"rez":result,"count":frameCount})
    sharedBool[0] = True


def calculDictEmotii():
    video = cv2.VideoCapture(st.session_state.videoPath)
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    video.release()
    framesPerBin = total_frames/100.0
    if framesPerBin<1:
        framesPerBin=1
    lista = [0] * 100
    dictEmotii = {"0": copy.deepcopy(lista), "1": copy.deepcopy(lista), "2": copy.deepcopy(lista), "3": copy.deepcopy(lista),"4": copy.deepcopy(lista)}
    for frame in st.session_state.listaEmotiiLive:
        bin = int(frame['count']/framesPerBin)
        if bin >= 0 and bin < 100:
            dictEmotii[str(frame['rez'])][bin] += 1
    return dictEmotii




def afisareChart(dict_data:dict):
    x = list(range(100))
    for i in range(100):
        sum = dict_data["0"][i]+dict_data["1"][i]+dict_data["2"][i]+dict_data["3"][i]+dict_data["4"][i]
        if sum == 0:
            continue
        dict_data["0"][i] = dict_data["0"][i]/sum * 100
        dict_data["1"][i] = dict_data["1"][i] / sum * 100
        dict_data["2"][i] = dict_data["2"][i] / sum * 100
        dict_data["3"][i] = dict_data["3"][i] / sum * 100
        dict_data["4"][i] = dict_data["4"][i] / sum * 100
    df = pd.DataFrame({
        'x': x,
        'angry': dict_data["0"],
        'happy': dict_data["1"],
        'neutral': dict_data["2"],
        'sad': dict_data["3"],
        'surprised': dict_data["4"]
    })

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['x'], y=df['angry'], mode='lines', name='angry', line=dict(color='red', width=3)))
    fig.add_trace(go.Scatter(x=df['x'], y=df['happy'], mode='lines', name='happy', line=dict(color='green', width=3)))
    fig.add_trace(go.Scatter(x=df['x'], y=df['neutral'], mode='lines', name='neutral', line=dict(color='yellow', width=3)))
    fig.add_trace(go.Scatter(x=df['x'], y=df['sad'], mode='lines', name='sad', line=dict(color='purple', width=3)))
    fig.add_trace(go.Scatter(x=df['x'], y=df['surprised'], mode='lines', name='surprised', line=dict(color='orange', width=3)))

    fig.update_layout(
        title='Emotions throughout the video',
        xaxis_title='Moment',
        yaxis_title='Emotion presence',
        hovermode='x unified'
    )
    return fig

def afisarePieChart(dict):
    emotionArray = [0,0,0,0,0]
    labels = ["angry","happy","neutral","sad","surprised"]
    for x in range(100):
        for y in range(5):
            emotionArray[y] += dict[str(y)][x]
    color_map={"angry":"red",
               "happy":"green",
               "neutral":"yellow",
               "sad":"purple",
               "surprised":"orange"}
    fig = px.pie(values=emotionArray, names=labels,title="Emotion presence", color=["angry","happy","neutral","sad","surprised"],color_discrete_map=color_map)
    return fig

@st.dialog("Enter a new title")
def rename():
    strType = "video"
    if st.session_state.type == "folder":
        strType = "folder"
    with st.container():
        col1, col2 = st.columns([8, 2])
        with col1:
            title = st.text_input("Enter the new title for your "+strType, placeholder="...", autocomplete="off")
        with col2:
            if st.button("rename"):
                asyncio.run(dataBase.rename(st.session_state.idRename, title))
                st.session_state.rename = False
                st.session_state.renamed = "none"
                st.rerun()

@st.dialog("Create a new folder")
def createFolder():
    st.session_state.newFolder = False
    with st.container():
        col1, col2 = st.columns([8, 2])
        with col1:
            folderName = st.text_input("Enter the name of the folder", placeholder="...", autocomplete="off")
        with col2:
            if st.button("create"):
                asyncio.run(dataBase.insertFolder(st.session_state.idUser, st.session_state.currentFolder, folderName))
                st.rerun()

def fileDownloading():
    emotions = ["angry", "happy", "neutral", "sad", "surprised"]
    if not os.path.exists(emotions[st.session_state.emotionIndex]):
        os.makedirs(emotions[st.session_state.emotionIndex],exist_ok=False)
    downl = False
    while True:
        image = asyncio.run(dataBase.getLabeledImage(st.session_state.idUser,st.session_state.emotionIndex))
        if image["image"] != "None":
            file_path = os.path.join(emotions[st.session_state.emotionIndex], image["idImage"]+".png")
            cv2.imwrite(file_path, np.array(image["image"]))
            downl = True
        else:
            break
    return downl

@st.dialog("Choose the files to download")
def downloadFiles():
    emotions = ["angry", "happy", "neutral", "sad", "surprised"]
    with st.container():
        col1,col2 = st.columns([1,1])
        with col1:
            if st.button("download all " + emotions[st.session_state.emotionIndex] + " pictures on this account"):
                asyncio.run(dataBase.resetDownloads(st.session_state.idUser,st.session_state.emotionIndex))
                downl = fileDownloading()
                if downl == True:
                    st.success("Files were downloaded successfully")
                else:
                    st.error("No files were downloaded")
        with col2:
            if st.button("download all new " + emotions[st.session_state.emotionIndex] + " pictures on this account", help="Downloads only the images that were never downloaded before"):
                downl = fileDownloading()
                if downl == True:
                    st.success("Files were downloaded successfully")
                else:
                    st.error("No files were downloaded")
