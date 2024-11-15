import tkinter as tk
from tkinter import Label, Button, OptionMenu, StringVar, messagebox
import cv2
from PIL import Image, ImageTk
from gesture_recognition import predict_gesture
from keyboard_map import simulate_key_press, set_gesture_key_mapping
from pynput.keyboard import Key
import mediapipe as mp
import time

class GestureRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Recognition App")

        # Set the darker theme
        self.root.configure(bg="#2E2E2E")
        self.font_color = "#FFFFFF"
        self.bg_color = "#2E2E2E"
        self.button_color = "#555555"
        self.highlight_color = "#FF6347"

        # Video Feed Display
        self.video_label = Label(root, bg=self.bg_color)
        self.video_label.pack()

        # Gesture Display
        self.gesture_label = Label(root, text="Predicted Gesture: None", font=("Helvetica", 16), fg=self.font_color, bg=self.bg_color)
        self.gesture_label.pack()

        # Start/Stop Buttons
        self.start_button = Button(root, text="Start Video", command=self.start_video, bg=self.button_color, fg=self.font_color)
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = Button(root, text="Stop Video", command=self.stop_video, bg=self.button_color, fg=self.font_color)
        self.stop_button.pack(side="right", padx=10)

        # Gesture Mapping Settings
        self.gesture_var = StringVar(root)
        self.gesture_var.set("Select Gesture")
        self.gesture_menu = OptionMenu(root, self.gesture_var, *self.get_gesture_options())
        self.gesture_menu.config(bg=self.button_color, fg=self.font_color)
        self.gesture_menu.pack(padx=10, pady=10)

        self.key_var1 = StringVar(root)
        self.key_var1.set("Select Key 1")
        self.key_menu1 = OptionMenu(root, self.key_var1, *self.get_key_options())
        self.key_menu1.config(bg=self.button_color, fg=self.font_color)
        self.key_menu1.pack(padx=10, pady=10)

        self.key_var2 = StringVar(root)
        self.key_var2.set("Select Key 2")
        self.key_menu2 = OptionMenu(root, self.key_var2, *self.get_key_options())
        self.key_menu2.config(bg=self.button_color, fg=self.font_color)
        self.key_menu2.pack(padx=10, pady=10)

        self.set_button = Button(root, text="Set Mapping", command=self.set_mapping, bg=self.button_color, fg=self.font_color)
        self.set_button.pack(padx=10, pady=10)

        # Initialize MediaPipe for hand detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.cap = None
        self.update_video_feed_id = None
        self.frame_skip_rate = 5
        self.current_frame = 0
        self.last_executed_time = time.time()
        self.is_running = False  # Variable to track if the app is in running state

    def get_gesture_options(self):
        return ['call', 'dislike', 'fist', 'four', 'like', 'mute', 'ok', 'one', 'palm', 'peace', 'peace_inverted', 'rock', 'stop', 'stop_inverted', 'three', 'three2', 'two_up', 'two_up_inverted']

    def get_key_options(self):
        return ['Key.cmd', 'Key.media_volume_down', 'Key.media_play_pause', 'Key.ctrl', 'Key.shift', 'Key.esc', 'Key.media_volume_up', 'Key.media_volume_mute', 'Key.enter', 'Key.alt', 'Key.page_down', 'Key.page_up', 'Key.f1', 'Key.f2', 'Key.f3', 'Key.f4', 'Key.f5']

    def set_mapping(self):
        gesture = self.gesture_var.get()
        key1 = self.key_var1.get()
        key2 = self.key_var2.get()
        
        # Parse the key combination
        if not gesture or key1 == "Select Key 1":
            messagebox.showerror("Error", "Please select a gesture and at least one key.")
            return
        
        key_combination = self.parse_key(key1, key2)
        if key_combination is None:
            messagebox.showerror("Error", "Invalid key selected.")
            return

        set_gesture_key_mapping(gesture, key_combination)
        messagebox.showinfo("Success", f"Gesture '{gesture}' mapped to '{key1}' and '{key2}'")

    def parse_key(self, key_str1, key_str2):
        key_map = {
            'Key.cmd': Key.cmd,
            'Key.media_volume_down': Key.media_volume_down,
            'Key.media_play_pause': Key.media_play_pause,
            'Key.ctrl': Key.ctrl,
            'Key.shift': Key.shift,
            'Key.esc': Key.esc,
            'Key.media_volume_up': Key.media_volume_up,
            'Key.media_volume_mute': Key.media_volume_mute,
            'Key.enter': Key.enter,
            'Key.alt': Key.alt,
            'Key.page_down': Key.page_down,
            'Key.page_up': Key.page_up,
            'Key.f1': Key.f1,
            'Key.f2': Key.f2,
            'Key.f3': Key.f3,
            'Key.f4': Key.f4,
            'Key.f5': Key.f5,
        }
        
        keys = []
        if key_str1 in key_map:
            keys.append(key_map[key_str1])
        if key_str2 in key_map:
            keys.append(key_map[key_str2])

        return tuple(keys) if keys else None

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            results = self.hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                if self.current_frame % self.frame_skip_rate == 0:
                    predicted_gesture = predict_gesture(img)
                    
                    # Stop gesture
                    if predicted_gesture == 'stop':
                        self.is_running = False
                        self.gesture_label.config(text="Recognition Stopped")
                    
                    # Start gesture (stop_inverted)
                    elif predicted_gesture == 'stop_inverted':
                        self.is_running = True
                        self.gesture_label.config(text="Recognition Started")
                        self.last_executed_time = time.time()
                    
                    # Process gestures only if running
                    if self.is_running:
                        current_time = time.time()
                        if current_time - self.last_executed_time >= 2:  # 2-second gap
                            self.gesture_label.config(text=f"Predicted Gesture: {predicted_gesture}")
                            simulate_key_press(predicted_gesture)
                            self.last_executed_time = current_time

            self.current_frame += 1

        self.update_video_feed_id = self.root.after(10, self.update_video_feed)

    def start_video(self):
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.update_video_feed()
            self.root.geometry("")  # Reset window size to allow dynamic resizing

    def stop_video(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.update_video_feed_id:
            self.root.after_cancel(self.update_video_feed_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureRecognitionApp(root)
    root.mainloop()
