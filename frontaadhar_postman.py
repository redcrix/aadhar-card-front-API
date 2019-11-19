from flask import Flask, json, request, render_template
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import cv2
import numpy as np
import re
import face_recognition
import time

# For error use:- pytesseract.pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
app = Flask(__name__)


@app.route('/aad_front_side', methods=['POST', 'GET'])
def front_name_dob_number():

    time_str = time.strftime("%Y%m%d-%H%M%S")

    if request.method == 'POST':
        print(request.files)
        if 'idfront' not in request.files:
            return json.dumps({"message": 'No image of frontside of aadhar card', "success": False, "data": ''})
        idfront = request.files['idfront']
        idfront.save(time_str + '_front1.jpg')
        tup = cv2.imread(time_str + '_front1.jpg')

        if request.method == 'POST':
            print(request.files)
            if 'p_image' not in request.files:
                return json.dumps({"message": 'No selfie image of user', "success": False, "data": ''})
            p_image = request.files['p_image']
            p_image.save(time_str + '_p_image.jpg')
            tup2 = cv2.imread(time_str + "_p_image.jpg")

        gray = cv2.cvtColor(tup, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.2, 7)

        for (x, y, w, h) in faces:
            ix = 0
            cv2.rectangle(tup, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi_color = tup[y:y + h, x:x + w]

            crop_pic = cv2.imwrite(time_str + '_croppic.jpg', roi_color)
            ix = ix + 1

        known_image = face_recognition.load_image_file(time_str + '_p_image.jpg')
        unknown_image = face_recognition.load_image_file(time_str + '_croppic.jpg')
        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
        bide_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results23 = face_recognition.compare_faces([bide_encoding], unknown_encoding)

        alpha = 1
        beta = 25
        result = cv2.addWeighted(tup, alpha, np.zeros(tup.shape, tup.dtype), 0, beta)
        text = (pytesseract.image_to_string(tup, lang='eng'))

        text = text.replace("/\s+/g, ' '","")
                #print(text)
        number = re.findall(r"[\+\(]?[1-9][0-9 .\-()]{8,}[0-9]", text)
        date = re.findall(r"[\d]{1,4}[/-][\d]{1,4}[/-][\d]{1,4}", text)
        name = re.findall(r"[A-Za-z]{6,15}\s[A-Za-z]{2,15}", text)

        data = dict({"name": name, "dob": date, "idn": number, "match": True})
        if results23 == [True]:
            return json.dumps({"code": 200, "message": 'ID data extract successfully', "success": True, "data": data}).replace("[", "").replace("]", "")
        else:
            data = dict({"name": '', "dob": '', "idn": '', "match": False})
            return json.dumps({"code": 201, "message": 'ID data extract unsuccessfully',"success": False, "data": data}).replace("[","").replace("]","")




if __name__ == '__main__':
    app.run(debug=True)
