import pymongo as pm
from fastapi import FastAPI, Request, Response, File, Form, UploadFile
import uvicorn
import json
from gridfs import GridFS, errors
from bson import ObjectId
import os
import modele

client = pm.MongoClient(f"mongodb://mongodb:27017")
db = client["proiect"]
fs = GridFS(db)
app = FastAPI()

@app.post("/existaUser/")
async def existaCont(cont:modele.UserName):
    user = cont.user
    colectie = db["conturi"]
    cont = colectie.find_one({"user":user})
    id = "None"
    if cont is not None:
        id = cont["_id"]
    return {"id":str(id)}


@app.post("/existaCont/")
async def existaCont(cont:modele.cont):
    user = cont.user
    parola = cont.parola
    colectie = db["conturi"]
    cont = colectie.find_one({"user":user,"parola":parola})
    id = "None"
    if cont is not None:
        id = cont["_id"]
    return {"id":str(id)}

@app.post("/rename/")
async def rename(name:modele.Rename):
    id = name.id
    titlu = name.titlu
    col = db["Videos"]
    col.update_one({"_id":ObjectId(id)},{"$set":{"titlu":titlu}})

@app.post("/insertCont/")
async def insertCont(cont:modele.cont):
    colectie = db["conturi"]
    result = colectie.insert_one({"user":cont.user,"parola":cont.parola})
    id = result.inserted_id
    return {"id":str(id)}

@app.post("/uploadVideoFirst/")
async def uploadVideoFirst(video: UploadFile = File(...),userId: str = Form(...),titlu: str = Form(...),parent:str=Form(...)):
    grid_in = fs.new_file(content_type=video.content_type)
    grid_in.write(video.file)
    grid_in.close()

    video_id = grid_in._id
    colVideo = db["Videos"]
    colVideo.insert_one({"user":userId,"idVideo":video_id,"titlu":titlu,"parent":parent,"type":"video"})
    return {"idVideo":str(video_id)}

@app.post("/uploadVideoEmotions/")
async def uploadVideoEmotions(idVideo : str = Form(...),emotii: str = Form(...)):
    emotii = json.loads(emotii)
    colVideouri = db["Videos"]
    idVideo = ObjectId(idVideo)
    colVideouri.update_one({"idVideo":idVideo},{"$set":{"emotii":emotii}})

@app.post("/uploadVideo/")
async def uploadVideo(video: UploadFile = File(...),userId: str = Form(...),titlu: str = Form(...),emotii: str = Form(...),parent: str = Form(...)):
    emotii = json.loads(emotii)
    grid_in = fs.new_file(content_type = video.content_type)
    grid_in.write(video.file)
    grid_in.close()

    video_id = grid_in._id
    colVideouri = db["Videos"]
    colVideouri.insert_one({"user":userId,"idVideo":video_id,"titlu":titlu,"emotii":emotii,"parent":parent,"type":"video"})

@app.post("/insertFolder/")
async def insertFolder(userId: str = Form(),parentId : str = Form(...),folderName: str = Form(...)):
    col = db["Videos"]
    col.insert_one({"user":userId,"parent":parentId,"titlu":folderName,"type":"folder"})
    print("sf")

@app.post("/deleteVideo/")
async def deleteVideo(videoId: modele.VideoId):
    idVideo = videoId.videoId
    try:
        video_id = ObjectId(idVideo)
    except Exception:
        return {"message":"Id video does not exist"}
    try:
        fs.delete(video_id)
    except errors.NoFile:
        return {"message": "Video not found in GridFS"}
    except Exception as e:
        return {"message":"Video not found"}
    colVideouri = db["Videos"]
    idVideo = ObjectId(idVideo)
    result = colVideouri.delete_one({"idVideo":idVideo})

    return {"message": "Video deleted successfully"}

def deleteChildren(parentId):
    col = db["Videos"]
    copii = col.find({"parent":parentId})
    for copil in copii:
        deleteChildren(str(copil["_id"]))
    col.delete_one({"_id":ObjectId(parentId)})


@app.post("/deleteFolder/")
async def deleteFolder(folderId: modele.FolderId):
    idFolder = folderId.folderId
    deleteChildren(idFolder)
    col = db["Videos"]
    col.delete_one({"_id":ObjectId(idFolder)})
    return {"message": "Folder deleted successfully"}


@app.post("/getAllVideos/")
async def getAllVideos(userId : modele.UserID):
    idCont = userId.userId
    parent = userId.parent
    colVideos = db["Videos"]
    rows = colVideos.find({"user":idCont,"parent":parent})
    rowsForReturn = []
    for row in rows:
        if row["type"] == "video":
            row["_id"] = str(row["_id"])
            row["idVideo"] = str(row["idVideo"])
            rowsForReturn.append(row)
        else:
            row["_id"] = str(row["_id"])
            rowsForReturn.append(row)
    return rowsForReturn

@app.post("/uploadLabeledImage/")
def uploadLabeledImage(labeledImages : modele.LabeledImages):
    col = db["LabeledImages"]
    for image in labeledImages.savedFrames:
        col.insert_one({"croppedImage":image.image,"userId":labeledImages.userId,"emotionIndex":image.emotionIndex,"saved":False})

@app.post("/getLabeledImage/")
async def getLabeledImage(userId: str = Form(...),emotionIndex : str = Form(...)):
    col = db["LabeledImages"]
    image = col.find_one({"userId":userId,"saved":False,"emotionIndex":emotionIndex})
    if image != None:
        idImage = image["_id"]
        col.update_one({"_id":idImage},{"$set":{"saved":True}})
        return {"image":image["croppedImage"],"idImage":str(idImage)}
    else:
        return {"image":"None"}

@app.post("/resetDownloads/")
async def resetDownloads(userId : str = Form(...),emotionIndex : str = Form()):
    col = db["LabeledImages"]
    col.update_many({"userId":userId,"emotionIndex":emotionIndex},{"$set":{"saved":False}})

@app.post("/getVideoById/")
async def getVideoById(videoId : modele.VideoId):
    try:
        idVideo = ObjectId(videoId.videoId)
    except Exception as e:
        return {"message": "Invalid video ID"}
    grid_out = fs.get(idVideo)
    video = grid_out.read()
    return Response(content=video)

@app.post("/getFolderParent/")
async def getFolderParent(folderId : modele.FolderId):
    id = folderId.folderId
    col = db["Videos"]
    folder = col.find_one({"_id":ObjectId(id)})
    if folder["parent"] == ("none"):
        return {"parentId": "none", "parentTitle": "Main page"}
    parent = col.find_one({"_id":ObjectId(folder["parent"])})
    return {"parentId":folder["parent"],"parentTitle":parent["titlu"]}

@app.post("/getVideoEmotionsById/")
async def getVideoEmotionsById(videoId : modele.VideoId):
    idVideo = ObjectId(videoId.videoId)
    colVideo = db["Videos"]
    dict = colVideo.find_one({"idVideo": idVideo}, {"_id": 0, "emotii": 1})["emotii"]
    return {"emotii":dict}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

