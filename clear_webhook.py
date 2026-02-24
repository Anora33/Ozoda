import requests

BOT_TOKEN = "8582862021:AAFld1J9r9ZIjLm5KOJUHsCK8Me-ULcSsh0"

# Webhook ni o'chirish
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True")
print("Webhook o'chirildi:", response.json())

# Bot holatini tekshirish
info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
print("Webhook info:", info.json())