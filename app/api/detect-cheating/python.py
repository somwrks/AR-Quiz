from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
import numpy as np
import base64
import mediapipe as mp
import json

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

EYE_GAZE_THRESHOLD = 0.2
HEAD_POSE_THRESHOLD = 30  # degrees

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        image_data = data['image']
        image_bytes = base64.b64decode(image_data)
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        
        face_mesh_results = face_mesh.process(image_rgb)
        
        if face_mesh_results.multi_face_landmarks:
            face_landmarks = face_mesh_results.multi_face_landmarks[0]
            
            # Eye gaze detection
            left_eye = np.mean([[face_landmarks.landmark[p].x, face_landmarks.landmark[p].y] for p in [33, 133]], axis=0)
            right_eye = np.mean([[face_landmarks.landmark[p].x, face_landmarks.landmark[p].y] for p in [362, 263]], axis=0)
            nose_tip = [face_landmarks.landmark[4].x, face_landmarks.landmark[4].y]
            
            gaze_vector = np.array([(left_eye[0] + right_eye[0])/2 - nose_tip[0],
                                    (left_eye[1] + right_eye[1])/2 - nose_tip[1]])
            
            if np.linalg.norm(gaze_vector) > EYE_GAZE_THRESHOLD:
                result = {'cheating_detected': 1, 'reason': 'Suspicious eye gaze'}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                return
            
            # Head pose estimation
            face_3d = []
            face_2d = []
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx in [33, 263, 1, 61, 291, 199]:
                    x, y = int(lm.x * w), int(lm.y * h)
                    face_2d.append([x, y])
                    face_3d.append([x, y, lm.z])
            
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)
            
            focal_length = w
            center = (w/2, h/2)
            cam_matrix = np.array([[focal_length, 0, center[0]],
                                [0, focal_length, center[1]],
                                [0, 0, 1]], dtype=np.float64)
            
            dist_matrix = np.zeros((4,1), dtype=np.float64)
            
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
            
            rmat, jac = cv2.Rodrigues(rot_vec)
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            
            x = angles[0] * 360
            y = angles[1] * 360
            
            if abs(x) > HEAD_POSE_THRESHOLD or abs(y) > HEAD_POSE_THRESHOLD:
                result = {'cheating_detected': 1, 'reason': 'Suspicious head pose'}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                return
            
            result = {'cheating_detected': 0, 'reason': 'No cheating detected'}
        else:
            result = {'cheating_detected': -1, 'reason': 'No face detected'}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=handler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
