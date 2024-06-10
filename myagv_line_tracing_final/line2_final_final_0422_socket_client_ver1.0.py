import cv2
import numpy as np
import threading
import logging
from ultralytics import YOLO
import socket
import sys

#################### 소켓 통신 config ##########################
HOST = '172.30.1.63'
PORT = 12345
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Client created')
c.connect((HOST,PORT))
print("Connected")
###############################################################

model = YOLO('myagv_line_tracing_final/best_final.pt') # 코랩에서 학습 후 모델 (코랩해서 학습해서 신호등 초록, 빨강색 구분 모델용)
run_flag = True
cap = cv2.VideoCapture(0)


def process_frame(frame):
    height, width, _ = frame.shape
    # roi_height = int((height*3/2))
    # roi_bottom = int(height*5/6)
    # roi_top = height - roi_height
    # roi = frame[roi_top:roi_bottom :]
    # line roi
    # cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 4)
    
    roi_height = int(height / 3)
    roi_height2 = int(height / 6)
    roi_top = height - roi_height2  
    roi_top2 = height - roi_height  
    
    roi = frame[roi_top2:roi_top, :] 
    
    # hsv transform
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_white = np.array([20, 95, 125], dtype=np.uint8)
    upper_white = np.array([60, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    # transform black, white and binary
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY) 
    
    # yellow binary image calculate
    yellow_binary_image = cv2.bitwise_and(binary_image, binary_image, mask=white_mask)
    
    # find outline
    contours, _ = cv2.findContours(yellow_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # max outline analyze
    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)

        M = cv2.moments(max_contour)

        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            # center_line = width // 2

            if cx < width / 3:
                return "LEFT"
            elif cx > width / 3 * 2:
                return "RIGHT"
            else:
                return "FORWARD" 
    return None

def camera_thread():
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera error")
                break
            
            class_id = 3
            result_yolo = model(frame)
            annotated_frame = result_yolo[0].plot()
            
            bndboxs = result_yolo[0].boxes.data
            # name = results[0].names
            
            for i, bndbox in enumerate(bndboxs):
                class_id = int(bndbox[5])
                # class_name = name[class_id]
            
            if class_id == 1: # 데이터 학습 yaml 파일 class_id : red_light
                run_flag = False # 1
                
            else: # 데이터 학습 yaml 파일 class_id : green_light
                run_flag = True # 0
                
            result = process_frame(annotated_frame)
            
            if result and run_flag:
                if result == "LEFT":
                    c.send(result.encode())
                elif result == "RIGHT":
                    c.send(result.encode())
                elif result == "FORWARD":
                    c.send(result.encode())
            else:
                print("==============AGV IS STOP ================")
                command = "STOP"
                c.send(command.encode())

            cv2.imshow("Yolo_model & line_tracer",annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()

camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()