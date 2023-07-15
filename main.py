from fastapi import FastAPI, UploadFile
from io import BytesIO
from PIL import Image
import easyocr
import numpy as np
from datetime import datetime

app = FastAPI()
reader = easyocr.Reader(['ko'])

@app.post("/imageOcr")
async def root(fileList: list[UploadFile]):
    timeStamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

    imageList = []
    mergedWidth, mergedHeight = 0, 0

    for file in fileList:
        content = await file.read()
        image = Image.open(BytesIO(content))
        width, height = image.size
        mergedWidth = width
        mergedHeight += height

        imageList.append(image)

    mergedImage : Image = Image.new("RGB", (mergedWidth, mergedHeight), (255, 255, 255))
    currentHeight = 0
    for image in imageList:
        mergedImage.paste(image, (0, currentHeight))
        currentHeight += image.height

    imageName = f"./image/{timeStamp}.png"

    mergedImage.save(imageName)
    ocrResult = reader.readtext(imageName)
    ocrFormat = []

    for point, text, acc in ocrResult:
        ocrFormat.append({
            "point1" : [int(point[0][0]), int(point[0][1])],
            "point2" : [int(point[2][0]), int(point[2][1])],
            "text" : text,
            "acc" : round(acc, 2)
        })

    print(ocrFormat)

    return {"timeStamp" : timeStamp, "ocr" : ocrFormat}