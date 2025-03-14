from random import randint
import streamlit as st
import os

import initPages
import auxFunctions

def initVariabile():
    if "appState" not in st.session_state:
        st.session_state.appState = "log-in"
    #recording-0 inca nu a inceput  1-acum inregistreaza 2-inregistrarea s-a terminat
    if "recording" not in st.session_state:
        st.session_state.recording = 0
    if "videoPath" not in st.session_state:
        currDir = os.getcwd()
        output_path = os.path.join(currDir, "video.mp4")
        st.session_state.videoPath = output_path
    if "listaEmotiiLive" not in st.session_state:
        st.session_state.listaEmotiiLive = []
    if "newFolder" not in st.session_state:
        st.session_state.newFolder = False
    if "currentFolder" not in st.session_state:
        st.session_state.currentFolder = "none"
    if "currentFolderName" not in st.session_state:
        st.session_state.currentFolderName = "Main page"
    if "rename" not in st.session_state:
        st.session_state.rename = False
    if "idRename" not in st.session_state:
        st.session_state.idRename = "none"
    if "nrReset" not in st.session_state:
        st.session_state.nrReset = 0
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = "History"
    if "type" not in st.session_state:
        st.session_state.type = ""
    if "menuIcon" not in st.session_state:
        icons = ["emoji-angry-fill","emoji-astonished-fill","emoji-frown-fill","emoji-laughing-fill","emoji-neutral-fill"]
        nr = randint(0,len(icons)-1)
        st.session_state.menuIcon = icons[nr]
    if "emotionIndex" not in st.session_state:
        st.session_state.emotionIndex = 0

def initGUI():
    if st.session_state.appState != "log-in":
        initPages.initBar()
    if st.session_state.appState != "new-video-live":
        if "cap" in st.session_state:
            if st.session_state.cap.isOpened():
                st.session_state.cap.release()
        st.session_state.recording = 0

    if st.session_state.rename == True:
        st.session_state.rename = False
        auxFunctions.rename()

    if st.session_state.appState == "log-in":
        initPages.initLogIn()

    elif st.session_state.appState == "Download labeled pictures":
        initPages.initDownload()

    elif st.session_state.appState == "history":
        initPages.initHistory()

    elif st.session_state.appState == "new-video":
        initPages.initNewVideo()

    elif st.session_state.appState == "new-video-live":
        initPages.initNewVideoLive()

    elif st.session_state.appState == "Help":
        initPages.initHelp()



def main():
    initVariabile()
    initGUI()



main()