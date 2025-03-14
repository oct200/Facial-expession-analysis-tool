import json
import bcrypt

import httpx
salt = b'$2b$14$/uMf73XbMiwSQU3gOBbFvu'


async def existaUser(user):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/existaUser/"
        response = await client.post(url, json={"user": user})
        return response.json()["id"]

async def resetDownloads(userId,emotionIndex):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/resetDownloads/"
        data = {"userId": userId,
                "emotionIndex":emotionIndex}
        await client.post(url, data=data)

async def getLabeledImage(userId,emotionIndex):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/getLabeledImage/"
        data = {"userId": userId,
                "emotionIndex":emotionIndex}
        response = await client.post(url, data=data)
        return response.json()

async def existaCont(user, parola):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/existaCont/"
        if user != "a" :
            parola = parola.encode('utf-8')
            parola = bcrypt.hashpw(parola,salt)
            parola = parola.decode('utf-8')
        response = await client.post(url, json={"user": user,"parola":parola})
        return response.json()["id"]

async def insertCont(user,parola):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/insertCont/"
        parola = parola.encode('utf-8')
        parola = bcrypt.hashpw(parola,salt)
        parola = parola.decode('utf-8')
        response = await client.post(url, json={"user": user, "parola":parola})
        return response.json()["id"]

async def rename(id,titlu):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/rename/"
        response = await client.post(url,json={"id":id,"titlu":titlu})

async def uploadVideo(video, userId, titlu, dict, parent):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/uploadVideo/"
        dict = json.dumps(dict)
        files = {
            "video": video
        }
        data={
            "userId":userId,
            "titlu":titlu,
            "emotii":dict,
            "parent":parent
        }
        response = await client.post(url, files=files, data=data, timeout=100)
        return response.json()

async def getAllVideos(userId,currentFolder):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/getAllVideos/"
        response = await client.post(url,json = {"userId":userId,"parent":currentFolder})
        return response.json()

async def getVideoById(videoId):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/getVideoById/"
        response = await client.post(url, json = {"videoId":videoId})
        return response.content

async def getVideoEmotionsById(videoId):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/getVideoEmotionsById/"
        response = await client.post(url, json = {"videoId":videoId})
        return response.json()

async def insertFolder(userId,parentId,folderName):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/insertFolder/"
        data={
            "userId":userId,
            "parentId":parentId,
            "folderName":folderName
        }
        response = await client.post(url, data=data)

async def deleteFolder(folderId):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/deleteFolder/"
        response = await client.post(url, json = {"folderId":folderId})
        return response.json()


async def deleteVideo(videoId):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/deleteVideo/"
        response = await client.post(url, json = {"videoId":videoId})
        return response.json()

async def getFolderParent(folderId):
    async with httpx.AsyncClient() as client:
        url = f"http://dataBaseAction:8000/getFolderParent/"
        response = await client.post(url, json = {"folderId":folderId})
        return response.json()








