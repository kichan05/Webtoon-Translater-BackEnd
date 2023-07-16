from datetime import datetime
from io import BytesIO

from PIL import Image
from PIL import ImageDraw
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

import config
from model import Webtoon
from webtoonTranslater import WebtoonTranslater

app = FastAPI()
webtoonTranslater = WebtoonTranslater(config.CLOVA_OCR_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 모든 origin을 허용합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 method를 허용합니다.
    allow_headers=["*"]  # 모든 headers를 허용합니다.
)


@app.get("/")
def root():
    return "Hello World"


@app.get("/test")
def test():
    timeStamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    return {"result": "OK", "timeStamp": timeStamp}

#
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

    ocr_result = webtoonTranslater.imageOCR(image_path, True)

    # draw = ImageDraw.Draw(merged_image)
    #
    # for i in ocr_result:
    #     draw.rectangle(
    #         (tuple(i["point1"]), tuple(i["point2"])),
    #         outline = (255, 0, 0), width=1
    #     )
    #
    # merged_image.show()


    return {"timeStamp": timeStamp, "ocr": ocr_result}

@app.post("/translate")
async def translate(webtoon : Webtoon):
    timeStamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    textAll = " ".join([i.text for i in webtoon.ocr])

    return {"timeStamp": timeStamp, "result" : textAll}


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