
import os
from dotenv import load_dotenv

# Explicitly load from the same location as main app
load_dotenv()

key = os.getenv("MPESA_CONSUMER_KEY")
secret = os.getenv("MPESA_CONSUMER_SECRET")

print("--- Credential Check ---")
if key == "your_consumer_key_here":
    print("KEY_STATUS: DEFAULT (Placeholder Detected)")
elif not key:
    print("KEY_STATUS: MISSING")
else:
    print("KEY_STATUS: SET (Length: {})".format(len(key)))
    if key.strip() != key:
        print("WARNING: KEY HAS WHITESPACE")

if secret == "your_consumer_secret_here":
    print("SECRET_STATUS: DEFAULT (Placeholder Detected)")
elif not secret:
    print("SECRET_STATUS: MISSING")
else:
    print("SECRET_STATUS: SET (Length: {})".format(len(secret)))
    if secret.strip() != secret:
        print("WARNING: SECRET HAS WHITESPACE")
