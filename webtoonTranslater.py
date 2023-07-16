# import easyocr
import json
import uuid
import time

import requests as req
from PIL import Image

class WebtoonTranslater:
    def __init__(self, CLOVA_OCR_API_KEY):
        self.CLOVA_OCR_API_KEY = CLOVA_OCR_API_KEY

    def imageOCR(self, image_path):
        def clova_ocr_format(ocr_result):
            ocr_filds = ocr_result["images"][0]["fields"]

            ocr_format = []

            for i in ocr_filds:
                bounding_poly = i["boundingPoly"]["vertices"]
                p1 = bounding_poly[0]
                p2 = bounding_poly[2]

                ocr_format.append({
                    "point1": [int(p1["x"]), int(p1["y"])],
                    "point2": [int(p2["x"]), int(p2["y"])],
                    "text": i["inferText"],
                    "confidence": i["inferConfidence"],
                    "lineBreak": i["lineBreak"],
                })

            return ocr_format

        api_url = "https://n87nr0rbfr.apigw.ntruss.com/custom/v1/23718/bcc5ffe3be8da4c798eb64b40967c258a03f17fd162bc02a15384f27b7537799/general"

        headers = {'X-OCR-SECRET': self.CLOVA_OCR_API_KEY}

        request_json = {
            'images': [
                {
                    'format': 'png',
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
            ('file', open(image_path, 'rb'))
        ]

        res = req.post(api_url, headers=headers, data=payload, files=files)
        res = json.loads(res.text.encode("utf8"))
        ocr_format = clova_ocr_format(res)

        return ocr_format



    def image_merged(self, image_list: list[Image]):
        merged_width, merged_height = 0, 0

        for image in image_list:
            width, height = image.size
            merged_width = width
            merged_height += height

        merged_image: Image = Image.new("RGB", (merged_width, merged_height), (255, 255, 255))
        currentHeight = 0
        for image in image_list:
            merged_image.paste(image, (0, currentHeight))
            currentHeight += image.height

        return merged_image
