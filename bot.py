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
@dp.message(F.text == "👨‍✈️ Haydovchi bo'lish")
async def driver_menu(message: types.Message):
    driver = await get_driver_by_user_id(message.from_user.id)

    if driver:
        status_text = {
            'pending': "🟡 Ko'rib chiqilmoqda",
            'approved': "🟢 Tasdiqlangan",
            'rejected': "🔴 Rad etilgan"
        }

        driver_status = driver['status']
        status_name = status_text.get(driver_status, 'Noma\'lum')

        text = (
            f"👨‍✈️ **Sizning profilingiz:**\n\n"
            f"👤 Ism: {driver['full_name']}\n"
            f"📞 Telefon: {driver['phone']}\n"
            f"🚗 Mashina: {driver['car_model']} ({driver['car_number']}) - {driver['car_color']}\n"
            f"📊 Holat: {status_name}\n\n"
            f"📅 Ro'yxatdan o'tgan: {driver['registered_at']}"
        )

        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        await message.answer(
            "👨‍✈️ **Haydovchi bo'lish**\n\n"
            "Haydovchi bo'lish uchun quyidagi tugmani bosing va ro'yxatdan o'ting.\n\n"
            "Ro'yxatdan o'tgach, administrator ma'lumotlaringizni tekshirib chiqadi.",
            reply_markup=get_driver_keyboard(),
            parse_mode="Markdown"
        )


@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_driver_registration(message: types.Message, state: FSMContext):
    driver = await get_driver_by_user_id(message.from_user.id)
    if driver:
        await message.answer(
            "❌ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            "Profilingizni ko'rish uchun '👨‍✈️ Haydovchi bo'lish' tugmasini bosing.",
            reply_markup=get_main_keyboard()
        )
        return

    await message.answer(
        "📝 **Haydovchi ro'yxatdan o'tish**\n\n"
        "1️⃣ Qadam: Ism va familiyangizni yozing (masalan: Aliyev Alijon):",
        parse_mode="Markdown"
    )
    await state.set_state(DriverRegistration.waiting_for_name)


@dp.message(DriverRegistration.waiting_for_name)
async def process_driver_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "2️⃣ Qadam: Telefon raqamingizni yuboring.\n\n"
        "Quyidagi tugma orqali yuborishingiz mumkin yoki qo'lda yozing:",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(DriverRegistration.waiting_for_phone)


