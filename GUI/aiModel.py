import httpx
import requests


async def prelucrareVideo(video_stream,userId, titlu, folderCurent):
    async with httpx.AsyncClient() as client:
        url = f"http://aiAction:8001/prelucrareVideo/"
        files = {
            "video": video_stream
        }
        data = {
            "userId": userId,
            "titlu": titlu,
            "parent": folderCurent
        }
        await client.post(url, files = files, data = data, timeout=1000)

def prelucrareImage(image_stream):
    image_stream = image_stream.tolist()
    url = f"http://aiAction:8001/prelucrareImagine/"
    response = requests.post(url,json={"poza":image_stream}, timeout=1000)
    return response.json()["rez"]


