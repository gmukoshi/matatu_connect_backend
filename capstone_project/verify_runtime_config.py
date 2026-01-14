from app import create_app

app = create_app()

print("--- RUNTIME CONFIG ---")
print(f"MPESA_CALLBACK_URL: {app.config.get('MPESA_CALLBACK_URL')}")
print("----------------------")
