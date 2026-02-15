import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import sqlite3
import random

# ============================================
# 1️⃣ BOT TOKENI
# ============================================
TOKEN = "8582862021:AAG2AybkC2Dg4K-gBLpHUgrfJu1OkBxog2w"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ============================================
# 2️⃣ MA'LUMOTLAR BAZASI
# ============================================
def init_db():
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()

    # Mijozlar
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     user_id
                     INTEGER
                     PRIMARY
                     KEY,
                     name
                     TEXT,
                     phone
                     TEXT,
                     created_at
                     TIMESTAMP
                 )''')

    # Haydovchilar
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (
                     driver_id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     telegram_id
                     INTEGER
                     UNIQUE,
                     full_name
                     TEXT,
                     phone
                     TEXT,
                     car_model
                     TEXT,
                     car_number
                     TEXT,
                     rating
                     REAL
                     DEFAULT
                     5.0,
                     is_available
                     BOOLEAN
                     DEFAULT
                     1,
                     total_trips
                     INTEGER
                     DEFAULT
                     0,
                     created_at
                     TIMESTAMP
                 )''')

    # Buyurtmalar
    c.execute('''CREATE TABLE IF NOT EXISTS orders
    (
        order_id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        user_id
        INTEGER,
        driver_id
        INTEGER
        DEFAULT
        NULL,
        user_name
        TEXT,
        user_phone
        TEXT,
        from_address
        TEXT,
        to_address
        TEXT,
        price
        INTEGER,
        distance
        REAL,
        status
        TEXT
        DEFAULT
        'yangi',
        created_at
        TIMESTAMP,
        accepted_at
        TIMESTAMP,
        completed_at
        TIMESTAMP,
        FOREIGN
        KEY
                 (
        user_id
                 ) REFERENCES users
                 (
                     user_id
                 ),
        FOREIGN KEY
                 (
                     driver_id
                 ) REFERENCES drivers
                 (
                     driver_id
                 ))''')

    conn.commit()
    conn.close()


init_db()


# ============================================
# 3️⃣ HOLATLAR (FSM)
# ============================================
class RegisterState(StatesGroup):
    name = State()
    phone = State()
    car_model = State()
    car_number = State()


class OrderState(StatesGroup):
    user_name = State()
    user_phone = State()
    from_address = State()
    to_address = State()
    confirm = State()


# ============================================
# 4️⃣ NARX HISOBI
# ============================================
def calculate_price(from_addr, to_addr):
    distance = random.randint(3, 15)
    return distance

