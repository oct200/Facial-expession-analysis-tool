from random import randint
import streamlit as st
import asyncio
import cv2
import threading
import os
import copy
from datetime import datetime
from streamlit_option_menu import option_menu

import dataBase
import aiModel
import auxFunctions

def initBar():
    with st.sidebar:
        app = option_menu(
            menu_title="Emotion detection",
            options = ['History','Upload video','Record new video','New folder','Download labeled pictures','Help','Back to log-in'],
            icons = ['clock-history','upload','webcam','folder','download','question-circle','person-fill'],
            menu_icon=st.session_state.menuIcon,
            default_index=['History','Upload video','Record new video','New folder','Download labeled pictures','Help','Back to log-in'].index(st.session_state.selected_option)
        )
        if app == "History":
            if st.session_state.appState != "history":
                st.session_state.appState = "history"
                st.session_state.selected_option = "History"
                st.session_state.nrReset = 0
                st.rerun()
        if app == "Upload video":
            if st.session_state.appState != "new-video":
                st.session_state.appState = "new-video"
                st.session_state.selected_option = "Upload video"
                st.session_state.nrReset = 0
                st.rerun()
        if app == "Record new video":
            if st.session_state.appState != "new-video-live":
                st.session_state.appState = "new-video-live"
                st.session_state.selected_option = "Record new video"
                st.rerun()
        if app == "New folder":
            if st.session_state.selected_option != "New folder":
                st.session_state.selected_option = "New folder"
                st.session_state.newFolder = True
                st.session_state.nrReset = 0
                st.rerun()
        if app == "Download labeled pictures":
            if st.session_state.appState != "Download labeled pictures":
                st.session_state.appState = "Download labeled pictures"
                st.session_state.selected_option = "Download labeled pictures"
                st.session_state.nrReset = 0
                st.rerun()
        if app == "Help":
            if st.session_state.appState != "Help":
                st.session_state.selected_option = "Help"
                st.session_state.appState = "Help"
                st.session_state.nrReset = 0
                st.rerun()
        if app == "Back to log-in":
            st.session_state.currentFolder = "none"
            st.session_state.appState = "log-in"
            st.session_state.selected_option = "History"
            st.session_state.recording = 0
            currDir = os.getcwd()
            output_path = os.path.join(currDir, "video.mp4")
            st.session_state.videoPath = output_path
            st.session_state.listaEmotiiLive = []
            st.session_state.newFolder = False
            st.session_state.currentFolder = "none"
            st.session_state.currentFolderName = "Main page"
            st.session_state.rename = False
            st.session_state.idRename = "none"
            st.session_state.nrReset = 0
            st.session_state.selected_option = "History"
            st.session_state.type = ""
            st.rerun()

def initLogIn():
    textbox_username = st.text_input("Enter your username", autocomplete="off", placeholder="username...")
    textbox_password = st.text_input("Enter your password", help="Minimum 8 characters", type="password",placeholder="password...")
    strErr = ""
    strSucc = ""
    with st.container():
        col1, col2 = st.columns([4, 4])
        with col1:
            if st.button("log-in"):
                if textbox_username and textbox_password:
                    id = asyncio.run(dataBase.existaCont(textbox_username, textbox_password))
                    if id != "None":
                        st.session_state.idUser = id
                        st.session_state.user = textbox_username
                        st.session_state.appState = "history"
                        icons = ["emoji-angry-fill", "emoji-astonished-fill", "emoji-frown-fill", "emoji-laughing-fill",
                                 "emoji-neutral-fill"]
                        nr = randint(0, len(icons) - 1)
                        st.session_state.menuIcon = icons[nr]
                        st.rerun()
                    else:
                        strErr = "Invalid username or password"
                else:
                    strErr = "Please insert both the username and the password"
        with col2:
            if st.button("new account"):
                if len(textbox_password) < 8:
                    strErr = "Password must contain minimum 8 characters"
                if len(strErr) < 8:
                    if textbox_username and textbox_password:
                        dejaExista = asyncio.run(dataBase.existaUser(textbox_username))
                        if dejaExista != "None":
                            strErr = "An account with this username already exists"
                        else:
                            id = asyncio.run(dataBase.insertCont(textbox_username, textbox_password))
                            st.session_state.idUser = id
                            st.session_state.user = textbox_username
                            strSucc = "Account created successfully"
                    else:
                        strErr = "Please insert both the username and the password"
    if strErr != "":
        st.error(strErr)
    if strSucc != "":
        st.success(strSucc)

