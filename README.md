# 🧠 Jaya-Shakti AI Assistant (Windows)

A voice-controlled desktop assistant powered by Google Gemini AI, designed to help with system tasks, media control, reminders, emails, WhatsApp, jokes, weather, news, and more — all through natural speech.

---

## 📦 Features

- 🎤 **Voice-controlled assistant** with wake words: `Jaya`, `Shakti`
- 🤖 **AI mode** (Gemini 1.5) for smart conversational answers
- 💻 **System control**: volume, brightness, lock, sleep, shutdown
- 🌦️ **Weather updates** via WeatherAPI
- 📰 **National & International news** via RSS feeds
- 📅 **Reminders** (add, list, clear)
- 💌 **Email sending** (via Gmail SMTP)
- 📱 **WhatsApp messaging** (via pywhatkit)
- 😂 **Joke generator** from 3 joke APIs
- 🔎 **Google Search** + **Wikipedia summarizer**
- 🧑 Customizable **user name** and **contacts**

---

## ⚙️ Setup Instructions (Windows)

### 1. 🧬 Clone or Download the Repo

# If using Git:
git clone https://github.com/your-username/jaya-shakti.git
cd jaya-shakti
Or download the ZIP from GitHub and extract it.


2. 🐍 Create a Virtual Environment (Optional but Recommended)
python -m venv venv
venv\Scripts\activate


3. 📥 Install Dependencies
pip install -r requirements.txt


4. 🧪 Create Config Files

⚠️ These files are excluded from GitHub for security.

🔐 Step 1: Copy Example Files
copy .env.example .env
copy config.example.py config.py

✍️ Step 2: Edit .env

Open .env and add your credentials:

GEMINI_API_KEY=your_google_gemini_api_key
WEATHER_API_KEY=your_weather_api_key
EMAIL_ADDRESS=your_gmail_address
EMAIL_APP_PASSWORD=your_gmail_app_password
ADMIN_NAME=YourName


💡 Don’t use your regular Gmail password — generate an App Password
 instead.


 ✍️ Step 3: Edit config.py

Add your contacts (email or WhatsApp number):

admin_name = "YourName"

CONTACTS = {
    "mom": {"email": "mom@example.com"},
    "dad": {"email": "dad@example.com"},
    "bestfriend": {"whatsapp": "+911234567890"}
}

EMAIL_CONFIG = {
    "from_email": "your_email@gmail.com",
    "app_password": "your_app_password"
}


5. 🚀 Run the Assistant
python main.py


Then say:

“Jaya” or “Jay” – to activate basic assistant
“Shakti” – to enter AI mode
“Stop Shakti” – to return to regular mode

| Category       | Commands                                            |
| -------------- | --------------------------------------------------- |
| 🌐 Web         | "Open YouTube", "Open Google", "Open ChatGPT"       |
| 🎵 Music       | "Play music", "Play \[song name]"                   |
| 💻 System      | "Volume up/down", "Mute/unmute", "Lock PC", "Sleep" |
| 🔆 Brightness  | "Brightness up/down"                                |
| 🕒 Time/Date   | "Speak time", "Speak date"                          |
| 📋 Reminders   | "Add reminder", "Show reminders", "Clear reminders" |
| 🌦️ Weather    | "Speak weather", "Speak weather in Delhi"           |
| 📰 News        | "National news", "International news"               |
| 😂 Jokes       | "Tell me a joke"                                    |
| 📬 Email       | "Send email"                                        |
| 📱 WhatsApp    | "Send WhatsApp"                                     |
| 🤖 AI Mode     | "Shakti", "Stop Shakti"                             |
| 🔍 Info Search | "Search Google for...", "In Wikipedia..."           |
| 👋 Exit/Sleep  | "Go to sleep", "Exit the program"                   |
| 👤 Update Name | "Change name", "Update name"                        |


🔐 Security Advice

✅ Keep .env and config.py private.
❌ Never upload these to GitHub or share publicly.
✔️ Use .env.example and config.example.py as templates for others.

📁 Project Structure
your_project/
├── main.py
├── system_control.py
├── config.py            # ❌ Don't upload
├── config.example.py    # ✅ Upload this
├── .env                 # ❌ Don't upload
├── .env.example         # ✅ Upload this
├── .gitignore           # ✅ Should ignore sensitive files
├── requirements.txt     # ✅ Upload this
└── README.md            # ✅ Upload this


🧠 Notes

This assistant works best on Windows.

Make sure microphone permissions are enabled.

For WhatsApp, you must be logged in to WhatsApp Web.

📜 License

MIT License

🙋‍♂️ Credits
Developed by Abhishek Sharma
Based on Python, Google Gemini AI, and various open-source APIs.