@dp.message(DriverRegistration.waiting_for_phone, F.contact)
async def process_driver_phone_contact(message: types.Message, state: FSMContext):
    # Kontakt orqali telefon raqam olish
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer(
        "✅ Telefon raqam qabul qilindi!\n\n"
        "3️⃣ Qadam: Mashina modelini yozing (masalan: Nexia 3, Cobalt, Lacetti):",
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
        "✅ Telefon raqam qabul qilindi!\n\n"
        "3️⃣ Qadam: Mashina modelini yozing (masalan: Nexia 3, Cobalt, Lacetti):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_car_model)


@dp.message(DriverRegistration.waiting_for_car_model)
async def process_driver_car_model(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await start_driver_registration(message, state)
        return

    await state.update_data(car_model=message.text)
    await message.answer(
        "4️⃣ Qadam: Mashina raqamini yozing (masalan: 01A123BC, 01 123 ABC):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_car_number)


@dp.message(DriverRegistration.waiting_for_car_number)
async def process_driver_car_number(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await start_driver_registration(message, state)
        return

    await state.update_data(car_number=message.text)
    await message.answer(
        "5️⃣ Qadam: Mashina rangini yozing (masalan: Oq, Qora, Kulrang):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_car_color)


@dp.message(DriverRegistration.waiting_for_car_color)
async def process_driver_car_color(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await start_driver_registration(message, state)
        return

    await state.update_data(car_color=message.text)
    await message.answer(
        "6️⃣ Qadam: Haydovchilik guvohnomasi rasmini yuboring:\n\n"
        "Iltimos, guvohnomangizning aniq rasmini yuboring.",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
    )
    await state.set_state(DriverRegistration.waiting_for_license_photo)


@dp.message(DriverRegistration.waiting_for_license_photo, F.photo)
async def process_driver_license_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    data = await state.get_data()

    success = await add_driver(
        user_id=message.from_user.id,
        full_name=data['full_name'],
        phone=data['phone'],
        car_model=data['car_model'],
        car_number=data['car_number'],
        car_color=data['car_color'],
        license_photo=photo.file_id
    )

    if success:
        await message.answer(
            "✅ **Ro'yxatdan o'tish muvaffaqiyatli!**\n\n"
            "Ma'lumotlaringiz administratorga yuborildi.\n"
            "Tekshiruvdan so'ng sizga xabar beramiz.\n\n"
            "Ortacha tekshirish vaqti: 5-10 daqiqa.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

        # Admin ga xabar yuborish
        username = message.from_user.username if message.from_user.username else 'yoq'

        admin_text = (
            f"🆕 **Yangi haydovchi ro'yxatdan o'tdi!**\n\n"
            f"👤 Ism: {data['full_name']}\n"
            f"📞 Telefon: {data['phone']}\n"
            f"🚗 Mashina: {data['car_model']} ({data['car_number']}) - {data['car_color']}\n"
            f"🆔 User ID: `{message.from_user.id}`\n"
            f"👤 Username: @{username}"
        )

        await bot.send_message(ADMIN_ID, admin_text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        await bot.send_photo(ADMIN_ID, photo.file_id, caption="📄 Haydovchilik guvohnomasi")
    else:
        await message.answer(
            "❌ Xatolik yuz berdi!\n\n"
            "Iltimos, qayta urinib ko'ring.",
            reply_markup=get_main_keyboard()
        )

    await state.clear()

    await state.clear()

    @dp.message(DriverRegistration.waiting_for_license_photo)  # <-- Oldida bo'sh joy YO'Q!
    async def process_driver_license_photo_invalid(message: types.Message, state: FSMContext):
        # kod

        @dp.message(DriverRegistration.waiting_for_license_photo)  # 511-qator
        async def process_driver_license_photo_invalid(message: types.Message, state: FSMContext):  # 512-qator
            if message.text == "🔙 Ortga":  # 513-qator (4 bo'sh joy)
                await start_driver_registration(message, state)  # 514-qator (8 bo'sh joy)
                return  # 515-qator (8 bo'sh joy)

            await message.answer(  # 516-qator (4 bo'sh joy)
                "❌ Iltimos, haydovchilik guvohnomasining rasmini yuboring!",
                reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
            )

        await message.answer(
            "❌ Iltimos, haydovchilik guvohnomasining rasmini yuboring!\n\n"
            "Rasm yuborish uchun: 📎 (skrepka) belgisini bosing va rasm tanlang.",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Ortga")]], resize_keyboard=True)
        )

    @dp.message(F.text == "📊 Mening statistika")
    async def driver_stats(message: types.Message):
        driver = await get_driver_by_user_id(message.from_user.id)

        if not driver:
            await message.answer(
                "❌ Siz haydovchi sifatida ro'yxatdan o'tmagansiz!\n\n"
                "Ro'yxatdan o'tish uchun '👨‍✈️ Haydovchi bo'lish' tugmasini bosing.",
                reply_markup=get_main_keyboard()
            )
            return

        if driver['status'] != 'approved':
            await message.answer(
                "⚠️ Statistikani ko'rish uchun haydovchi sifatida tasdiqlangan bo'lishingiz kerak.\n\n"
                "Hozirgi holatingiz: " + ("🟡 Kutilmoqda" if driver['status'] == 'pending' else "🔴 Rad etilgan"),
                reply_markup=get_main_keyboard()
            )
            return

        # Statistika ma'lumotlarini olish
        async with aiosqlite.connect("taxi_bot.db") as db:
            # Haydovchining buyurtmalari
            cursor = await db.execute(
                "SELECT COUNT(*) FROM orders WHERE driver_id = ? AND status = 'completed'",
                (message.from_user.id,)
            )
            completed_orders = await cursor.fetchone()

            cursor = await db.execute(
                "SELECT COUNT(*) FROM orders WHERE driver_id = ? AND status = 'cancelled'",
                (message.from_user.id,)
            )
            cancelled_orders = await cursor.fetchone()

            cursor = await db.execute(
                "SELECT COUNT(*) FROM orders WHERE driver_id = ? AND status = 'pending'",
                (message.from_user.id,)
            )
            pending_orders = await cursor.fetchone()

            cursor = await db.execute(
                "SELECT SUM(price) FROM orders WHERE driver_id = ? AND status = 'completed'",
                (message.from_user.id,)
            )
            total_earnings = await cursor.fetchone()

        stats_text = (
            f"📊 **Sizning statistikangiz:**\n\n"
            f"✅ Bajarilgan buyurtmalar: {completed_orders[0] if completed_orders else 0}\n"
            f"⏳ Kutilayotgan buyurtmalar: {pending_orders[0] if pending_orders else 0}\n"
            f"❌ Bekor qilingan buyurtmalar: {cancelled_orders[0] if cancelled_orders else 0}\n"
            f"💰 Umumiy daromad: {total_earnings[0] if total_earnings[0] else 0} so'm\n\n"
            f"🚗 Mashina: {driver['car_model']} ({driver['car_number']})"
        )

        await message.answer(stats_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    # Ortga qaytish handleri
    @dp.message(F.text == "🔙 Ortga")
    async def go_back(message: types.Message, state: FSMContext):
        current_state = await state.get_state()

        if current_state is not None:
            await state.clear()
            await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        else:
            await message.answer("Bosh menyu", reply_markup=get_main_keyboard())

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