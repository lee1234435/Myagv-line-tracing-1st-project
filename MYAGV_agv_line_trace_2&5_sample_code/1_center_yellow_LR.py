import cv2
import numpy as np

cap = cv2.VideoCapture(0)

def process_frame(frame):
    height, width, _ = frame.shape
    roi_height = int(height / 3)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    # 그레이스케일 이미지에서 중앙 선 그리기
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 2)

    # Define lower and upper bounds for the color yellow in HSV space
    # Hue range for yellow is approximately 25 to 35 degrees, but it's scaled to 0-180 in OpenCV, so we divide by 2
    lower_yellow = np.array([20, 100, 100], dtype=np.uint8)  # Adjust saturation and value as needed
    upper_yellow = np.array([30, 255, 255], dtype=np.uint8)  # Adjust saturation and value as needed
  
    # Assuming 'frame' is your input BGR image
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    cv2.imshow("yellow_mask", yellow_mask) 

    # To see the result
    # cv2.imshow("yellow_mask", yellow_mask) 

    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)# print (len(contours))
   
    # 윤곽선 검출 및 처리 
    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)

        # 물체의 중심 계산 및 결과 출력 
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            
            center_line = width // 2
            if cx < center_line - 50:
                return "LEFT"
            elif cx > center_line + 50:
                return "RIGHT"

    return None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    result = process_frame(frame)

    if result:
        print(result)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(2000) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()