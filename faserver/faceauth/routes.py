import io
import cv2
import base64
import numpy as np
from imageio import imread
from .logic import getToken, add_camera_entry, face_recognition
from flask import Blueprint, request, jsonify

mod = Blueprint("faceauth", __name__, template_folder="templates")


@mod.route("/register-client", methods=['POST'])
def camera_register():
    if request.method == 'POST':
        camera_name = request.json['clientId']
        camera_serial_num = request.json['serialNumber']
        camera_token = getToken(camera_name + camera_serial_num)

        try:
            add_camera_entry(camera_name, camera_serial_num, camera_token)

            response_data = {
                'status': 'PASS',
                'message': "Camera registered succesfully!",
                'token': camera_token
            }
            return jsonify(response_data)
        except BaseException:
            response_data = {
                'status': 'FAIL',
                'message': "There was a problem registering the camera"
            }
            return jsonify(response_data)
    else:
        response_data = {
            'status': 'FAIL',
            'message': "Invalid request!"
        }
        return jsonify(response_data)


# Keeping the Debug codes until I am satisfied of
# the stability of the following code.
# Will be removed before merging with master
@mod.route("/face-auth", methods=['POST'])
def face_auth():
    if request.method == 'POST':
        encoded_img_list = request.json["imageList"]
        id_dict = {}

        # DEBUG
        imageCount = 0

        for encoded_image in encoded_img_list:
            # Get rid of the meta info
            if ',' in encoded_image:
                encoded_image = encoded_image.split(',')[1]

            img = imread(io.BytesIO(base64.b64decode(encoded_image)))

            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # DEBUG
            print()
            print("Image Number:", imageCount + 1)
            imageCount += 1

            # Shape the image for consistency
            print("[INFO] Reshaping image... ", end="")
            h, w = frame.shape[0:2]
            maxDim = max([h, w])
            extraPadding = 50
            dh = (maxDim - h) // 2 + extraPadding
            dw = (maxDim - w) // 2 + extraPadding
            frame = cv2.copyMakeBorder(frame.copy(), dh, dh, dw, dw, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            print("Reshaping done!")
            print("[INFO] Resultant frame shape:", frame.shape)

            #DEBUG
            # cv2.imshow("frame" + str(imageCount), frame)

            result = face_recognition(frame)


            if result['status'] == 'PASS':
                # DEBUG
                print("[DEBUG] Individual Face Id result -- ID: {0} PROBABILITY: {1}".format(result['id'], result['probability']))
                
                id = result['id']
                probability = result['probability']

                if id in id_dict:
                    id_dict[id]['probability_sum'] += probability
                    id_dict[id]['count'] += 1
                else:
                    id_dict[id] = {
                        'name': id.replace('_', " "),
                        'probability_sum': probability,
                        'count': 1
                    }


        finalId = None
        finalName = None
        finalProbability = 0
        maxCount = 0
        for key, value in id_dict.items():
            if value['count'] > maxCount:
                finalProbability = value['probability_sum'] / value['count']
                finalName = value['name']
                finalId = key
                maxCount = value['count']

        # Sanity check
        if finalId == None or finalName == None or finalProbability == 0:
            return jsonify({
                'status': 'FAIL',
                'message': 'Oops! Something went wrong... :/'
            })

        # DEBUG
        print("[DEBUG] Final results -- ID: {0} NAME: {1} PROBABILITY: {2}".format(finalId, finalName, finalProbability))

        return jsonify({
            'status': 'PASS',
            'id': finalId,
            'name': finalName,
            'probability': finalProbability
        })
    else:
        return jsonify({
            'status': 'FAIL',
            'message': 'Invalid request!'
        })