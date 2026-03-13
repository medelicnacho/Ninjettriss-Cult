import pyttsx3
import os
from pydub import AudioSegment

engine = pyttsx3.init()

voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 135)

# path to your txt file
txt_path = "doctrine.txt"

# read the text file
with open(txt_path, "r", encoding="utf-8") as file:
    text = file.read()

downloads = os.path.join(os.path.expanduser("~"), "Downloads")

wav_path = os.path.join(downloads, "Alien Weed Cult.wav")
mp3_path = os.path.join(downloads, "Alien Weed Cult.mp3")

# generate wav
engine.save_to_file(text, wav_path)
engine.runAndWait()

print("Saved WAV:", wav_path)

# convert wav → mp3
sound = AudioSegment.from_wav(wav_path)
sound.export(mp3_path, format="mp3")

print("Saved MP3:", mp3_path)
