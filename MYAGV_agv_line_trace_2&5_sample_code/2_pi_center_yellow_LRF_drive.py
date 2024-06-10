import cv2
import numpy as np
from pymycobot.myagv import MyAgv
import threading
import time

agv = MyAgv("/dev/ttyAMA2", 115200)

def process_frame(frame):
    height, width, _ = frame.shape
    roi_height = int(height / 3)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    # 그레이스케일 이미지에서 중앙 선 그리기
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 2)

    # Define lower and upper bounds for the color yellow in HSV space
    # Hue range for yellow is approximately 25 to 35 degrees, but it's scaled to 0-180 in OpenCV, so we divide by 2
    
    # Assuming 'frame' is your input BGR image
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100], dtype=np.uint8)  # Adjust saturation and value as needed
    upper_yellow = np.array([30, 255, 255], dtype=np.uint8)  # Adjust saturation and value as needed
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    cv2.imshow("yellow_mask", yellow_mask) 

    # To see the result
    # cv2.imshow("yellow_mask", yellow_mask) 
    
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    yellow_binary_image = cv2.bitwise_and(binary_image, binary_image, mask=yellow_mask)

    contours, _ = cv2.findContours(yellow_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)

        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            center_line = width // 2
            if cx < center_line - 50:
                return "LEFT"
            elif cx > center_line + 50:
                return "RIGHT"
            else:
                return "FORWARD"

    return None

def camera_thread():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error")
            break

        result = process_frame(frame)
        if result:
            print(result)
            if result == "LEFT":
                agv.counterclockwise_rotation(1)
                time.sleep(1)
    
            elif result == "RIGHT":
                agv.clockwise_rotation(1)
                time.sleep(1)

            elif result == "FORWARD":
                agv.go_ahead(5)
                time.sleep(1)

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    agv.stop()
    cap.release()
    cv2.destroyAllWindows()

# 메인 스레드에서 카메라 스레드 실행
camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()

# 카메라 스레드가 종료될 때까지 대기
camera_thread.join()