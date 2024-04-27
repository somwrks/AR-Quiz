from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import mediapipe as mp

app = Flask(__name__)

# Initialize MediaPipe Face Detection and Face Mesh
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Cheating detection threshold
CHEATING_THRESHOLD = 0.3
EYE_GAZE_THRESHOLD = 0.2

# Lifeline counter
lifeline = 3

@app.route('/detect_cheating', methods=['POST'])
def detect_cheating():
    global lifeline

    # Get the image data from the request
    image_data = request.get_json()['image']

    # Decode the image data and convert it to a numpy array
    image_bytes = base64.b64decode(image_data)
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    # Resize the image to a smaller size
    image = cv2.resize(image, (640, 480))

    # Detect faces in the image
    face_results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Check if a face is detected
    if face_results.detections:
        print("Face detected")
        # Get the face bounding box and calculate the center
        for detection in face_results.detections:
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = int((bbox.xmin + bbox.width) * w)
            y2 = int((bbox.ymin + bbox.height) * h)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Detect face landmarks
            face_mesh_results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if face_mesh_results.multi_face_landmarks:
                for face_landmarks in face_mesh_results.multi_face_landmarks:
                    left_eye_center = (int(face_landmarks.landmark[33].x * w), int(face_landmarks.landmark[33].y * h))
                    right_eye_center = (int(face_landmarks.landmark[263].x * w), int(face_landmarks.landmark[263].y * h))
                    # Check if the eyes are within the allowed gaze radius
                    if abs(left_eye_center[0] - center_x) > w * EYE_GAZE_THRESHOLD or \
                       abs(left_eye_center[1] - center_y) > h * EYE_GAZE_THRESHOLD or \
                       abs(right_eye_center[0] - center_x) > w * EYE_GAZE_THRESHOLD or \
                       abs(right_eye_center[1] - center_y) > h * EYE_GAZE_THRESHOLD:
                        lifeline -= 1
                        print(f"Lifeline: {lifeline}")
                        if lifeline <= 0:
                            print("Cheating detected")
                            # Draw a red rectangle around the face
                            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            return jsonify({'cheating_detected': 1, 'lifeline': 0})
                        else:
                            print("Cheating not detected")
                            # Draw a green rectangle around the face
                            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            return jsonify({'cheating_detected': -1, 'lifeline': lifeline})

    return jsonify({'cheating_detected': 1, 'lifeline': lifeline-1})

if __name__ == '__main__':
    app.run(debug=True)