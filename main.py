import time
import pyttsx3
import speech_recognition as sr
from googlesearch import search
import wikipedia
import webbrowser
import datetime
import requests
import google.generativeai as genai
import re
import importlib
import sys
import config
import os
import pyjokes
import feedparser
import random
import smtplib
import pywhatkit as kit
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from system_control import SystemControl

try:
    from twilio.rest import Client
    _has_twilio = True
except Exception:
    _has_twilio = False


sysctrl = SystemControl()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
engine = pyttsx3.init()
r = sr.Recognizer()
engine.setProperty('rate', 136)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
reminders = []

def show_user_manual():
    """Display the user manual in the terminal"""
    manual = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            JAYA-SHAKTI AI ASSISTANT                         ║
║                                USER MANUAL                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

BASIC USAGE:
  • Say "Jaya" or "Jay" to wake up the assistant
  • After activation, give voice commands
  • Say "Shakti" to activate AI-powered responses
  • Say "Stop Shakti" to return to basic commands

VOICE COMMANDS:
  • Open websites: "Open YouTube", "Open Google", "Open ChatGPT"
  • Media control: "Play music", "Play [song name]"
  • System control: 
      - "Volume up/down/mute/unmute"
      - "Brightness up/down"
      - "Lock PC", "Shutdown", "Restart", "Sleep PC"
  • Information:
      - "Speak time", "Speak date"
      - "Speak weather" or "Speak weather in [city]"
      - "National news", "International news"
      - "In Wikipedia [topic]"
  • Utilities:
      - "Add reminder [task]" or "Remember [task]"
      - "Show reminders", "Clear reminders"
      - "Tell me a joke"
      - "Search Google for [query]"
  • Communication:
      - "Send WhatsApp" (follow prompts)
      - "Send email" (follow prompts)
  • Settings:
      - "Update name" or "Change name" to change how assistant addresses you

ADVANCED FEATURES:
  • Jaya-Shakti AI mode: Activate with "Shakti" for AI-powered conversations
  • External actions: After AI responses, you can choose to save, email, or 
    WhatsApp the information

EXITING:
  • Say "Go to sleep" to put assistant in standby mode
  • Say "Exit the program" to completely quit

CONFIGURATION:
  • Edit config.py to add contacts for easy messaging
  • Set up environment variables in .env file:
      - EMAIL_ADDRESS: Your Gmail address
      - EMAIL_APP_PASSWORD: Gmail app password
      - GEMINI_API_KEY: Google Gemini API key
      - WEATHER_API_KEY: WeatherAPI.com key

TROUBLESHOOTING:
  • Ensure microphone permissions are granted
  • Check internet connection for AI and news features
  • For WhatsApp: Make sure you're logged in to WhatsApp Web
  • For email: Verify app password is correctly set up in Gmail

