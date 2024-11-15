from pynput.keyboard import Controller, Key

keyboard = Controller()

# Default gesture-to-key mappings
gesture_to_key = {
    'call': (Key.cmd, Key.shift, 'a'),              # Custom action for 'call'
    
    # System Controls
    'four': (Key.ctrl, Key.shift, Key.esc),         # Open Task Manager
    'rock': (Key.cmd, 'l'),                         # Lock screen
    'three': (Key.alt, Key.tab),                    # Switch window   
    'three2': Key.page_down,                        # Scroll Down
    'ok': Key.enter,                                # Enter/Select
    'fist': (Key.alt, Key.f4),                         # Windows search
    
    # Media Controls
    'mute': Key.media_volume_mute,                  # Mute/Unmute
    'dislike': Key.media_volume_down,               # Volume Down
    'like': Key.media_volume_up,                    # Volume Up
    'palm': Key.media_play_pause,                   # Play/Pause
    'peace': Key.media_next,                        # Next Track
    'peace_inverted': Key.media_previous,           # Previous Track
    
    # Browser Controls
    'one': (Key.ctrl, 't'),                         # New Tab
    'two_up': Key.page_down,                        # Page Down
    'two_up_inverted': Key.page_up                  # Page Up
}

# Function to dynamically update gesture-to-key mappings
def set_gesture_key_mapping(gesture_name, key_combination):
    global gesture_to_key
    gesture_to_key[gesture_name] = key_combination

def simulate_key_press(gesture_name):
    if gesture_name in gesture_to_key:
        key = gesture_to_key[gesture_name]
        if isinstance(key, tuple):
            for k in key:
                keyboard.press(k)
            for k in key:
                keyboard.release(k)
        else:
            keyboard.press(key)
            keyboard.release(key)