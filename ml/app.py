from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import mediapipe as mp

app = Flask(__name__)

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

CHEATING_THRESHOLD = 0.3
EYE_GAZE_THRESHOLD = 0.2


@app.route('/detect_cheating', methods=['POST'])
def detect_cheating():
    global lifeline

    image_data = request.get_json()['image']

    image_bytes = base64.b64decode(image_data)
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    image = cv2.resize(image, (640, 480))

    face_results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if face_results.detections:
        print("Face detected")  
        for detection in face_results.detections:
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = int((bbox.xmin + bbox.width) * w)
            y2 = int((bbox.ymin + bbox.height) * h)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            face_mesh_results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if face_mesh_results.multi_face_landmarks:
                
                cheating_detected = 0 
                
                for face_landmarks in face_mesh_results.multi_face_landmarks:
                    left_eye_center = (int(face_landmarks.landmark[33].x * w), int(face_landmarks.landmark[33].y * h))
                    right_eye_center = (int(face_landmarks.landmark[263].x * w), int(face_landmarks.landmark[263].y * h))
                    print("left_eye_center[0] - center_x -> ", left_eye_center[0] - center_x, " > ",w * EYE_GAZE_THRESHOLD," <- w * EYE_GAZE_THRESHOLD")
                    print("left_eye_center[1] - center_y -> ", left_eye_center[1] - center_y, " > ",h * EYE_GAZE_THRESHOLD," <- h * EYE_GAZE_THRESHOLD")
                    print("right_eye_center[0] - center_x -> ", right_eye_center[0] - center_x, " > ",w * EYE_GAZE_THRESHOLD," <- w * EYE_GAZE_THRESHOLD")
                    print("right_eye_center[0] - center_x ->", right_eye_center[0] - center_x, " > ",h * EYE_GAZE_THRESHOLD," <- h * EYE_GAZE_THRESHOLD")
                   
                    if abs(left_eye_center[0] - center_x) > w * EYE_GAZE_THRESHOLD or \
                       abs(left_eye_center[1] - center_y) > h * EYE_GAZE_THRESHOLD or \
                       abs(right_eye_center[0] - center_x) > w * EYE_GAZE_THRESHOLD or \
                       abs(right_eye_center[1] - center_y) > h * EYE_GAZE_THRESHOLD:
                        
                       
                        cheating_detected = 1  
                        
                if cheating_detected:
                    print("cheating")
                    return jsonify({'cheating_detected': 1})
                else:
                    print("not cheating")
                    return jsonify({'cheating_detected': 0})

    # If no face is detected
    print("Face not detected")
    return jsonify({'cheating_detected': -1})


if __name__ == '__main__':
    app.run(debug=True)