def initHistory():
    emptyVideoWidget = st.empty()
    with st.container():
        col1, col2 = st.columns([5, 5])
        with col1:
            emptyWidget = st.empty()
        with col2:
            emptyWidget2 = st.empty()
    st.title(st.session_state.currentFolderName + ": ")
    listaVideos = asyncio.run(dataBase.getAllVideos(st.session_state.idUser, st.session_state.currentFolder))
    for video in listaVideos:
        if video["type"] == "folder":
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([5, 1, 1, 1, 1])
                with col1:
                    st.write(video['titlu'])
                with col2:
                    if st.button("📂", help="OPEN FOLDER", key="open folder " + video['_id']):
                        st.session_state.currentFolder = video['_id']
                        st.session_state.currentFolderName = video['titlu']
                        st.rerun()
                with col4:
                    if st.button("✏️", help="RENAME FOLDER", key="rename" + video['_id']):
                        st.session_state.rename = True
                        st.session_state.idRename = video['_id']
                        st.session_state.type = video["type"]
                        st.rerun()
                with col5:
                    if st.button("🗑️", help="DELETE FOLDER", key="delete " + video['_id']):
                        asyncio.run(dataBase.deleteFolder(video['_id']))
                        st.rerun()
    for video in listaVideos:
        if video["type"] == "video":
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([5, 1, 1, 1, 1])
                if video["type"] == "video":
                    with col1:
                        st.write(video['titlu'])
                    with col2:
                        if (st.button("👁️", help="SEE VIDEO", key="see video " + video['idVideo'])):
                            response = asyncio.run(dataBase.getVideoById(video['idVideo']))
                            emptyVideoWidget.video(response)
                    if "emotii" in video:
                        with col3:
                            if (st.button("🎭", help="SEE EMOTIONS", key="see emotions " + video['idVideo'])):
                                dict = asyncio.run(dataBase.getVideoEmotionsById(video['idVideo']))["emotii"]
                                emptyWidget2.plotly_chart(auxFunctions.afisarePieChart(dict))
                                emptyWidget.plotly_chart(auxFunctions.afisareChart(dict))
                    else:
                        with col3:
                            if (st.button("⏳", help="VIDEO IS STILL BEING PROCESSED",
                                          key="see emotions " + video['idVideo'])):
                                emptyWidget.write("The video is still being processed")
                    with col4:
                        if st.button("✏️", help="RENAME VIDEO", key="rename" + video['idVideo']):
                            st.session_state.rename = True
                            st.session_state.idRename = video['_id']
                            st.session_state.type = video["type"]
                            st.rerun()
                    with col5:
                        if (st.button("🗑️", help="DELETE VIDEO", key="delete " + video['idVideo'])):
                            asyncio.run(dataBase.deleteVideo(video['idVideo']))
                            st.rerun()
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    if st.session_state.currentFolder != "none":
        if st.button("⤸"):
            parent = asyncio.run(dataBase.getFolderParent(st.session_state.currentFolder))
            st.session_state.currentFolder = parent["parentId"]
            st.session_state.currentFolderName = parent["parentTitle"]
            st.rerun()

    if st.session_state.newFolder == True:
        auxFunctions.createFolder()

def initDownload():
    emotions = ["Angry", "Happy", "Neutral", "Sad", "Surprised"]
    i = 0
    st.header("Download 48x48 greyscale images of faces that strongly match these expressions:")
    for emotion in emotions:
        with st.container():
            col1, col2 = st.columns([4, 2])
            with col1:
                st.write(emotions[i])
            with col2:
                if st.button("⬇️", key=str(i) + emotions[i]):
                    st.session_state.emotionIndex = i
                    auxFunctions.downloadFiles()
        i += 1

def initNewVideo():
    file_name = st.file_uploader("Choose a video", type=["mp4", "avi", "webm", "mov", "mkv"])
    textbox_titlu = st.text_input("Choose a title for the video", autocomplete="off")
    if st.button("upload new video"):
        if file_name:
            video_data = file_name.read()
            asyncio.run(aiModel.prelucrareVideo(video_data, st.session_state.idUser, textbox_titlu,st.session_state.currentFolder))
            st.success("The video is now being processed")


