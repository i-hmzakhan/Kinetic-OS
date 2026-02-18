import customtkinter as ctk
import json
import os

class SettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Mouse Settings")
        self.geometry("400x500")
        self.settings_path = "settings.json"
        
        # Default Settings
        self.current_settings = {
            "smoothening": 6,
            "scroll_speed": 3,
            "click_dist": 35,
            "frame_margin": 100
        }
        self.load_settings()

        # UI Elements
        ctk.CTkLabel(self, text="AI MOUSE CONTROLS", font=("Roboto", 20, "bold")).pack(pady=20)

        # Smoothening Slider
        ctk.CTkLabel(self, text="Smoothening (Higher = Slower/Stable)").pack()
        self.smooth_slider = ctk.CTkSlider(self, from_=1, to=20, command=self.save_settings)
        self.smooth_slider.set(self.current_settings["smoothening"])
        self.smooth_slider.pack(pady=10)

        # Scroll Speed Slider
        ctk.CTkLabel(self, text="Scroll Sensitivity").pack()
        self.scroll_slider = ctk.CTkSlider(self, from_=1, to=10, command=self.save_settings)
        self.scroll_slider.set(self.current_settings["scroll_speed"])
        self.scroll_slider.pack(pady=10)

        # Trackpad Margin Slider
        ctk.CTkLabel(self, text="Trackpad Size (Margin)").pack()
        self.margin_slider = ctk.CTkSlider(self, from_=20, to=250, command=self.save_settings)
        self.margin_slider.set(self.current_settings["frame_margin"])
        self.margin_slider.pack(pady=10)

        ctk.CTkButton(self, text="Apply & Save", command=self.save_settings).pack(pady=30)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                self.current_settings = json.load(f)

    def save_settings(self, _=None):
        self.current_settings = {
            "smoothening": int(self.smooth_slider.get()),
            "scroll_speed": int(self.scroll_slider.get()),
            "frame_margin": int(self.margin_sidebar.get())
        }
        with open(self.settings_path, "w") as f:
            json.dump(self.current_settings, f)

if __name__ == "__main__":
    app = SettingsApp()
    app.mainloop()