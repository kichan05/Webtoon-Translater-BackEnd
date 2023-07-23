from datetime import datetime
from io import BytesIO

from PIL import Image, ImageFont
from PIL import ImageDraw
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from model import Webtoon
from webtoonTranslater import WebtoonTranslater

app = FastAPI()
webtoonTranslater = WebtoonTranslater()

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

    drawImage = merged_image.copy()
    draw = ImageDraw.Draw(drawImage)
    for n, i in enumerate(ocr_result):
        box_postion = tuple(i["point1"] + i["point2"])

        draw.rectangle(
            box_postion,
            width=2, outline=(255, 57, 57)
        )

    drawImage.save(f"./ocr/{timeStamp}.png")

    return {"timeStamp": timeStamp, "ocr": ocr_result}

@app.post("/translate")
async def translate(webtoon : Webtoon):
    translate = [webtoonTranslater.dialogue_translate(i.text) for i in webtoon.ocr]
    print(translate)

    webtoonImage = Image.open(f"./image/{webtoon.time_stamp}.png")

    draw = ImageDraw.Draw(webtoonImage)
    font = ImageFont.truetype("./font/KOMTXTBI.ttf", size=20)

    for n, text in enumerate(translate):
        box_postion = tuple(webtoon.ocr[n].point1 + webtoon.ocr[n].point2)

        draw.rectangle(
            box_postion,
            fill="#ffffff",
        )

        draw.text(
            box_postion,
            text=text, fill="#000000", font=font
        )

    webtoonImage.save(f"./translate/{webtoon.time_stamp}.png")

    return {"result" : "success", "translate_webtoon_url" : f"/translate/{webtoon.time_stamp}.png"}


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

@app.get("/translate/{image_name}")
def getTranslateImage(image_name):
    return FileResponse(f"./translate/{image_name}", media_type="image/*")

@app.get("/ocr/{image_name}")
def getOcrImage(image_name):
    return FileResponse(f"./ocr/{image_name}", media_type="image/*")


# if __name__ == '__main__':
    # webtoonTranslater.drawWebtoon("./image/2023-07-17 01.53.26.png", "test.png")