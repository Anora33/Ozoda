import asyncio
import logging
import os
import warnings
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import aiosqlite

# Ogohlantirishlarni o'chirish
warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.INFO)

# .env faylni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==================== MA'LUMOTLAR BAZASI ====================

async def init_db():
    async with aiosqlite.connect("taxi_bot.db") as db:
        # drivers jadvali
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS drivers
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
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
                             car_color
                             TEXT,
                             license_photo
                             TEXT,
                             status
                             TEXT
                             DEFAULT
                             'pending',
                             registered_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        # orders jadvali
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS orders
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             user_name
                             TEXT,
                             user_phone
                             TEXT,
                             driver_id
                             INTEGER,
                             start_location
                             TEXT,
                             end_location
                             TEXT,
                             price
                             INTEGER
                             DEFAULT
                             0,
                             status
                             TEXT
                             DEFAULT
                             'pending',
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)
        await db.commit()
        print("✅ Database yaratildi!")


async def add_driver(user_id, full_name, phone, car_model, car_number, car_color, license_photo):
    async with aiosqlite.connect("taxi_bot.db") as db:
        try:
            await db.execute("""
                             INSERT INTO drivers (user_id, full_name, phone, car_model, car_number, car_color,
                                                  license_photo, status)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                             """,
                             (user_id, full_name, phone, car_model, car_number, car_color, license_photo, 'pending'))
            await db.commit()
            return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False


async def get_approved_drivers_count():
    async with aiosqlite.connect("taxi_bot.db") as db:
        try:
            cursor = await db.execute("SELECT COUNT(*) FROM drivers WHERE status = 'approved'")
            result = await cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0


async def get_pending_drivers():
    async with aiosqlite.connect("taxi_bot.db") as db:
        try:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM drivers WHERE status = 'pending'")
            return await cursor.fetchall()
        except:
            return []


async def get_driver_by_user_id(user_id):
    async with aiosqlite.connect("taxi_bot.db") as db:
        try:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM drivers WHERE user_id = ?", (user_id,))
            return await cursor.fetchone()
        except:
            return None


async def add_order(user_id, user_name, user_phone, start_location, end_location):
    async with aiosqlite.connect("taxi_bot.db") as db:
        cursor = await db.execute("""
                                  INSERT INTO orders (user_id, user_name, user_phone, start_location, end_location)
                                  VALUES (?, ?, ?, ?, ?)
                                  """, (user_id, user_name, user_phone, start_location, end_location))
        await db.commit()
        return cursor.lastrowid


async def update_driver_status(driver_id, status):
    async with aiosqlite.connect("taxi_bot.db") as db:
        await db.execute("UPDATE drivers SET status = ? WHERE id = ?", (status, driver_id))
        await db.commit()


# ==================== HOLATLAR (FSM) ====================

class DriverRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_car_model = State()
    waiting_for_car_number = State()
    waiting_for_car_color = State()
    waiting_for_license_photo = State()


