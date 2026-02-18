import customtkinter as ctk
import cv2
from PIL import Image
import HandTrackingModule as htm
import os
import datetime

# Appearance Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HandTrackingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Hand Tracking & Data Logger")
        self.geometry("1200x700")

        # Path Setup
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.current_dir, "hand_data_log.csv")

        # Initialize Hand Detector
        self.detector = htm.HandDetector(num_hands=2)
        self.cap = cv2.VideoCapture(0)
        self.is_recording = False

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # 1. Left Sidebar (Controls)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="CONTROLS", font=("Roboto", 18, "bold")).pack(pady=20)
        
        self.count_label = ctk.CTkLabel(self.sidebar, text="Fingers: 0", font=("Roboto", 40))
        self.count_label.pack(pady=20)

        self.pinch_status = ctk.CTkLabel(self.sidebar, text="PINCH: OFF", text_color="gray")
        self.pinch_status.pack(pady=5)

        self.thumb_status = ctk.CTkLabel(self.sidebar, text="THUMBS UP: OFF", text_color="gray")
        self.thumb_status.pack(pady=5)

        self.record_btn = ctk.CTkButton(self.sidebar, text="START LOGGING", fg_color="green", command=self.toggle_recording)
        self.record_btn.pack(pady=30, padx=10)

        self.quit_btn = ctk.CTkButton(self.sidebar, text="EXIT", fg_color="transparent", border_width=1, command=self.close_app)
        self.quit_btn.pack(side="bottom", pady=20)

        # 2. Center Area (Video Feed)
        self.video_container = ctk.CTkFrame(self)
        self.video_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_container, text="")
        self.video_label.pack(expand=True)

        # 3. Right Sidebar (Landmark Coordinates)
        self.data_sidebar = ctk.CTkFrame(self, width=250)
        self.data_sidebar.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.data_sidebar, text="LANDMARK POSITIONS", font=("Roboto", 14, "bold")).pack(pady=10)
        
        self.coord_box = ctk.CTkTextbox(self.data_sidebar, width=230, height=550, font=("Courier", 12))
        self.coord_box.pack(padx=10, pady=10)

        self.update_frame()

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.configure(text="STOP LOGGING", fg_color="red")
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w") as f:
                    f.write("timestamp,gesture,landmarks\n")
        else:
            self.record_btn.configure(text="START LOGGING", fg_color="green")

    def update_frame(self):
        success, img = self.cap.read()
        if success:
            img = self.detector.find_hands(img)
            lm_list = self.detector.get_positions(img)

            coord_text = "ID |  X  |  Y \n------------------\n"
            
            if len(lm_list) != 0:
                # Update Finger Count & Gestures
                fingers = self.detector.fingers_up()
                self.count_label.configure(text=f"Fingers: {fingers.count(1)}")

                # Update Gesture UI
                is_pinching = self.detector.is_pinching(img)
                self.pinch_status.configure(text="PINCH: ACTIVE" if is_pinching else "PINCH: OFF",
                                            text_color="#1fcf8d" if is_pinching else "gray")
                
                self.thumb_status.configure(text="THUMBS UP: ACTIVE" if self.detector.is_thumbs_up(img) else "THUMBS UP: OFF",
                                            text_color="#1fcf8d" if self.detector.is_thumbs_up(img) else "gray")

                # Build Coordinate Table String
                for lm in lm_list:
                    coord_text += f"{lm[0]:02d} | {lm[1]:03d} | {lm[2]:03d}\n"

                # Handle Data Logging
                if is_pinching and self.is_recording:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")
                    flat_data = ",".join([f"{l[1]}:{l[2]}" for l in lm_list])
                    with open(self.log_file, "a") as f:
                        f.write(f"{timestamp},pinch,{flat_data}\n")

            # Update Scrollbox with coords
            self.coord_box.delete("1.0", "end")
            self.coord_box.insert("1.0", coord_text)

            # Convert to GUI Image
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk

        self.after(10, self.update_frame)

    def close_app(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = HandTrackingApp()
    app.mainloop()