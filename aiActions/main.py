import copy
import threading
import time
import os
from fastapi import FastAPI, Request, File, Form, UploadFile
import uvicorn
import tempfile
import cv2
import numpy as np
import tensorflow.keras as keras
import base64
import httpx
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

import modele

model = keras.models.load_model('model2.keras')
app = FastAPI()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
executor = ThreadPoolExecutor()
executor2 = ThreadPoolExecutor()

def prelucrare(video):
    emotii = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    return video

def faceCrop(img):
    neighs = [15,10,8,6]
    i = 0
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=neighs[i])
    i+=1
    while len(faces) < 1 and i < 4:
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=neighs[i])
        i += 1
    if len(faces) != 1:
        return None
    for (x, y, w, h) in faces:
        img = frame[y:y + h, x:x + w]
        img = cv2.resize(img, (48, 48))
    return img

def prediction(img):
    emotions = {0:"angry", 1: "happy" , 2:"neutral", 3:"sad" , 4:"surprised"}
    strongMatch = False
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    img = img/255.0
    prediction = model.predict(img)
    predictie = np.argmax(prediction)
    if prediction[0][predictie] > 0.99:
        strongMatch = True
    if predictie == 3 or predictie == 0:
        prediction[0][2] *= 50
    return {"pred":np.argmax(prediction),"strongMatch":strongMatch}

def uploadCroppedImages(croppedImage,uncroppedImage,userId,emotionIndex):
    url = f'http://dataBaseAction:8000/uploadLabeledImage/'
    with httpx.Client() as client:
        client.post(url, json = {"croppedImage":croppedImage.tolist(),"uncroppedImage":uncroppedImage.tolist(),"userId":userId,"emotionIndex":str(emotionIndex)})




async def send_labeled_image_thread(croppedImage,uncroppedImage,userId):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor2, uploadCroppedImages, croppedImage, uncroppedImage,userId)

def fctVideo(file_name,userId):
    lista = [0]*100
    dictEmotii = {0:copy.deepcopy(lista),1:copy.deepcopy(lista),2:copy.deepcopy(lista),3:copy.deepcopy(lista),4:copy.deepcopy(lista)}
    video = cv2.VideoCapture(file_name)
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    framesPerBatch = total_frames/100.0
    pas = int(framesPerBatch/5)
    if pas < 1:
        pas = 1
    curent = 0
    savedFrames =[]
    while curent < total_frames:
        video.set(cv2.CAP_PROP_POS_FRAMES, curent)
        ret, frame = video.read()
        if not ret:
            break
        print(str(curent) + "/" + str(total_frames))
        try:
            face = faceCrop(frame)
            pred = prediction(face)
            dictEmotii[pred["pred"]][int(curent / framesPerBatch)] += 1
            if pred["strongMatch"] == True:
                savedFrames.append({"image":face.tolist(),"emotionIndex":str(pred["pred"])})
        except Exception as e:
            print(e)
        curent += pas
    video.release()
    cv2.destroyAllWindows()
    return {"dictEmotii":dictEmotii,"lista":savedFrames}

def uploadFrames(savedFrames,userId):
    with httpx.Client() as client:
        url = "http://dataBaseAction:8000/uploadLabeledImage/"
        client.post(url, json={"savedFrames":savedFrames,"userId":userId})



def functiePrelucrareVideo(video_data, video_id,userId):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_data)
        temp_video.flush()
    rez = fctVideo(temp_video.name,userId)
    dictEmotii = rez["dictEmotii"]
    savedFrames = rez["lista"]
    uploadFrames(savedFrames,userId)
    tries = 0
    max_tries = 300
    while tries < max_tries:
        try:
            os.remove(temp_video.name)
            break
        except:
            pass
        time.sleep(0.5)
        tries += 1
    url = f'http://dataBaseAction:8000/uploadVideoEmotions/'
    data = {
        "idVideo": video_id,
        "emotii": json.dumps(dictEmotii)
    }
    with httpx.Client() as client:
        client.post(url, data=data, timeout=1000)

async def process_video_in_thread(video_data, video_id,userId):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, functiePrelucrareVideo, video_data, video_id,userId)

@app.post("/prelucrareImagine/")
async def prelucrareImagine(request:modele.Lista):
    try:
        image = np.array(request.poza)
        image = cv2.convertScaleAbs(image)
        face = faceCrop(image)
        rez = int(prediction(face)["pred"])
        return {"rez":rez}
    except:
        return {"rez":6}


@app.post("/prelucrareVideo/")
async def prelucrareVideo(video: UploadFile = File(...),userId: str = Form(...),titlu: str = Form(...),parent: str = Form(...)):
    async with httpx.AsyncClient() as client:
        video = await video.read()
        url = f'http://dataBaseAction:8000/uploadVideoFirst/'
        files = {
            "video": video
        }
        data = {
            "userId": userId,
            "titlu": titlu,
            "parent": parent
        }
        response = await client.post(url, files=files, data=data, timeout = 1000)
        video_id = response.json()["idVideo"]
        asyncio.create_task(process_video_in_thread(video,video_id,userId))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)