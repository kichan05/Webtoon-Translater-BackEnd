# import easyocr
import json
import uuid
import time

import numpy as np

import requests as req
from PIL import Image
from easyocr import easyocr

from sklearn.cluster import DBSCAN

import config


class WebtoonTranslater:
    def __init__(self):
        self.reader = easyocr.Reader(['ko'])
        self.clustering = DBSCAN(eps=50, min_samples=1)

    def imageOCR(self, image_path, free):
        def clova_ocr_format(ocr_result):
            ocr_filds = ocr_result["images"][0]["fields"]

            ocr_format = []

            for i in ocr_filds:
                bounding_poly = i["boundingPoly"]["vertices"]
                p1 = bounding_poly[0]
                p2 = bounding_poly[2]

                ocr_format.append({
                    # "ocr_type": "clova orc",
                    "point1": [int(p1["x"]), int(p1["y"])],
                    "point2": [int(p2["x"]), int(p2["y"])],
                    "text": i["inferText"],
                    "confidence": i["inferConfidence"],
                    # "lineBreak": i["lineBreak"],
                })

            return ocr_format

        def clova_ocr():
            api_url = "https://n87nr0rbfr.apigw.ntruss.com/custom/v1/23718/bcc5ffe3be8da4c798eb64b40967c258a03f17fd162bc02a15384f27b7537799/general"

            headers = {'X-OCR-SECRET': config.CLOVA_OCR_API_KEY}

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

        def easy_ocr():
            ocrResult = self.reader.readtext(image_path)
            ocrFormat = []

            for point, text, acc in ocrResult:
                ocrFormat.append({
                    # "ocr_type": "easy ocr",
                    "point1": [int(point[0][0]), int(point[0][1])],
                    "point2": [int(point[2][0]), int(point[2][1])],
                    "text": text,
                    "confidence": round(acc, 2)
                })

            return ocrFormat

        if (free):
            ocr_result = easy_ocr()
        else:
            ocr_result = clova_ocr()

        ocr_clustr = self.cloud_clustering(ocr_result)

        return ocr_clustr

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

    def cloud_clustering(self, cloud_list):
        coords = [
            [
                np.float64((cloud["point1"][0] + cloud["point2"][0]) / 2),
                np.float64((cloud["point1"][1] + cloud["point2"][0]) / 2),
            ] for cloud in cloud_list
        ]
        coords = np.array(coords)

        clusters = self.clustering.fit(coords)
        lables = clusters.labels_

        cloud_cluster = {}

        for n, cluster in enumerate(lables):
            cloud = cloud_list[n]
            if (cluster in cloud_cluster):
                cloud_cluster[cluster]["point1"][0] = min(cloud_cluster[cluster]["point1"][0], cloud["point1"][0])
                cloud_cluster[cluster]["point1"][1] = min(cloud_cluster[cluster]["point1"][1], cloud["point1"][1])

                cloud_cluster[cluster]["point2"][0] = max(cloud_cluster[cluster]["point2"][0], cloud["point2"][0])
                cloud_cluster[cluster]["point2"][1] = max(cloud_cluster[cluster]["point2"][1], cloud["point2"][1])

                cloud_cluster[cluster]["text"] += " " + cloud["text"]

                cloud_cluster[cluster]["confidence"].append(cloud["confidence"])
            else:
                cloud_cluster[cluster] = {
                    "point1": cloud["point1"],
                    "point2": cloud["point2"],
                    "text": cloud["text"],
                    "confidence": [cloud["confidence"]]
                }

        for cluster in set(lables):
            confidence = cloud_cluster[cluster]["confidence"]
            cloud_cluster[cluster]["confidence"] = round(sum(confidence) / len(confidence), 3)

        return list(cloud_cluster.values())

    def dialogue_translate(self, text):
        def papago_api_tranlate(text):
            url = f"https://openapi.naver.com/v1/papago/n2mt"
            header = {
                "Content-Type": "application/x-www-form-urlencoded",
                "charset": "UTF-8",
                "X-Naver-Client-Id": config.PAPAGO_CLIENT_ID,
                "X-Naver-Client-Secret": config.PAPAGO_CLIENT_SECRET
            }
            params = {
                "source": "ko",
                "target": "en",
                "text": text
            }

            res = req.post(url, headers=header, data=params)
            res = json.loads(res.text)

            return res["message"]["result"]["translatedText"]

        return papago_api_tranlate(text)
