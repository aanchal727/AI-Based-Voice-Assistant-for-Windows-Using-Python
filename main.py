import librosa
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import noisereduce as nr
import webrtcvad
import speech_recognition as sr
import pyttsx3
import requests
from bs4 import BeautifulSoup
import datetime
import os
from time import sleep
import subprocess
import pyautogui

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice",voices[1].id)
# engine.setProperty("rate",100)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source :
        print("listening.....")
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1
        recognizer.energy_threshold = 100
        audio = recognizer.listen(source,0,4)
    try:
        print("Understanding...")
        query = recognizer.recognize_google(audio,language="en-in")
        print(F"You said : {query}\n")
    except Exception as e:
        print("Say that again")
        return "None"
    return query
    
def load_voice_file(file_path):
    y, sr_rate = librosa.load(file_path, sr=None)
    y = nr.reduce_noise(y=y, sr=sr_rate) 
    return y, sr_rate

# Voice activity detection (VAD)
def apply_vad(audio_segment):
    vad = webrtcvad.Vad()
    vad.set_mode(2) 
    samples = np.array(audio_segment.get_array_of_samples())
    return vad.is_speech(samples.tobytes(), audio_segment.frame_rate)

# Function to extract MFCC features
def extract_features(y, sr_rate):
    mfcc = librosa.feature.mfcc(y=y, sr=sr_rate, n_mfcc=13)
    return mfcc.T

# Function to enroll the user's voiceprint
def enroll_voiceprint(file_path):
    y, sr_rate = load_voice_file(file_path)
    features = extract_features(y, sr_rate)
    np.save("user_voiceprint.npy", features)
    print("Voiceprint has been saved.")

# Capture real-time voice input with noise reduction
def capture_voice_for_authentication():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 900  
    with sr.Microphone() as source:
        print("Calibrating microphone for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"Noise threshold set to {recognizer.energy_threshold}")
        print("Please say password for authentication...")
        audio = recognizer.listen(source,0,4)
        
        with open("temp_voice.wav", "wb") as f:
            f.write(audio.get_wav_data())
        
        y, sr_rate = load_voice_file("temp_voice.wav")
        os.remove("temp_voice.wav")
        return extract_features(y, sr_rate)

# Authenticate the user using DTW and VAD
def authenticate_user():
    if not os.path.exists("user_voiceprint.npy"):
        print("No voiceprint found. Please enroll first.")
        return False
    
    captured_features = capture_voice_for_authentication()
    stored_features = np.load("user_voiceprint.npy", allow_pickle=True)
    
    distance, _ = fastdtw(stored_features, captured_features, dist=euclidean)
    print(f"DTW Distance: {distance}")
    
    if distance < 90000:
        print("Voice Authentication successful.")
        speak("Voice Authentication successful.")
        return True
    else:
        print("Voice Authentication failed.")
        speak("Voice Authentication failed.")
        return False

# Secondary password-based authentication
def handle_secondary_authentication():
    correct_password = "1234"
    user_input = input("Please enter your password: ")
    
    if user_input == correct_password:
        print("Secondary authentication successful.")
        speak("Secondary authentication successful.")
        return True
    else:
        print("Secondary authentication failed. Access denied.")
        speak("Secondary authentication failed. Access denied.")
        return False

def alarm(query):
    timehere = open("Alarmtext.txt","a")
    timehere.write(query)
    timehere.close()
    subprocess.run(["python", "alarm.py"])


if __name__ == "__main__":
    
    enroll_voiceprint("Recording.wav")
    
    if authenticate_user() or handle_secondary_authentication():
        speak("Welcome back Yash, say key word ,'wake up', to start")
        while True:
            query=takeCommand().lower()
            if "wake up" in query:
                from Startby import greetme
                greetme()
                
                while True:
                    query = takeCommand().lower()
                    if "go to sleep" in query:
                        speak("Ok Yash , You can call me anytime")
                        break
                    elif "hello" in query:
                        speak("Hello Yash , How are you ?")
                    elif "i am fine" in query:
                        speak("That's Great")
                    elif "how are you" in query or "how r u" in query:
                        speak("Perfectly fine , thank you for asking")
                    elif "thank you" in query:
                        speak("Welcome Yash")
                        
                    elif "open" in query:
                        from AppOpening import openappweb
                        openappweb(query)
                    elif "close" in query:
                        from AppOpening import closeappweb
                        closeappweb(query)
                    elif "pause" in query:
                        pyautogui.press("k")
                        speak("Video paused")
                    elif "play" in query:
                        pyautogui.press("k")
                        speak("Video Played")
                    elif "mute" in query :
                        pyautogui.press("m")
                        speak("Video muted")
                    elif "unmute" in query:
                        pyautogui.press("m")
                        speak("Video unmuted")
                    elif "volume up" in query:
                        from volume import volumeup
                        speak("volume is increasing")
                        volumeup()
                    elif "volume down" in query:
                        from volume import volumedown
                        speak("volume is decreasing")
                        volumedown()
                        
                    elif "google" in query:
                        from SearchNow import searchGoogle
                        searchGoogle(query)
                        sleep(0.5)
                    elif "youtube" in query:
                        from SearchNow import searchYoutube
                        searchYoutube(query)
                        sleep(0.5)
                    elif "wikipedia" in query:
                        from SearchNow import searchWikipedia
                        searchWikipedia(query)
                        sleep(0.5)
                    elif "temperature" in query:
                        search = "temperature in pune"
                        url = f"https://www.google.com/search?q={search}"
                        recognizer = requests.get(url)
                        data = BeautifulSoup(recognizer.text,"html.parser")
                        temp = data.find("div", class_ = "BNeawe").text
                        speak(f"Current {search} is {temp}")
                    elif "weather" in query:
                        search = "weather in pune"
                        url = f"https://www.google.com/search?q={search}"
                        recognizer = requests.get(url)
                        data = BeautifulSoup(recognizer.text,"html.parser")
                        weather_description = data.find("div", class_="BNeawe tAd8D AP7Wnd").text
                        speak(f"Current {search} is {weather_description}")
                    elif "the time" in query:
                        strtime = datetime.datetime.now().strftime("%H:%M")
                        speak(f"Current time is {strtime}")
                    elif "set an alarm" in query:
                        print("input time example:- 10:10")
                        speak("set an alarm")
                        a = input("Please tell the time :- ")
                        alarm(a)
                        speak("alarm set successfully")
                    elif "remember that" in query:
                        remembermessage = query.replace("remember that","")
                        remembermessage = query.replace("remember","")
                        remembermessage = query.replace("buddy","")
                        speak("you told me "+remembermessage)
                        remember = open("Remember.txt","w")
                        remember.write(remembermessage)
                        remember.close()
                    elif "what do you remember" in query:
                        remember =open("Remember.txt","r")
                        speak("You told me "+remember.read())
                    elif "whatsapp" in query:
                        from Whatsapp import sendmessage
                        sendmessage()
                    
                    elif "bye" in query:
                        speak("bye-bye, system is turning off")
                        exit()
    
    else:
        speak("bye, system is turning off")
        exit()
        