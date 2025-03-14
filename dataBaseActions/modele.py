from pydantic import BaseModel

class UserName(BaseModel):
    user:str

class cont(BaseModel):
    user:str
    parola:str

class FrameData(BaseModel):
    image:list
    emotionIndex:str

class LabeledImages(BaseModel):
    savedFrames: list[FrameData]
    userId:str

class UserID(BaseModel):
    userId:str
    parent:str

class VideoId(BaseModel):
    videoId:str

class FolderId(BaseModel):
    folderId:str

class Rename(BaseModel):
    id:str
    titlu:str

