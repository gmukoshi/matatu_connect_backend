---
description: How to setup Ngrok for local M-Pesa callbacks
---
# Setting up Ngrok for M-Pesa Callbacks

Since Safaricom cannot access your `localhost` server, you need a "tunnel" to expose your local backend to the internet. Ngrok does this for you.

## 1. Install Ngrok
**If you are on Linux (Ubuntu/Debian):**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
```
*Alternatively, download it from [ngrok.com](https://ngrok.com/download).*

## 2. Authenticate (One time)
Sign up at [dashboard.ngrok.com](https://dashboard.ngrok.com/signup) to get your Authtoken.
```bash
ngrok config add-authtoken <YOUR_TOKEN_HERE>
```

## 3. Run Ngrok
In a **new terminal window**, run:
```bash
ngrok http 5000
```
*(Assuming your backend is running on port 5000)*

## 4. Get Your Public URL
Ngrok will show a forwarding URL like:
`Forwarding                    https://1234-56-78-90.ngrok-free.app -> http://localhost:5000`

Copy the `https://...` URL.

## 5. Update Backend Configuration
1. Open your `.env` file in the backend directory.
2. Find `MPESA_CALLBACK_URL`.
3. Update it to use your new Ngrok URL:
```ini
MPESA_CALLBACK_URL=https://1234-56-78-90.ngrok-free.app/api/payments/callback
```
*(Make sure to append `/api/payments/callback` at the end!)*

## 6. Restart Backend
You must restart your Flask server for the new `.env` changes to take effect.
```bash
# In your backend terminal:
Ctrl+C
python3 app.py  # or however you start it
```

## 7. Test
Make a payment in the app. The callback should now successfully reach your backend.
