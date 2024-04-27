from flask import Flask, request, jsonify
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()

# Cheating detection threshold
CHEATING_THRESHOLD = 0.3

# Lifeline counter
lifeline = 3

@app.route('/detect_cheating', methods=['POST'])
def detect_cheating():
    global lifeline

    # Get the image data from the request
    image_data = request.get_json()['image']

    # Decode the image data and convert it to a numpy array
    image = np.frombuffer(bytes.fromhex(image_data), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Detect faces in the image
    results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Check if a face is detected
    if results.detections:
        # Get the face bounding box and calculate the center
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = int((bbox.xmin + bbox.width) * w)
            y2 = int((bbox.ymin + bbox.height) * h)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Check if the face is within the allowed radius
            if abs(center_x - image.shape[1] // 2) > image.shape[1] * CHEATING_THRESHOLD or \
               abs(center_y - image.shape[0] // 2) > image.shape[0] * CHEATING_THRESHOLD:
                lifeline -= 1
                if lifeline <= 0:
                    return jsonify({'cheating_detected': True, 'lifeline': 0})
                else:
                    return jsonify({'cheating_detected': True, 'lifeline': lifeline})
    
    return jsonify({'cheating_detected': False, 'lifeline': lifeline})

if __name__ == '__main__':
    app.run(debug=True)