import cv2
import numpy as np
from pymycobot.myagv import MyAgv
import threading
import time

cap = cv2.VideoCapture(0)
MA = MyAgv('/dev/ttyAMA2', 115200)
global line_flag 
line_flag = True

def process_frame(frame, line_flag):
    
    if line_flag == False:
        MA.retreat(1)
        
    height, width, _ = frame.shape
    roi_height = int(height / 4)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (255, 0, 0), 2)
    
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100], dtype=np.uint8)
    upper_yellow = np.array([30, 255, 255], dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    cv2.imshow("yellow_mask", yellow_mask) 

    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    direction = None
    
    if len(contours) >= 1:
        line_flag = True
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)
        
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = roi_height // 2
            
            center_line = width // 2
            if cx < center_line - 150:
                direction = "LEFT" 

                # counterclockwise
                MA.go_ahead(1)
                MA.counterclockwise_rotation(1)
                
                #time.sleep(3)

            elif cx > center_line + 150:
                direction = "RIGHT"

                # clockwise
                MA.go_ahead(1)
                MA.clockwise_rotation(1)
                #time.sleep(3)
            else:
                direction = "FORWARD"

                # forward
                MA.go_ahead(1)
                #time.sleep(3)
                
            # 화면에 화살표 그리기
            if direction == "LEFT":
                cv2.arrowedLine(frame, (center_line, roi_top + cy), (center_line - 50, roi_top + cy), (0, 0, 255), 5)
            elif direction == "RIGHT":
                cv2.arrowedLine(frame, (center_line, roi_top + cy), (center_line + 50, roi_top + cy), (0, 0, 255), 5)
            elif direction == "FORWARD":
                cv2.arrowedLine(frame, (center_line, roi_top + cy + 20), (center_line, roi_top + cy - 20), (0, 0, 255), 5)
                
    else:
        # 노랑색 라인이 감지되지 않을 때 STOP 표시
        direction = "STOP"
        cv2.putText(frame, "STOP", (width // 2 - 50, roi_top + roi_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if line_flag == True:
            MA.stop()
        line_flag = False


    return direction, line_flag

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    result,line_flag = process_frame(frame,line_flag)

    if result:
        print(result)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        MA.stop()
        break

cap.release()
cv2.destroyAllWindows()
MA.stop()
