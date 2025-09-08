import os
from dotenv import load_dotenv

load_dotenv()

admin_name = "YourName"

CONTACTS = {
    "mom": {"email": "mom@example.com"},
    "dad": {"email": "dad@example.com"},
    "sahil": {"email": "sahil@example.com"}
}

EMAIL_CONFIG = {
    "from_email": os.getenv("EMAIL_ADDRESS"),
    "app_password": os.getenv("EMAIL_APP_PASSWORD")
}
