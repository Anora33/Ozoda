import os
from dotenv import load_dotenv
import requests

# .env faylini yuklash
load_dotenv()

# Tokenni olish
token = os.getenv('BOT_TOKEN')

print("=" * 50)
print("TOKEN TEKSHIRISH DASTURI")
print("=" * 50)

print(f"\n📁 Joriy papka: {os.getcwd()}")
print(f"📄 .env fayli bormi: {'HA' if os.path.exists('.env') else 'YOQ'}")

if os.path.exists('.env'):
    print("\n📝 .env fayli ichidagi birinchi qator:")
    with open('.env', 'r') as f:
        first_line = f.readline().strip()
        print(f"   {first_line}")

print(f"\n🔑 BOT_TOKEN: {token[:10]}...{token[-5:] if token else 'TOPILMADI'}")

if token:
    print(f"📏 Token uzunligi: {len(token)} belgi")

    print("\n📡 Telegram API ga so'rov yuborilmoqda...")

    # Telegram API orqali tekshirish
    url = f"https://api.telegram.org/bot{token}/getMe"

    try:
        response = requests.get(url, timeout=10)
        print(f"📨 Javob status kodi: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot = data['result']
                print("\n" + "=" * 50)
                print("✅ BOT MUVAFFAQIYATLI ISHLADI!")
                print("=" * 50)
                print(f"🤖 Bot username: @{bot['username']}")
                print(f"🆔 Bot ID: {bot['id']}")
                print(f"📛 Bot nomi: {bot.get('first_name', 'Noma')}")
                print(f"🌐 Til: {bot.get('language_code', 'Noma')}")
                print("=" * 50)
                print("\n✨ Endi asosiy botni ishga tushirishingiz mumkin!")
            else:
                print(f"\n❌ Xatolik: {data}")
        elif response.status_code == 401:
            print("\n❌ XATOLIK: Token noto'g'ri yoki o'chirilgan!")
            print("   @BotFather ga borib yangi token oling:")
            print("   1. Telegramda @BotFather ga yozing")
            print("   2. /mybots ni bosing")
            print("   3. @taksi24_uz_bot ni tanlang")
            print("   4. API Token -> Revoke current token")
            print("   5. Yangi token oling va .env fayliga yozing")
        else:
            print(f"\n❌ Xatolik {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ INTERNET XATOSI: Internetga ulanish yo'q!")
    except requests.exceptions.Timeout:
        print("\n❌ VAQT XATOSI: Telegram server javob bermadi!")
    except Exception as e:
        print(f"\n❌ KUTILMAGAN XATOLIK: {e}")

else:
    print("\n❌ TOKEN TOPILMADI!")
    print("\nSabablari:")
    print("1. .env fayli mavjud emas")
    print("2. .env faylida BOT_TOKEN=... qatori yo'q")
    print("3. .env fayli noto'g'ri joyda")
    print("\nYechim:")
    print("1. .env fayli yarating:")
    print("   BOT_TOKEN=8582862021:AAGvDQtO0bDhyev_3AND2PpWzt5zYsPMLkk")
    print("2. Faylni saqlang")
    print("3. Qaytadan ishga tushiring")

print("\n" + "=" * 50)