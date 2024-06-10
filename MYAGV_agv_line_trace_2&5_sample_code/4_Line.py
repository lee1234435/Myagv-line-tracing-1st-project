import cv2
import numpy as np
from pymycobot.myagv import MyAgv
import threading
import time

# MyAgv 占쏙옙체 占쏙옙占쏙옙. 占쏙옙트占쏙옙 占쏙옙占?占쌈듸옙占쏙옙 占쏙옙占쏙옙 환占썸에 占승곤옙 占쏙옙占쏙옙占쌔억옙 占쌌니댐옙.
agv = MyAgv("/dev/ttyAMA2", 115200)

def process_frame(frame):
    height, width, _ = frame.shape
    roi_height = int(height / 3)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]
    
    # 화占쏙옙 占쌩앙울옙 占쏙옙 占쌓몌옙占쏙옙
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 2)
    
    # 占쏙옙占?占쏙옙占쏙옙占쏙옙 占쏙옙占쏙옙 HSV 占쏙옙환 占쏙옙 占쏙옙占쏙옙킹
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_white = np.array([20, 100, 100], dtype=np.uint8)
    upper_white = np.array([30, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    # 占쏙옙占쏙옙화
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    yellow_binary_image = cv2.bitwise_and(binary_image, binary_image, mask=white_mask)

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

    return None

def turn_left(MA):
    print("Turning LEFT")
    MA.go_ahead(1)
    time.sleep(1)
    MA.counterclockwise_rotation(1) #CCW
    time.sleep(1)

def turn_right(MA):
    print("Turning RIGHT")
    MA.go_ahead(1)
    time.sleep(1)
    MA.clockwise_rotation(1) #CC
    time.sleep(1)
    
    
def camera_thread():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error")
            break

        result = process_frame(frame)
        if result:
            print(result)  # 占싱뱄옙 占쏙옙占썩서 占쏙옙占쏙옙占?占쏙옙占쏙옙構占?占쌍쏙옙占싹댐옙.
            if result == "LEFT":
                threading.Timer(0.3, lambda: turn_left(agv)).start()
            elif result == "RIGHT":
                threading.Timer(0.3, lambda: turn_right(agv)).start()



        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 占쏙옙占쏙옙 占쏙옙占쏙옙占썲에占쏙옙 카占쌨띰옙 占쏙옙占쏙옙占쏙옙 占쏙옙占쏙옙
camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()

# 카占쌨띰옙 占쏙옙占쏙옙占썲가 占쏙옙占쏙옙占?占쏙옙占쏙옙占쏙옙 占쏙옙占?camera_thread.join()