#se inregistreaza un nou video, se scrie intr-un fisier din care se salveaza videoul si se trimite catre baza de date de-o data cu rezultatul analizei
#pe parcursul filmarii se analizeaza pe rand frame-uri, un nou frame fiind analizat doar dupa terminarea celui trimis la modelul ai inaintea sa
#rezultatul, respectiv dictionarul cu prezenta emotiilor se calculeaza la orpirea filmarii
def initNewVideoLive():
    if st.session_state.nrReset == 0:
        st.session_state.nrReset += 1
        st.rerun()
    if "cap" not in st.session_state:
        st.session_state.cap = cv2.VideoCapture(0)
    st.session_state.cap.open(0)
    if "out" not in st.session_state:
        frame_width = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'H246')
        st.session_state.out = cv2.VideoWriter(str(st.session_state.videoPath), fourcc, 25.0,
                                               (frame_width, frame_height))
    if st.session_state.recording == 0:
        if not st.session_state.out.isOpened():
            frame_width = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'H246')
            st.session_state.out.open(str(st.session_state.videoPath), fourcc, 25.0, (frame_width, frame_height))
    if st.session_state.recording == 0:
        if st.button("start video"):
            st.session_state.recording = 1
            st.rerun()
    if st.session_state.recording == 1:
        if st.button("stop video"):
            st.session_state.recording = 2
            st.rerun()
    pictureFrame = st.empty()
    if st.session_state.recording == 0:
        while st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if not ret:
                st.write("error getting video")
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pictureFrame.image(frame_rgb)
    if st.session_state.recording == 1:
        sharedBool = [True]
        frameCount = 0
        while st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if not ret:
                st.write("error getting video")
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pictureFrame.image(frame_rgb)
            if sharedBool[0] == True:
                sharedBool[0] = False
                thread = threading.Thread(target=auxFunctions.threadEmotie,
                                          args=(frame_rgb, sharedBool, frameCount, st.session_state.listaEmotiiLive))
                thread.start()
            st.session_state.out.write(frame)
            frameCount += 1
    if st.session_state.recording == 2:
        if st.session_state.out.isOpened():
            st.session_state.out.release()
        with open(st.session_state.videoPath, "rb") as file:
            video = file.read()
            st.video(video)
        dictEmotii = auxFunctions.calculDictEmotii()
        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                dictEmotii2 = copy.deepcopy(dictEmotii)
                st.plotly_chart(auxFunctions.afisareChart(dictEmotii2))
            with col2:
                dictEmotii3 = copy.deepcopy(dictEmotii)
                st.plotly_chart(auxFunctions.afisarePieChart(dictEmotii3))
        asyncio.run(dataBase.uploadVideo(video, st.session_state.idUser, str(datetime.now()), dictEmotii,
                                         st.session_state.currentFolder))
        if os.path.exists(st.session_state.videoPath):
            os.remove(st.session_state.videoPath)
        st.session_state.listaEmotiiLive.clear()

def initHelp():
    st.title("Info about the app")
    st.header("History")
    st.text(
        "In the 'History' section, the user can see all the videos and folders created by him. \nEvery new video or folder will be saved in the folder displayed at that time in the history.")
    st.header("Uploading a video")
    st.text(
        "By clicking the 'Upload video' option in the option menu, the user can send a new video to be analysed and saved in the database.\nAfter selecting a video and a title, clicking the 'upload' button sends the video to be processed.\nThe user can check if the video processing is complete in the 'History' section")
    st.header("Recording a video")
    st.text(
        "By clicking the 'Record new video' option in the option menu, the user can record a video in the app, which is analysed in real-time.\nThe video recording only starts after the 'Start' button was pushed.\nAfter the 'Stop' button is pressed, the video analysis is displayed on the screen and the video in saved in the database.")
    st.header("Creating a folder")
    st.text(
        "By clicking the 'New folder' option in the option meny, a new folder can be created.\nThis new file will be stored in the folder currecntly displayed in the 'History' section")
    st.header("Emotion analysis explained")
    st.subheader("Emotions timeline")
    st.text(
        "This plot shows how the person's emotions throughout the video.\nThe video is divided into 100 parts.\nEach point on the plot represents one emotion's presence in the corresponding moment of the video, as a percentage.\nFor example, if the first part of the video has 4 frames where the person is happy and 1 frame where the person is sad,\n the value for 'happy' will be 80, while for 'sad', it will be 20.\nExample,where the person is mostly happy in the first half of the video, then mostly sad and angry in the second half:")
    list = [0] * 100
    dict = {
        '0': [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 2, 4, 3, 2, 2, 2, 4, 2, 3, 3, 4, 4, 2, 2, 3, 4, 2, 4, 4, 2,
              3, 3, 2, 3, 4, 3, 3, 4, 2, 3, 2, 4, 4, 3, 2, 3, 4, 4, 4, 2, 4, 2, 3, 2, 4, 2, 2, 4, 2, 3],
        '1': [4, 5, 4, 4, 4, 4, 5, 5, 4, 5, 5, 4, 4, 5, 4, 5, 5, 5, 5, 4, 4, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 4, 4, 4,
              5, 4, 5, 5, 4, 5, 5, 4, 4, 5, 4, 4, 4, 5, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        '2': [2, 0, 2, 2, 1, 2, 2, 1, 1, 1, 2, 1, 1, 1, 0, 2, 1, 2, 1, 2, 2, 0, 0, 0, 2, 1, 1, 1, 2, 0, 0, 0, 0, 1, 2,
              0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 2, 0, 2, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0,
              1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1],
        '3': [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0,
              0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 4, 5, 4, 4, 5, 5, 4, 4, 5, 4, 5, 4, 5, 5, 4, 4, 5, 4, 5, 5,
              5, 4, 4, 5, 5, 4, 5, 4, 4, 5, 5, 4, 4, 5, 5, 4, 4, 5, 4, 5, 4, 4, 4, 5, 5, 4, 4, 5, 4, 5],
        '4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    st.plotly_chart(auxFunctions.afisareChart(dict))
    st.subheader("Emotions pie chart")
    st.text(
        "This pie chart shows emotions' presence as a percentage, suming up all the analysed frames.\nExample for the same analysis as the last chart:")
    st.plotly_chart(auxFunctions.afisarePieChart(dict))

