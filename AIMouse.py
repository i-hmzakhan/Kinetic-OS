import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui
import json
import os

##########################
# Initial Defaults (Will be overwritten by settings.json)
wCam, hCam = 640, 480
frameR_top = 30      
frameR_bottom = 240  
frameR_side = 100
smoothening = 6      
scroll_multiplier = 3
click_dist = 35
##########################

pLocX, pLocY = 0, 0
cLocX, cLocY = 0, 0
frame_count = 0

def load_settings():
    """Reads settings from the JSON file created by the Settings GUI."""
    global smoothening, scroll_multiplier, frameR_side, click_dist
    settings_path = "settings.json"
    
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                config = json.load(f)
                smoothening = max(1, config.get("smoothening", 6))
                scroll_multiplier = config.get("scroll_speed", 3)
                frameR_side = config.get("frame_margin", 100)
                # Apply same margin to bottom for consistency if desired, 
                # or keep your custom bottom bias
        except Exception as e:
            print(f"Error loading settings: {e}")

# Initialize Camera and Detector
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.HandDetector(num_hands=1)
wScr, hScr = pyautogui.size()
pyautogui.PAUSE = 0

# Load initial settings
load_settings()

while True:
    success, img = cap.read()
    if not success: break
    
    # Reload settings every 30 frames to allow real-time GUI adjustments
    frame_count += 1
    if frame_count % 30 == 0:
        load_settings()

    img = cv2.flip(img, 1) 
    img = detector.find_hands(img)
    lmList = detector.get_positions(img)

    # Visual Trackpad Boundary
    cv2.rectangle(img, (frameR_side, frameR_top), 
                  (wCam - frameR_side, hCam - frameR_bottom), (255, 0, 255), 2)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]   # Index Tip
        x2, y2 = lmList[12][1:]  # Middle Tip
        
        fingers = detector.fingers_up()

        # 1. EXIT GESTURE: ONLY Pinky is up
        if fingers == [0, 0, 0, 0, 1]:
            print("Pinky Kill-Switch Triggered. Closing...")
            break

        # 2. SCROLL MODE: 4 Fingers up
        elif fingers == [0, 1, 1, 1, 1]:
            if pLocY != 0:
                diff = pLocY - y1
                if abs(diff) > 5:
                    pyautogui.scroll(int(diff * scroll_multiplier))
            
            cv2.putText(img, "SCROLLING", (wCam-200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
            pLocY = y1 

        # 3. CLICK GESTURE: Victory Sign
        elif fingers[1] == 1 and fingers[2] == 1:
            dist = np.hypot(x2 - x1, y2 - y1)
            if dist < click_dist: 
                cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                time.sleep(0.2) 

        # 4. MOVEMENT MODE: ONLY Index
        elif fingers == [0, 1, 0, 0, 0]:
            x3 = np.interp(x1, (frameR_side, wCam - frameR_side), (0, wScr))
            y3 = np.interp(y1, (frameR_top, hCam - frameR_bottom), (0, hScr))

            cLocX = pLocX + (x3 - pLocX) / smoothening
            cLocY = pLocY + (y3 - pLocY) / smoothening

            pyautogui.moveTo(cLocX, cLocY)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            pLocX, pLocY = cLocX, cLocY
            
    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()