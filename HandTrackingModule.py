import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time
import math

"""
HandTrackingModule.py
---------------------
Lightweight wrapper around MediaPipe's Hand Landmarker for simple
hand-detection use-cases. Provides:
 - `HandDetector` class to detect hands and extract landmark positions
 - Helper methods to recognize simple gestures (pinch, thumbs-up,
     middle-finger) and to determine which fingers are up

Notes:
 - MediaPipe provides normalized landmark coordinates in [0,1]. This
     module converts them to pixel coordinates using the image shape.
 - The module expects a `hand_landmarker.task` model file to be in the
     same directory as this script.
"""


class HandDetector:
        """Detector utility built on top of MediaPipe Hand Landmarker.

        Parameters
        - num_hands: maximum number of hands to detect in the frame.
        - min_detection_confidence: placeholder for compatibility; the
            `HandLandmarkerOptions` used below can accept more parameters.

        Attributes
        - `detector`: the MediaPipe HandLandmarker instance
        - `results`: last detection results returned by the detector
        - `lm_list`: last extracted list of landmark pixel coordinates
        - `connections`: list of landmark index pairs used to draw the
            skeleton (lines between joints)
        """

        def __init__(self, num_hands=2, min_detection_confidence=0.5):
                # Find the model file that MediaPipe will load. This expects the
                # `hand_landmarker.task` file to live next to this script.
                current_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(current_dir, 'hand_landmarker.task')

                # Create base options and hand landmarker options. We only set
                # `num_hands` here; other options can be supplied if needed.
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=num_hands)

                # Build the detector and initialize storage fields used by the
                # rest of the helper methods.
                self.detector = vision.HandLandmarker.create_from_options(options)
                self.results = None
                # `lm_list` will contain lists like [id, x_pixel, y_pixel]
                self.lm_list = []

                # Connections define which landmark pairs should be connected
                # when drawing the hand skeleton. Indexes refer to MediaPipe's
                # 21 hand landmarks (0..20).
                self.connections = [
                        # Thumb
                        (0, 1), (1, 2), (2, 3), (3, 4),
                        # Index Finger
                        (0, 5), (5, 6), (6, 7), (7, 8),
                        # Middle Finger
                        (9, 10), (10, 11), (11, 12),
                        # Ring Finger
                        (13, 14), (14, 15), (15, 16),
                        # Pinky
                        (0, 17), (17, 18), (18, 19), (19, 20),
                        # Palm/Knuckle connections
                        (5, 9), (9, 13), (13, 17)
                ]

        def find_hands(self, img, draw=True):
            """Run hand detection on the provided BGR image.

            - Converts the BGR `img` (OpenCV default) to RGB and constructs a
            MediaPipe `Image` for detection.
            - Stores the raw `results` object on `self.results` for later use.
            - If `draw` is True, overlays the skeleton connections and landmark
            points onto the original image and returns the annotated image.

            Returns the (possibly annotated) image.
            """
            # MediaPipe expects RGB images; OpenCV uses BGR by default.
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            # Run detection and keep the result for other helpers
            self.results = self.detector.detect(mp_image)

            # If drawing is requested and we have detected hand landmarks,
            # draw skeleton lines first and then the joint dots.
            if draw and self.results.hand_landmarks:
                for hand_lms in self.results.hand_landmarks:
                    h, w, c = img.shape

                    # Draw connections: map normalized coords to pixel coords
                    # Then draw a line between the pair of points.
                    for connection in self.connections:
                        p1_idx, p2_idx = connection
                        x1, y1 = int(hand_lms[p1_idx].x * w), int(hand_lms[p1_idx].y * h)
                        x2, y2 = int(hand_lms[p2_idx].x * w), int(hand_lms[p2_idx].y * h)
                        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red lines

                    # Draw the landmark points (small filled circles). The wrist
                    # (index 0) is emphasized with a larger green dot.
                    for id, lm in enumerate(hand_lms):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)  # Purple joints
                        if id == 0:
                            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)  # Wrist
            return img

        def get_positions(self, img, hand_no=0):
            """Extract pixel positions for landmarks of a detected hand.

            - `hand_no` chooses which detected hand (0 is the first).
            - Returns a list of `[id, x_pixel, y_pixel]` entries. If no hands
            were detected or `hand_no` is out-of-range, returns an empty list.
            """
            self.lm_list = []
            if self.results.hand_landmarks:
                h, w, c = img.shape
                if hand_no < len(self.results.hand_landmarks):
                    my_hand = self.results.hand_landmarks[hand_no]
                    for id, lm in enumerate(my_hand):
                        # Convert normalized (0..1) coordinates to pixel coords
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        self.lm_list.append([id, cx, cy])
            return self.lm_list

        def is_pinching(self, img, draw=True):
            """Return True when thumb tip (landmark 4) and index tip
            (landmark 8) are close enough to be considered a pinch.

            - Uses an empirical pixel-distance threshold (35 px). This value
            may need tuning for different resolutions and camera distances.
            - If `draw` is True, show a green circle between the two tips.
            """
            if len(self.lm_list) >= 9:
                x1, y1 = self.lm_list[4][1], self.lm_list[4][2]  # Thumb tip
                x2, y2 = self.lm_list[8][1], self.lm_list[8][2]  # Index tip
                distance = math.hypot(x2 - x1, y2 - y1)
                if distance < 35:
                    if draw:
                        cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 15, (0, 255, 0), cv2.FILLED)
                    return True
            return False
    
        def is_thumbs_up(self, img, draw=True):
            """Basic thumbs-up detection.

            Heuristic:
            - Thumb tip (4) is above the IP joint (3) -> suggests thumb extended
            - All other fingers' tips (8,12,16,20) are below their PIP joints
            -> suggests those fingers are folded down

            Note: For mirrored input (left vs right hand or flipped camera),
            some X-based heuristics may need flipping. This implementation
            uses only vertical comparisons for the thumb.
            """
            if len(self.lm_list) >= 21:
                thumb_up = self.lm_list[4][2] < self.lm_list[3][2]

                fingers_down = (
                    self.lm_list[8][2] > self.lm_list[6][2] and
                    self.lm_list[12][2] > self.lm_list[10][2] and
                    self.lm_list[16][2] > self.lm_list[14][2] and
                    self.lm_list[20][2] > self.lm_list[18][2]
                )

                if thumb_up and fingers_down:
                    if draw:
                        # Emphasize the thumb tip visually
                        cv2.circle(img, (self.lm_list[4][1], self.lm_list[4][2]), 15, (0, 255, 0), cv2.FILLED)
                    return True
            return False

        def is_middle_finger(self, img, draw=True):
            """Detect if the middle finger alone is extended.

            Heuristic: middle tip (12) above its PIP (10) while the other
            finger tips are below their corresponding PIP joints.
            """
            if len(self.lm_list) >= 21:
                middle_up = self.lm_list[12][2] < self.lm_list[10][2]

                others_down = (
                    self.lm_list[8][2] > self.lm_list[6][2] and
                    self.lm_list[16][2] > self.lm_list[14][2] and
                    self.lm_list[20][2] > self.lm_list[18][2]
                )

                if middle_up and others_down:
                    if draw:
                        # Emphasize middle fingertip with a red marker
                        cv2.circle(img, (self.lm_list[12][1], self.lm_list[12][2]), 15, (0, 0, 255), cv2.FILLED)
                    return True
            return False
        
        def fingers_up(self):
            """Return a 5-element list indicating which fingers are up.

            Format: [thumb, index, middle, ring, pinky] where each element is
            1 if the finger is considered 'up' and 0 otherwise.

            Thumb detection uses X-coordinate comparison (tip vs joint).
            Other fingers use vertical comparisons (tip vs PIP joint) because
            an extended finger will have a tip with smaller Y value (higher
            on the image) than its PIP joint.
            """
            fingers = []
            if len(self.lm_list) != 0:
                # Thumb: compare X coordinates of tip (4) and its previous joint (3)
                # Note: This assumes a right-hand orientation in the image.
                if self.lm_list[4][1] > self.lm_list[3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Other fingers: Tips [8, 12, 16, 20] compared to PIP joints
                tip_ids = [8, 12, 16, 20]
                for id in tip_ids:
                    # If tip Y < PIP Y, the finger is UP (Y decreases upward)
                    if self.lm_list[id][2] < self.lm_list[id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

            return fingers

