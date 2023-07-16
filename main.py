import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from datetime import datetime
from io import BytesIO
from PIL import Image
import config
from webtoonTranslater import WebtoonTranslater

app = FastAPI()
webtoonTranslater = WebtoonTranslater(config.CLOVA_OCR_API_KEY)


@app.get("/")
def root():
    return "Hello World"


@app.get("/test")
def test():
    timeStamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    return {"result": "OK", "timeStamp": timeStamp}

@app.post("/imageOcr")
async def imageOcr(fileList: list[UploadFile]):
    timeStamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

    image_list = []
    for file in fileList:
        content = await file.read()
        image = Image.open(BytesIO(content))
        image_list.append(image)

    merged_image = webtoonTranslater.image_merged(image_list)

    image_path = f"./image/{timeStamp}.png"
    merged_image.save(image_path)

    ocr_result = webtoonTranslater.imageOCR(image_path)

    return {"timeStamp": timeStamp, "ocr": ocr_result}


@app.post("/imageUpload")
async def imageUpload(fileList: list[UploadFile]):
    for file in fileList:
        content = await file.read()
        image = Image.open(BytesIO(content))
        image.show()

    return {"result": "OK"}


@app.get("/image/{image_name}")
def getImage(image_name):
    return FileResponse(f"./image/{image_name}", media_type="image/*")

if __name__ == '__main__':
    uvicorn.run("main:app")