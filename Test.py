import cv2
import time
from HandTrackingModule import HandDetector
import mediapipe as mp
import os


# Open the default camera (0). Change index to select a different camera.
cap = cv2.VideoCapture(0)

# Hand detection helper from our module
detector = HandDetector()

# Used for FPS calculation
p_time = 0


# Main loop: read frames, detect hands, display annotations and metrics
while True:
    success, img = cap.read()
    if not success:
        break

    # Detect hands and draw landmarks on `img` (in-place)
    img = detector.find_hands(img)

    # Retrieve pixel positions of landmarks for the first detected hand
    lm_list = detector.get_positions(img)

    # Simple gesture annotations: pinch, thumbs-up, middle-finger
    # These call detector methods that use the last `lm_list` values.
    if detector.is_pinching(img):
        cv2.putText(img, "PINCH", (10, 120), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    if detector.is_thumbs_up(img):
        cv2.putText(img, "Good Job!", (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Note: message here is offensive; consider changing to a neutral
    # debug message before sharing or deploying the app.
    if detector.is_middle_finger(img):
        cv2.putText(img, "(middle finger)", (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    # Show the number of fingers currently detected as 'up'
    lm_list = detector.get_positions(img)  # refresh to ensure latest
    if len(lm_list) != 0:
        fingers = detector.fingers_up()
        total_fingers = fingers.count(1)

        # Draw a filled rectangle as background for the finger-count text
        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(total_fingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)

    # Overlay landmark indices near their pixel positions (helpful for debugging)
    if len(lm_list) != 0:
        for id, lm in enumerate(lm_list):
            x, y = lm[1], lm[2]
            cv2.putText(img, str(id), (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
            # Also print to console for quick inspection during development
            print(f"Landmark {id}: ({x}, {y})")

    # FPS Calculation and display
    c_time = time.time()
    fps = 1 / (c_time - p_time) if p_time != 0 else 0
    p_time = c_time
    cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Show the annotated frame
    cv2.imshow("Module Test", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Redraw finger count once more before next loop iteration (optional)
    lm_list = detector.get_positions(img)
    if len(lm_list) != 0:
        fingers = detector.fingers_up()
        total_fingers = fingers.count(1)  # Count how many '1's are in the list
        # Draw the number on the frame as a persistent overlay
        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(total_fingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)