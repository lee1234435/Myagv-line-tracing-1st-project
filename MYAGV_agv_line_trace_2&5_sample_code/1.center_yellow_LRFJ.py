import cv2
import numpy as np

cap = cv2.VideoCapture(0)

def process_frame(frame):
    height, width, _ = frame.shape
    roi_height = int(height / 3)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (255, 0, 0), 2)
    
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100], dtype=np.uint8)
    upper_yellow = np.array([30, 255, 255], dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    cv2.imshow("yellow_mask", yellow_mask) 
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)


    yellow_binary_image = cv2.bitwise_and(binary_image, binary_image, mask=yellow_mask)

    contours, _ = cv2.findContours(yellow_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    direction = None
    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)
        
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = roi_height // 2
            
            center_line = width // 2
            if cx < center_line - 50:
                direction = "LEFT"
            elif cx > center_line + 50:
                direction = "RIGHT"
            else:
                direction = "FRONT"
                
            # 화면에 화살표 그리기
            if direction == "LEFT":
                cv2.arrowedLine(frame, (center_line, roi_top + cy), (center_line - 50, roi_top + cy), (0, 0, 255), 5)
            elif direction == "RIGHT":
                cv2.arrowedLine(frame, (center_line, roi_top + cy), (center_line + 50, roi_top + cy), (0, 0, 255), 5)
            elif direction == "FRONT":
                cv2.arrowedLine(frame, (center_line, roi_top + cy + 20), (center_line, roi_top + cy - 20), (0, 0, 255), 5)

    return direction

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    result = process_frame(frame)

    if result:
        print(result)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