# ============================================
# 5️⃣ KLAVIATURALAR
# ============================================
def main_menu():
    kb = [
        [KeyboardButton(text="🚖 Buyurtma berish")],
        [KeyboardButton(text="📋 Mening buyurtmalarim"), KeyboardButton(text="🚗 Haydovchi menyusi")],
        [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="⚙️ Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def driver_menu():
    kb = [
        [KeyboardButton(text="✅ Yangi buyurtmalar"), KeyboardButton(text="📊 Mening statistika")],
        [KeyboardButton(text="🔄 Holatni o'zgartirish"), KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def phone_kb():
    kb = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="🔙 Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def cancel_kb():
    kb = [[KeyboardButton(text="❌ Bekor qilish")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def confirm_order_kb():
    kb = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def accept_order_kb(order_id):
    kb = [
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{order_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ============================================
# 6️⃣ START
# ============================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, name, created_at) VALUES (?, ?, ?)",
              (user_id, user_name, datetime.now()))
    conn.commit()
    conn.close()

    await message.answer(
        f"🚖 <b>XUSH KELIBSIZ, {user_name}!</b>\n\n"
        f"Bu Taksi24 bot orqali:\n"
        f"✅ Taksi buyurtma qilishingiz mumkin\n"
        f"✅ Haydovchi sifatida ro'yxatdan o'tishingiz mumkin\n"
        f"✅ Narxlarni oldindan bilib olishingiz mumkin\n\n"
        f"<b>Pastdagi tugmalardan birini tanlang:</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


# ============================================
# 7️⃣ HAYDOVCHI MENYUSI
# ============================================
@dp.message(lambda message: message.text == "🚗 Haydovchi menyusi")
async def driver_menu_handler(message: types.Message):
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM drivers WHERE telegram_id = ?", (message.from_user.id,))
    driver = c.fetchone()
    conn.close()

    if driver:
        status_text = "✅ Bo'sh" if driver[7] else "⏳ Band"

        await message.answer(
            f"🚗 <b>Haydovchi menyusi</b>\n\n"
            f"👤 {driver[2]}\n"
            f"🚘 {driver[4]} ({driver[5]})\n"
            f"⭐ Reyting: {driver[6]}\n"
            f"🔄 Holat: {status_text}",
            reply_markup=driver_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "🚗 <b>Haydovchi bo'lish</b>\n\n"
            "Ro'yxatdan o'tish uchun /register bosing",
            parse_mode="HTML"
        )


# ============================================
# 8️⃣ HAYDOVCHI RO'YXATDAN O'TISH
# ============================================
@dp.message(Command("register"))
async def register_start(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.name)
    await message.answer(
        "👤 <b>Haydovchi ro'yxatdan o'tish</b>\n\n"
        "Ism-familiyangizni kiriting:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@dp.message(RegisterState.name)
async def register_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=main_menu())
        return

    await state.update_data(full_name=message.text)
    await state.set_state(RegisterState.phone)
    await message.answer(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=phone_kb()
    )


@dp.message(RegisterState.phone)
async def register_phone(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(RegisterState.name)
        await message.answer("Ismingizni kiriting:", reply_markup=cancel_kb())
        return

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)
    await state.set_state(RegisterState.car_model)
    await message.answer(
        "🚗 Mashinangiz modeli:",
        reply_markup=cancel_kb()
    )


@dp.message(RegisterState.car_model)
async def register_car(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=main_menu())
        return

    await state.update_data(car_model=message.text)
    await state.set_state(RegisterState.car_number)
    await message.answer(
        "🔢 Davlat raqami:",
        reply_markup=cancel_kb()
    )


@dp.message(RegisterState.car_number)
async def register_number(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi", reply_markup=main_menu())
        return

    data = await state.get_data()

    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute('''INSERT INTO drivers (telegram_id, full_name, phone, car_model, car_number, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (message.from_user.id, data['full_name'], data['phone'], data['car_model'], message.text, datetime.now()))
    conn.commit()
    conn.close()

    await message.answer(
        "✅ <b>HAYDOVCHI SIFATIDA RO'YXATDAN O'TDINGIZ!</b>\n\n"
        f"👤 {data['full_name']}\n"
        f"📞 {data['phone']}\n"
        f"🚗 {data['car_model']}\n"
        f"🔢 {message.text}\n\n"
        f"Endi yangi buyurtmalarni qabul qilishingiz mumkin!",
        reply_markup=driver_menu(),
        parse_mode="HTML"
    )
    await state.clear()


# ============================================
# 9️⃣ BUYURTMA BERISH
# ============================================
@dp.message(lambda message: message.text == "🚖 Buyurtma berish")
@dp.message(Command("order"))
async def order_start(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.user_name)
    await message.answer(
        "👤 <b>Ismingizni kiriting:</b>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@dp.message(OrderState.user_name)
async def order_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Buyurtma bekor qilindi!", reply_markup=main_menu())
        return

    await state.update_data(user_name=message.text)
    await state.set_state(OrderState.user_phone)
    await message.answer(
        "📞 <b>Telefon raqamingiz:</b>",
        reply_markup=phone_kb(),
        parse_mode="HTML"
    )


@dp.message(OrderState.user_phone)
async def order_phone(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.set_state(OrderState.user_name)
        await message.answer("👤 Ismingizni kiriting:", reply_markup=cancel_kb())
        return

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(user_phone=phone)
    await state.set_state(OrderState.from_address)
    await message.answer(
        "📍 <b>Qayerdan?</b>\n\n"
        "Masalan: Chilonzor 19, 5-uy",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@dp.message(OrderState.from_address)
async def order_from(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Buyurtma bekor qilindi!", reply_markup=main_menu())
        return

    await state.update_data(from_address=message.text)
    await state.set_state(OrderState.to_address)
    await message.answer(
        "🏁 <b>Qayerga?</b>\n\n"
        "Masalan: Yunusobod 17, 12-uy",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
@dp.message(OrderState.to_address)
async def order_to(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Buyurtma bekor qilindi!", reply_markup=main_menu())
        return
    
    await state.update_data(to_address=message.text)
    data = await state.get_data()
    
    # BU QATOR TO'G'RI BOLISHI KERAK:
    distance = calculate_price(data['from_address'], data['to_address'])  # <-- FAQAT distance
    
    await state.update_data(distance=distance)
    
    await message.answer(
        f"🚖 <b>BUYURTMA MA'LUMOTLARI</b>\n\n"
        f"👤 <b>Ism:</b> {data['user_name']}\n"
        f"📞 <b>Telefon:</b> {data['user_phone']}\n"
        f"📍 <b>Qayerdan:</b> {data['from_address']}\n"
        f"🏁 <b>Qayerga:</b> {data['to_address']}\n"
        f"📏 <b>Masofa:</b> {distance} km\n\n"
        f"Buyurtmani tasdiqlaysizmi?",
        reply_markup=confirm_order_kb(),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.confirm)
# ============================================
# 🔟 BUYURTMA TASDIQLASH
# ============================================
@dp.callback_query(lambda c: c.data == "confirm")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # DATA NI TEKSHIRISH
    required_keys = ['user_name', 'user_phone', 'from_address', 'to_address', 'distance']
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        await callback.message.edit_text(
            f"❌ Xatolik! Ma'lumotlar to'liq emas.\n"
            f"Yo'qotilgan: {', '.join(missing_keys)}\n\n"
            f"Iltimos, /order buyrug'ini qaytadan bosing."
        )
        await state.clear()
        return
    
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO orders
                 (user_id, user_name, user_phone, from_address, to_address, distance, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, data['user_name'], data['user_phone'], data['from_address'],
               data['to_address'], data['distance'], 'yangi', datetime.now()))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    await callback.message.edit_text(
        f"✅ <b>BUYURTMA QABUL QILINDI!</b>\n\n"
        f"🆔 Buyurtma raqami: <b>{order_id}</b>\n"
        f"👤 {data['user_name']}\n"
        f"📍 {data['from_address']} → {data['to_address']}\n"
        f"📏 Masofa: {data['distance']} km\n\n"
        f"⏳ <b>Haydovchi qidirilmoqda...</b>\n"
        f"Tez orada siz bilan bog'lanamiz!"
    )
    
    await notify_drivers(order_id, data)
    await state.clear()

        # Haydovchini band qilish
        c.execute("UPDATE drivers SET is_available = 0 WHERE telegram_id = ?", (driver_id,))
        conn.commit()
    else:
        await callback.message.edit_text(
            "❌ Buyurtma allaqachon boshqa haydovchi tomonidan qabul qilingan!"
        )

    conn.close()


@dp.callback_query(lambda c: c.data.startswith('reject_'))
async def reject_order(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Buyurtma rad etildi")


# ============================================
# 1️⃣3️⃣ HAYDOVCHI MENYUSI
# ============================================
@dp.message(lambda message: message.text == "✅ Yangi buyurtmalar")
async def show_new_orders(message: types.Message):
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute('''SELECT *
                 FROM orders
                 WHERE status = 'yangi'
                 ORDER BY created_at DESC''')
    orders = c.fetchall()
    conn.close()

    if not orders:
        await message.answer("📭 Yangi buyurtmalar yo'q")
        return

    for order in orders:
        await message.answer(
            f"🚖 <b>Buyurtma #{order[0]}</b>\n\n"
            f"👤 {order[3]}\n"
            f"📍 {order[5]} → {order[6]}\n"
            f"📏 {order[8]} km\n"
            f"💰 {order[7]} so'm\n"
            f"🕐 {order[10]}",
            reply_markup=accept_order_kb(order[0])
        )


@dp.message(lambda message: message.text == "📊 Mening statistika")
async def driver_stats(message: types.Message):
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()

    c.execute('''SELECT *
                 FROM drivers
                 WHERE telegram_id = ?''', (message.from_user.id,))
    driver = c.fetchone()

    c.execute('''SELECT COUNT(*)
                 FROM orders
                 WHERE driver_id = ?
                   AND status = 'bajarildi' ''', (driver[0],))
    completed = c.fetchone()[0]

    c.execute('''SELECT COUNT(*)
                 FROM orders
                 WHERE driver_id = ?
                   AND status = 'qabul_qilindi' ''', (driver[0],))
    current = c.fetchone()[0]

    conn.close()

    status_text = "✅ Bo'sh" if driver[7] else "⏳ Band"

    await message.answer(
        f"📊 <b>STATISTIKA</b>\n\n"
        f"👤 {driver[2]}\n"
        f"🚗 {driver[4]} ({driver[5]})\n"
        f"⭐ Reyting: {driver[6]}\n"
        f"✅ Bajarilgan: {completed}\n"
        f"⏳ Joriy: {current}\n"
        f"🔄 Holat: {status_text}",
        parse_mode="HTML"
    )


@dp.message(lambda message: message.text == "🔄 Holatni o'zgartirish")
async def toggle_availability(message: types.Message):
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute('''UPDATE drivers
                 SET is_available = NOT is_available
                 WHERE telegram_id = ?''', (message.from_user.id,))
    conn.commit()

    c.execute('''SELECT is_available
                 FROM drivers
                 WHERE telegram_id = ?''', (message.from_user.id,))
    status = c.fetchone()[0]
    conn.close()

    status_text = "✅ Bo'sh" if status else "⏳ Band"
    await message.answer(f"✅ Holat o'zgartirildi: {status_text}")


# ============================================
# 1️⃣4️⃣ MENING BUYURTMALARIM
# ============================================
@dp.message(lambda message: message.text == "📋 Mening buyurtmalarim")
async def my_orders(message: types.Message):
    conn = sqlite3.connect('taxi_bot.db')
    c = conn.cursor()
    c.execute('''SELECT *
                 FROM orders
                 WHERE user_id = ?
                 ORDER BY created_at DESC LIMIT 5''',
              (message.from_user.id,))
    orders = c.fetchall()
    conn.close()

    if not orders:
        await message.answer("📭 Sizda hali buyurtmalar yo'q")
        return

    text = "📋 <b>OXIRGI 5 TA BUYURTMA</b>\n\n"
    for order in orders:
        status_emoji = {
            'yangi': '⏳',
            'qabul_qilindi': '✅',
            'bajarildi': '🎉',
            'bekor_qilindi': '❌'
        }
        text += f"{status_emoji.get(order[9], '⏳')} <b>#{order[0]}</b>\n"
        text += f"📍 {order[5]} → {order[6]}\n"
        text += f"📏 {order[8]} km\n"
        text += f"🕐 {order[10][:16]}\n\n"

    await message.answer(text, parse_mode="HTML")


# ============================================
# 1️⃣5️⃣ YORDAM VA ALOQA
# ============================================
@dp.message(lambda message: message.text == "📞 Aloqa")
async def contact(message: types.Message):
    await message.answer(
        "📞 <b>BIZ BILAN BOG'LANISH</b>\n\n"
        "☎️ Telefon: +998 90 123 45 67\n"
        "📧 Email: support@taksi24.uz\n"
        "🌐 Sayt: https://taksi24.uz\n\n"
        "⏰ 24/7",
        parse_mode="HTML"
    )


@dp.message(lambda message: message.text == "⚙️ Yordam")
@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        "🚕 <b>YORDAM</b>\n\n"
        "📌 <b>Buyruqlar:</b>\n"
        "/start - Botni ishga tushirish\n"
        "/order - Taksi buyurtma qilish\n"
        "/register - Haydovchi bo'lish\n"
        "/help - Yordam\n\n"
        "🚖 <b>Mijozlar uchun:</b>\n"
        "- Buyurtma berish\n"
        "- Narxlarni ko'rish\n"
        "- Haydovchini kuzatish\n\n"
        "🚗 <b>Haydovchilar uchun:</b>\n"
        "- Ro'yxatdan o'tish\n"
        "- Yangi buyurtmalarni ko'rish\n"
        "- Statistika\n\n"
        "📞 Aloqa: +998 90 123 45 67",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


# ============================================
# 1️⃣6️⃣ ORQAGA QAYTISH
# ============================================
@dp.message(lambda message: message.text == "🔙 Asosiy menyu")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyu", reply_markup=main_menu())


@dp.message(lambda message: message.text == "❌ Bekor qilish")
async def cancel_all(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi", reply_markup=main_menu())


# ============================================
# 1️⃣7️⃣ BOTNI ISHGA TUSHIRISH
# ============================================
async def main():
    print("=" * 50)
    print("🚖 TAKSI BOT ISHGA TUSHDI!")
    print("🤖 Bot: @taksi24_uz_bot")
    print("📊 Vaqt: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