Press Enter to continue...
"""
    print(manual)
    input()

def get_news_rss(url, top_n=5):
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:top_n]]
    return headlines

def send_whatsapp(number, message):
    try:
        import pywhatkit
        speak(f"Sending WhatsApp message to {number}")
        pywhatkit.sendwhatmsg_instantly(number, message, wait_time=15, tab_close=True)
        print(f"WhatsApp message sent to {number}")
        return True
    except Exception as e:
        print("WhatsApp error:", e)
        if "qr" in str(e).lower() or "session" in str(e).lower():
            speak("It looks like you are not logged in to WhatsApp Web. Please scan the QR code in your browser.")
        else:
            speak("Sorry, I could not send the WhatsApp message due to an error.")
        return False


def speak_india_news():
    rss_url = "https://www.thehindu.com/news/national/feeder/default.rss"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        speak("Sorry, I could not fetch the news right now.")
        return
    
    speak("Here are the top news headlines from India:")
    
    for idx, entry in enumerate(feed.entries[:5], 1):
        headline = entry.title
        print(f"{idx}. {headline}")
        speak(f"{idx}. {headline}")

def save_to_file(query, reply, filename="shakti_saved_info.txt"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"--- {timestamp} ---\n")
            f.write(f"Query: {query}\n")
            f.write(f"Answer: {reply}\n\n")
        print(f"Info saved in {filename}")
        return True
    except Exception as e:
        print("File save error:", e)
        return False


def speak_international_news():
    url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    headlines = get_news_rss(url)
    speak("Here are the top international news headlines:")
    for idx, headline in enumerate(headlines, 1):
        speak(f"{idx}. {headline}")


def _resolve_contact(recipient: str) -> dict:
    recipient = recipient.strip()
    if "@" in recipient:
        return {"email": recipient}
    if recipient.startswith("+") and recipient[1:].isdigit():
        return {"whatsapp": recipient}
    return config.CONTACTS.get(recipient.lower(), {})

def send_email(to_email, subject, body):
    try:
        from_email = config.EMAIL_CONFIG["from_email"]
        password = config.EMAIL_CONFIG["app_password"]

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print("Email error:", e)
        return False
    
def get_joke():
    sources = ['pyjokes', 'icanhazdadjoke', 'officialjokeapi']
    choice = random.choice(sources)

    try:
        if choice == 'pyjokes':
            return pyjokes.get_joke()

        elif choice == 'icanhazdadjoke':
            response = requests.get(
                "https://icanhazdadjoke.com/",
                headers={"Accept": "application/json"},
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("joke", "No joke found.")

        elif choice == 'officialjokeapi':
            response = requests.get(
                "https://official-joke-api.appspot.com/random_joke",
                timeout=5
            )
            response.raise_for_status()
            joke_data = response.json()
            return f"{joke_data.get('setup')} ... {joke_data.get('punchline')}"

    except requests.RequestException as e:
        print("Joke API error:", e)
        return "Sorry, I couldn't fetch a joke right now."


def first_line_only(text):
    parts = re.split(r'[.\n]', text)
    if parts:
        return parts[0].strip()
    return text

def handle_external_action(query, reply):
    print("What do you want me to do with this info?")
    choice = input("Type 'save', 'email', 'whatsapp', or 'no': ").strip().lower()

    if choice == "save":
        save_to_file(query, reply)

    elif choice == "email":
        recipient = input("Enter recipient email address: ").strip()
        subject = input("Enter email subject: ").strip()
        custom_msg = input("What message do you want me to send in the email?\n(Type 'use reply' to send Shakti's answer): ").strip()
        if custom_msg.lower() == "use reply":
            custom_msg = reply
        send_email(recipient, subject, custom_msg)

    elif choice == "no":
        print("Skipping external action.")
    else:
        print("Invalid choice. Nothing done.")
        
def update_admin_name(new_name):
    env_file = ".env"
    lines = []
    updated = False

    # Read existing .env (if present)
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Rewrite with new ADMIN_NAME (or add if missing)
    with open(env_file, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("ADMIN_NAME="):
                f.write(f"ADMIN_NAME={new_name}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"ADMIN_NAME={new_name}\n")

    speak(f"Okay, I have updated the name. From now on, your name is {new_name}.")

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9.,!?': ]+", " ", text)
    return text.strip()

def ask_genai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Generative AI error:", e)
        
        # Fallback to Wikipedia
        try:
            result = wikipedia.summary(prompt, sentences=2)
            return result
        except Exception as e_wiki:
            print("Wikipedia error:", e_wiki)
            return "Sorry, I couldn't find any information on that topic."


from config import admin_name
def recognize_once(prompt=None, timeout=3, phrase_time_limit=4, retries=2):
    """
    Listen to user's voice once with retries.
    """
    if prompt:
        print(prompt)
    for attempt in range(retries + 1):
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = r.recognize_google(audio).lower()
                if text:
                    return text
            except sr.WaitTimeoutError:
                print("Listening timed out (no speech detected). Retrying...")
            except sr.UnknownValueError:
                print("Could not understand audio. Retrying...")
            except sr.RequestError:
                speak("Speech recognition service is unavailable. Check your internet")
                return None
            except Exception as e:
                print("Unexpected listening error:", e)
    return None


def greet():
    importlib.reload(config)
    hour = int(time.strftime("%H"))
    admin_name = config.admin_name

    if hour < 12:
        greet_msg = f"Good morning, {admin_name}!"
    elif hour < 18:
        greet_msg = f"Good afternoon, {admin_name}!"
    else:
        greet_msg = f"Good evening, {admin_name}!"

    print(greet_msg)

def add_reminder(task):
    reminders.append(task)
    speak(f"I have added the reminder: {task}")

def list_reminders():
    if not reminders:
        speak("You have no reminders right now.")
    else:
        speak("Here are your reminders:")
        for idx, rmd in enumerate(reminders, 1):
            speak(f"{idx}. {rmd}")
            print(f"{idx}. {rmd}")

def clear_reminders():
    reminders.clear()
    speak("All reminders have been cleared.")

def get_weather(city="Delhi"):
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key:
        return "Weather API key is missing. Please set it in your environment variables."

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city}

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()  # Raise error if status is not 200
        data = response.json()

        if "error" in data:
            return f"Sorry, I couldn't fetch the weather for {city}. {data['error']['message']}"

        city_name = data["location"]["name"]
        country = data["location"]["country"]
        temp = data["current"]["temp_c"]
        desc = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]

        return f"The weather in {city_name}, {country} is {desc} with a temperature of {temp}°C and humidity {humidity}%."

    except requests.RequestException as e:
        print("Weather API request error:", e)
        return "Sorry, there was a problem connecting to the weather service."

def speak(text):
    cleaned_text = clean_text(text)
    sentences = cleaned_text.split(". ")

    if len(sentences) <= 9:
        spoken_text = cleaned_text
        print(f"Jaya (spoken): {spoken_text}\n")
    else:
        spoken_text = ". ".join(sentences[:2]) + "."
        print(f"Jaya (spoken): {spoken_text} ...")

    engine.say(spoken_text)
    engine.runAndWait()


def wakeUp_Command():
    while True:
        wakeUp = recognize_once("Waiting for the call 'Jaya'...", timeout=5, phrase_time_limit=5)
        # Fix: check that wakeUp is not None, then test both "jaya" and "jay"
        if wakeUp and ('jaya' in wakeUp or 'jay' in wakeUp):
            print('Jaya Active..')
            speak('Jaya is Activated now')
            greet()

            while True:
                command = recognize_once("Give me a command\nSay 'Shakti' To Activate Jaya-Shakti AI Responses", 
                                         timeout=6, phrase_time_limit=6)
                if command:
                    print(f"{config.admin_name}: {command}\n")
                    result = processCommand(command)
                    if result == "sleep":
                        break
                else:
                    print("No command detected. Listening again...")
                time.sleep(0.3)
        else:
            time.sleep(0.3)


def processCommand(c):
    c = c.lower()
    if 'open youtube' in c:
        webbrowser.open('https://www.youtube.com')
        speak('Opening Youtube')
    elif 'open google' in c:
        webbrowser.open('https://www.google.com')
        speak('Opening Google')
    elif 'open helper' in c:
        webbrowser.open('https://www.chatgpt.com')
        speak('Opening Helper')
    elif 'open code with harry' in c:
        webbrowser.open('https://www.codewithharry.com')
        speak('Opening code with harry')
    elif "tell me a joke" in c:
        joke_text = get_joke()
        speak(joke_text)
    elif 'thank you' in c:
        speak("Most welcome, tell me if there is anything else I can help with")
    elif "volume up" in c:
        sysctrl.volume_up()
        speak("Volume increased.")
    elif "volume down" in c:
        sysctrl.volume_down()
        speak("Volume decreased.")
    elif "volume mute" in c:
        sysctrl.mute()
        speak("Volume muted.")
    elif "volume unmute" in c:
        sysctrl.unmute()
        speak("Volume unmuted.")
    elif "brightness up" in c:
        try:
            sysctrl.brightness_up()
            speak("Brightness increased.")
        except Exception as e:
            speak("Sorry, I couldn’t change brightness on this display.")
            print("Error:", e)
    elif "brightness down" in c:
        sysctrl.brightness_down()
        speak("Brightness decreased.")
    elif "lock pc" in c:
        sysctrl.lock()
        speak("Locking PC.")
    elif "shutdown" in c:
        speak("Are you sure you want to shut down?, Say 'yes ofcourse' or no")
        confirm = recognize_once(timeout=3, phrase_time_limit=3)
        if confirm and "yes" in confirm:
            sysctrl.shutdown()
    elif "restart" in c:
        speak("Restarting now.")
        sysctrl.restart()
    elif "sleep pc" in c:
        sysctrl.sleep()
        speak("Putting system to sleep.")     
    elif "shakti" in c:
        speak("Jaya-Shakti AI is now active. Say 'Stop Shakti' to exit.")
        print("Jaya-Shakti AI active. Say 'Stop Shakti' to exit.")

        miss_count = 0
        while True:
            query_input = recognize_once(timeout=8, phrase_time_limit=10)

            if not query_input:
                miss_count += 1
                if miss_count >= 3:
                    speak("I couldn't hear you, please try again.")
                    miss_count = 0
                continue
            else:
                miss_count = 0

            print(f"{config.admin_name} : {query_input}")

            if "stop shakti" in query_input.lower():
                speak("Stopping Jaya-Shakti AI. Waiting for wake word again.")
                print("Jaya-Shakti AI stopped.")
                return

            query = query_input.strip()
            reply = ask_genai(query)

            cleaned_text = clean_text(reply)
            sentences = cleaned_text.split(". ")

            # Speak only first 2-3 sentences if response is long
            if len(sentences) > 5:
                spoken_text = ". ".join(sentences[:3]) + "."
            else:
                spoken_text = cleaned_text

            print(f"Jaya-Shakti AI: {reply}")
            speak(spoken_text)
    elif "send whatsapp" in c:
        speak("Make sure you're logged in to WhatsApp Web.")
        speak("Whom should I send the WhatsApp message to? Please type the number with country code.")
        number = input("Enter phone number (with +91 etc): ").strip()

        if not number.startswith("+"):
            speak("Please include the country code.")
            return

        speak("Please speak your WhatsApp message now.")
        message = recognize_once(timeout=6, phrase_time_limit=8)

        if not message:
            speak("I could not understand. Type message manually or type 'exit'.")
            message = input("Enter message: ")

        speak(f"You said: {message}. Should I send it?")
        confirm = recognize_once(timeout=3, phrase_time_limit=3)

        if confirm and ("yes" in confirm.lower() or "of course" in confirm.lower()):
            success = send_whatsapp(number, message)
            if success:
                speak("WhatsApp message has been sent successfully.")
            else:
                speak("Sorry, I could not send the WhatsApp message.")
        else:
            speak("Message cancelled.")

    elif 'exit the program' in c:
        speak("Are you sure, you want to exit? Say 'yes ofcourse' or 'no'.")
        while True:
            print("Waiting for your response---")
            answer = recognize_once(timeout=4, phrase_time_limit=5)
            print(f"{config.admin_name} : {answer}")
            if answer:
                if 'yes' in answer:
                    speak('Exiting the program')
                    sys.exit()
                elif 'no' in answer:
                    speak('Welcome back to the program')
                    break
                else:
                    speak("Please say clearly 'yes ofcourse' or 'no'.")
            else:
                speak("I could not hear you. Please say 'yes ofcourse' or no.")
    elif "add reminder" in c or "remember" in c:
        task = c.replace("add reminder", "").replace("remember", "").strip()
        if not task:
            speak("What should I remind you about?")
            task_input = recognize_once(timeout=4, phrase_time_limit=5)
            if task_input:
                task = task_input
            else:
                speak("Sorry, I could not understand the reminder.")
                return
        add_reminder(task)
    elif "show reminders" in c or "list reminders" in c:
        list_reminders()
    elif "clear reminders" in c or "delete reminders" in c:
        clear_reminders()
    elif "speak weather" in c and "speak" in c:
        words = c.split()
        city = None
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = words[idx + 1]
        if not city:
            speak("Please tell me the city name.")
            city_input = recognize_once(timeout=4, phrase_time_limit=5)
            if city_input:
                city = city_input.title()
            else:
                speak("Sorry, I could not understand the city name.")
                return
        report = get_weather(city)
        print(report)
        speak(report)
    elif "speak time" in c and "speak" in c:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
        print(f"Time: {now}")
    elif "speak date" in c and "speak" in c:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today's date is {today}")
        print(f"Date: {today}")
    elif "national news" in c or "speak india news" in c:
        speak("Fetching top news headlines from India...")
        speak_india_news()

    elif "international news" in c or "speak world news" in c:
        speak("Fetching top international news headlines...")
        speak_international_news()
    elif "in wikipedia" in c:
        try:
            query = re.sub(r"\b(in )?wikipedia\b", "", c).strip()
            result = wikipedia.summary(query, sentences=2)
            speak(result)
            print(result)
        except Exception as e:
            speak("Sorry, I could not find anything on Wikipedia.")
            print("Error:", e)
    elif "play music" in c or "play song" in c:
        speak("Which song would you like me to play?")
        song = recognize_once(timeout=3, phrase_time_limit=5)
        if song:
            import pywhatkit
            speak(f"Playing {song} from YouTube")
            pywhatkit.playonyt(song)
        else:
            speak("Sorry, I could not understand the song name.")
    elif "update name" in c or "change name" in c:
        speak("Sure, what should I call you?")
        new_name_input = recognize_once(timeout=4, phrase_time_limit=5)
        if new_name_input:
            update_admin_name(new_name_input.title())
        else:
            speak("Sorry, I could not understand the name.")
    elif "send email" in c:
        speak("Whom should I send the email to? Please type the recipient email.")
        to_email = input("Enter Recipient Email: ").strip()

        speak(f"Got it. What is the subject?")
        subject = input("Enter Subject: ").strip()

        speak("What should I write in the message?")
        body = input("Enter Message Body: ").strip()

        success = send_email(to_email, subject, body)

        if success:
            speak("Email has been sent successfully.")
        else:
            speak("Sorry, I could not send the email.")

    elif "search google" in c:
        query = c.replace("search google for", "").replace("search google", "").strip()
        speak(f"Searching Google for {query}")
        print(f"Searching Google for {query}")
        try:
            results = list(search(query, num=3, stop=3, pause=2))
            if results:
                webbrowser.open(results[0])
                print("Opened:", results[0])
                for url in results[1:]:
                    print(url)
            else:
                speak("No results found.")
        except Exception as e:
            print("Google search error:", e)
            speak("Sorry, I couldn't perform the searched due to a network error.")

    elif "go to sleep" in c:
        speak("Okay, I will wait until you call me again.")
        return "sleep"
    else:
        speak("Sorry, Give a Proper Command")

if __name__ == "__main__":
    show_user_manual()  # Add this line to show the manual first
    print("Welcome to the Program Jaya-Shakti")
    speak("Initializing Jaya")
    greet()

    while True:
        command = recognize_once("Listening for your command...", timeout=5, phrase_time_limit=6)

        if command:
            print(f"{config.admin_name}: {command}\n")
            result = processCommand(command)
            if result == "sleep":
                speak("Okay, waiting for your next command.")
                continue
        else:
            # If nothing is heard, just loop again without errors
            print("No command detected. Listening again...")
        
        time.sleep(0.3)

