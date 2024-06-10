import cv2
import numpy as np
import threading
from pymycobot.myagv import MyAgv
import time
import sys

agv = MyAgv("/dev/ttyAMA2", 115200)
run_flag = True
yellow_direction = None

def process_frame(frame):
    height, width, _ = frame.shape
    # roi_height = int((height*3/2))
    # roi_bottom = int(height*5/6)
    # roi_top = height - roi_height
    # roi = frame[roi_top:roi_bottom :]
    
    roi_height1 = int(height /3)
    roi_height2 = int(height/6)
    roi_top = height - roi_height2
    roi_top2 = height - roi_height1
    
    roi = frame[roi_top2:roi_top,:]
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height2), (255, 0, 0), 2)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_white = np.array([20, 95, 125], dtype=np.uint8)
    upper_white = np.array([60, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY) 
    
    yellow_binary_image = cv2.bitwise_and(binary_image, binary_image, mask=white_mask)
    
    contours, _ = cv2.findContours(yellow_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(max_contour)

        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            if cx < width / 3:
                return "LEFT"
            elif cx > width / 3 * 2:
                return "RIGHT"
            else:
                return "FORWARD" 
    return None

def camera_thread():
    global yellow_direction
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error")
            break
        
        result = process_frame(frame)
        if result:
            yellow_direction = result

        cv2.imshow("Line Tracer", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            agv.stop()
            sys.exit()
            
            break
        
    agv.stop()
    cap.release()
    cv2.destroyAllWindows()

def motor_thread():
    while True:
        global run_flag
        global yellow_direction

        if yellow_direction and run_flag:
            if yellow_direction == "LEFT":
                #agv.restore()
                agv.counterclockwise_rotation(3)
                agv.go_ahead(1)
                print("LEFT")
                time.sleep(0.1)
            elif yellow_direction == "RIGHT":
                #agv.restore()
                agv.clockwise_rotation(3)
                agv.go_ahead(1)
                
                print("RIGHT")
                time.sleep(0.1)
            elif yellow_direction == "FORWARD":
                #agv.restore()
                agv.go_ahead(10)
                print("FORWARD")
                time.sleep(0.1)
        else:
            print("AGV IS STOPPED")
            agv.stop()

# 쓰레드 생성
camera_thread = threading.Thread(target=camera_thread)
motor_thread = threading.Thread(target=motor_thread)

# 쓰레드 시작
camera_thread.start()
motor_thread.start()

camera_thread.join()
motor_thread.join()

agv.stop()
