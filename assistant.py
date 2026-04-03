import speech_recognition as sr
import pyttsx3
import os
import time

# ---------- VOICE SETUP ----------
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------- MICROPHONE SETUP ----------
recognizer = sr.Recognizer()

# Automatically pick the first available microphone
mic_index = 0
mic_name = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")
    if "microphone" in name.lower() or "headset" in name.lower():
        mic_index = i
        mic_name = name
        break

mic = sr.Microphone(device_index=mic_index)
speak(f"Jarvis online. Using microphone: {mic_name or 'default'}")

# ---------- FOLDER LOCATIONS TO SEARCH ----------
SEARCH_DIRECTORIES = [
    r"C:\Users\pcass\Desktop",
    r"C:\Users\pcass\Downloads",
    r"C:\Users\pcass\Documents",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Users\pcass\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc"
]

# ---------- FIXED PROGRAM LAUNCH PATHS ----------
PROGRAM_PATHS = {
    "wow": r"C:\Program Files (x86)\World of Warcraft\_retail_\Wow.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": r"C:\Users\pcass\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk"
}

# ---------- HELPER FUNCTION TO OPEN PROGRAMS OR FILES ----------
def open_program(name):
    name = name.lower().strip()
    
    # Check if the program is in the predefined paths
    if name in PROGRAM_PATHS:
        program_path = PROGRAM_PATHS[name]
        speak(f"Found {name}. Opening now.")
        print(f"Trying to open {program_path}")  # Debugging line
        os.system(f'start "" "{program_path}"')
        return

    # If the program wasn't found in predefined paths, search through directories
    for directory in SEARCH_DIRECTORIES:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if name in file.lower() and file.lower().endswith(('.exe', '.lnk', '.bat', '.docx', '.pdf')):
                    file_path = os.path.join(root, file)
                    speak(f"Found {name}. Opening now.")
                    print(f"Found {file_path}")  # Debugging line
                    os.system(f'start "" "{file_path}"')
                    return
    speak(f"Sorry, I couldn't find {name} anywhere on your computer.")

# ---------- MAIN LOOP ----------
while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("Listening... (adjusting for noise)")
            audio = recognizer.listen(source)
            print("Audio data captured")

        command_dict = recognizer.recognize_google(audio, show_all=True)

        if isinstance(command_dict, dict) and 'alternative' in command_dict:
            print("Command dict:", command_dict)

            # Extract best command
            best_command = None
            highest_confidence = 0.0
            for alt in command_dict['alternative']:
                conf = alt.get('confidence', 0)
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_command = alt.get('transcript', '').lower()

            print("Heard:", best_command)

            if not best_command:
                speak("Sorry, I couldn't hear anything clearly. Please try again.")
                continue

            # Only continue if the command starts with "Jarvis"
            if "jarvis" not in best_command:
                continue

            # Clean command to remove "Jarvis"
            command_clean = best_command.replace("jarvis", "").strip()

            # Handle the shutdown command explicitly
            if "shutdown" in command_clean or "close assistant" in command_clean:
                speak("Shutting down assistant.")
                break

            # Execute other commands
            open_program(command_clean)

    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that. Could you repeat?")
        continue

    except Exception as e:
        print("Error:", e)
        speak("An error occurred. Check the console.")
        time.sleep(1)