class TaxiOrder(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_start_location = State()
    waiting_for_end_location = State()
    waiting_for_confirmation = State()


# ==================== TUGMALAR ====================

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="🚖 Taksi chaqirish")],
        [KeyboardButton(text="👨‍✈️ Haydovchi bo'lish"), KeyboardButton(text="👤 Profilim")],
        [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="ℹ️ Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_driver_keyboard():
    kb = [
        [KeyboardButton(text="📝 Ro'yxatdan o'tish")],
        [KeyboardButton(text="📊 Mening statistika")],
        [KeyboardButton(text="🔙 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_admin_keyboard():
    kb = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="admin_approve")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data="admin_reject")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_confirmation_keyboard():
    kb = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ==================== HANDLERLAR ====================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "🚖 **Taksi Bot**ga xush kelibsiz!\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


# --- MIJOZLAR UCHUN ---

@dp.message(F.text == "🚖 Taksi chaqirish")
async def process_order_start(message: types.Message, state: FSMContext):
    drivers_count = await get_approved_drivers_count()
    if drivers_count == 0:
        await message.answer(
            "⚠️ **Hozircha haydovchilar yo'q!**\n\n"
            "Birozdan keyin urinib ko'ring.",
            parse_mode="Markdown"
        )
        return

    await message.answer("📝 **Buyurtma berish**\n\n1️⃣ Ismingizni yozing:")
    await state.set_state(TaxiOrder.waiting_for_name)


@dp.message(TaxiOrder.waiting_for_name)
async def process_order_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("2️⃣ Telefon raqamingizni yozing:")
    await state.set_state(TaxiOrder.waiting_for_phone)


@dp.message(TaxiOrder.waiting_for_phone)
async def process_order_phone(message: types.Message, state: FSMContext):
    await state.update_data(user_phone=message.text)
    await message.answer("3️⃣ Ketish manzilingizni yozing:")
    await state.set_state(TaxiOrder.waiting_for_start_location)


@dp.message(TaxiOrder.waiting_for_start_location)
async def process_start_location(message: types.Message, state: FSMContext):
    await state.update_data(start_location=message.text)
    await message.answer("4️⃣ Borish manzilingizni yozing:")
    await state.set_state(TaxiOrder.waiting_for_end_location)


@dp.message(TaxiOrder.waiting_for_end_location)
async def process_end_location(message: types.Message, state: FSMContext):
    await state.update_data(end_location=message.text)

    data = await state.get_data()

    text = (
        f"🚖 **Buyurtma tafsilotlari:**\n\n"
        f"👤 Ism: {data['user_name']}\n"
        f"📞 Telefon: {data['user_phone']}\n"
        f"📍 Ketish: {data['start_location']}\n"
        f"🏁 Borish: {message.text}\n\n"
        f"Tasdiqlaysizmi?"
    )

    await message.answer(text, reply_markup=get_confirmation_keyboard(), parse_mode="Markdown")
    await state.set_state(TaxiOrder.waiting_for_confirmation)


@dp.callback_query(TaxiOrder.waiting_for_confirmation, F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    order_id = await add_order(
        user_id=callback.from_user.id,
        user_name=data['user_name'],
        user_phone=data['user_phone'],
        start_location=data['start_location'],
        end_location=data['end_location']
    )

    await callback.message.edit_text("✅ Buyurtmangiz qabul qilindi!")
    await state.clear()

    # Admin ga xabar
    await bot.send_message(
        ADMIN_ID,
        f"🔔 Yangi buyurtma #{order_id}\n👤 {data['user_name']}\n📍 {data['start_location']} → {data['end_location']}"
    )


@dp.callback_query(TaxiOrder.waiting_for_confirmation, F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await state.clear()


# --- HAYDOVCHILAR UCHUN ---

@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_driver_registration(message: types.Message, state: FSMContext):
    driver = await get_driver_by_user_id(message.from_user.id)
    if driver:
        await message.answer("❌ Siz allaqachon ro'yxatdan o'tgansiz!")
        return

    await message.answer("1️⃣ Ism familiyangizni yozing:")
    await state.set_state(DriverRegistration.waiting_for_name)


@dp.message(DriverRegistration.waiting_for_name)
async def process_driver_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "📞 Telefon raqamingizni yuboring.\n\n"
        "Quyidagi tugma orqali yuborishingiz mumkin:",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(DriverRegistration.waiting_for_phone)


@dp.message(DriverRegistration.waiting_for_phone, F.contact)
async def process_driver_phone_contact(message: types.Message, state: FSMContext):
    # Kontact orqali telefon raqam olish
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer(
        "3️⃣ Mashina modelini yozing (masalan: Nexia 3, Cobalt, Lacetti):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_car_model)


@dp.message(DriverRegistration.waiting_for_phone)
async def process_driver_phone_text(message: types.Message, state: FSMContext):
    # Qo'lda yozilgan telefon raqam
    if message.text == "🔙 Ortga":
        await start_driver_registration(message, state)
        return

    phone = message.text
    await state.update_data(phone=phone)
    await message.answer(
        "3️⃣ Mashina modelini yozing (masalan: Nexia 3, Cobalt, Lacetti):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_car_model)


# Ortga qaytish handleri
@dp.message(F.text == "🔙 Ortga")
async def go_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [DriverRegistration.waiting_for_phone,
                         DriverRegistration.waiting_for_car_model,
                         DriverRegistration.waiting_for_car_number,
                         DriverRegistration.waiting_for_car_color,
                         DriverRegistration.waiting_for_license_photo]:
        await start_driver_registration(message, state)
    else:
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        await state.clear()

# --- ADMIN UCHUN ---

@dp.callback_query(F.data == "admin_approve")
async def approve_driver(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q")
        return
    await callback.message.edit_text("✅ Haydovchi tasdiqlandi")


@dp.callback_query(F.data == "admin_reject")
async def reject_driver(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q")
        return
    await callback.message.edit_text("❌ Haydovchi rad etildi")


@dp.message(Command("drivers"))
async def show_pending_drivers(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    drivers = await get_pending_drivers()
    if not drivers:
        await message.answer("📭 Kutilayotgan haydovchilar yo'q.")
        return

    for driver in drivers:
        text = (
            f"👤 Ism: {driver['full_name']}\n"
            f"📞 Telefon: {driver['phone']}\n"
            f"🚗 Mashina: {driver['car_model']} ({driver['car_number']}) - {driver['car_color']}"
        )
        await message.answer(text, reply_markup=get_admin_keyboard())
        if driver['license_photo']:
            await bot.send_photo(message.chat.id, photo=driver['license_photo'])


@dp.message(Command("drivers_count"))
async def show_drivers_count(message: types.Message):
    count = await get_approved_drivers_count()
    await message.answer(f"🚖 Tasdiqlangan haydovchilar: {count} ta")


# ==================== ASOSIY ====================

async def main():
    await init_db()
    print("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Bot to'xtatildi")