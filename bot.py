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
        # Eski jadvallarni o'chirish
        try:
            await db.execute("DROP TABLE IF EXISTS drivers")
            await db.execute("DROP TABLE IF EXISTS orders")
            print("✅ Eski jadvallar o'chirildi")
        except:
            pass

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

        # orders jadvali - narxsiz
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
                             INTEGER
                             DEFAULT
                             NULL,
                             start_location
                             TEXT,
                             end_location
                             TEXT,
                             latitude
                             REAL
                             DEFAULT
                             NULL,
                             longitude
                             REAL
                             DEFAULT
                             NULL,
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
        print("✅ Yangi database yaratildi!")


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


async def add_order(user_id, user_name, user_phone, start_location, end_location, latitude=None, longitude=None):
    async with aiosqlite.connect("taxi_bot.db") as db:
        cursor = await db.execute("""
                                  INSERT INTO orders (user_id, user_name, user_phone, start_location, end_location,
                                                      latitude, longitude)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)
                                  """,
                                  (user_id, user_name, user_phone, start_location, end_location, latitude, longitude))
        await db.commit()
        return cursor.lastrowid


async def update_driver_status(driver_id, status):
    async with aiosqlite.connect("taxi_bot.db") as db:
        await db.execute("UPDATE drivers SET status = ? WHERE id = ?", (status, driver_id))
        await db.commit()


async def get_all_approved_drivers():
    async with aiosqlite.connect("taxi_bot.db") as db:
        try:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM drivers WHERE status = 'approved'")
            return await cursor.fetchall()
        except:
            return []


# ==================== TEST HAYDOVCHI YARATISH ====================

async def create_test_driver():
    """Test uchun haydovchi yaratish"""
    async with aiosqlite.connect("taxi_bot.db") as db:
        # Test haydovchi mavjudligini tekshirish
        cursor = await db.execute("SELECT COUNT(*) FROM drivers WHERE user_id = ?", (ADMIN_ID,))
        count = await cursor.fetchone()

        if count[0] == 0:
            # Test haydovchi yaratish
            await db.execute("""
                             INSERT INTO drivers (user_id, full_name, phone, car_model, car_number, car_color,
                                                  license_photo, status)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                             """, (ADMIN_ID, "Test Haydovchi", "+998901234567", "Test Car", "01A123AA", "Qora",
                                   "test_photo_id", "approved"))
            await db.commit()
            print("✅ Test haydovchi yaratildi!")
        else:
            print("✅ Test haydovchi allaqachon mavjud")


# ==================== HOLATLAR (FSM) ====================

class DriverRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_car_model = State()
    waiting_for_car_number = State()
    waiting_for_car_color = State()
    waiting_for_license_photo = State()


class TaxiOrder(StatesGroup):
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


def get_admin_keyboard(driver_id):
    kb = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{driver_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{driver_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_confirmation_keyboard():
    kb = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_location_keyboard():
    kb = [
        [KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)],
        [KeyboardButton(text="🔙 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_contact_keyboard():
    kb = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="🔙 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


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


# ==================== TAKSI CHAQIRISH ====================

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

    # Foydalanuvchi ma'lumotlarini avtomatik olish
    user_name = message.from_user.full_name

    await state.update_data(user_name=user_name)
    await message.answer(
        f"👋 Assalomu alaykum, {user_name}!\n\n"
        f"Iltimos, telefon raqamingizni yuboring yoki quyidagi tugma orqali ulashing:",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(TaxiOrder.waiting_for_phone)


@dp.message(TaxiOrder.waiting_for_phone, F.contact)
async def process_order_phone_contact(message: types.Message, state: FSMContext):
    # Kontaktdan telefon raqamni olish
    phone = message.contact.phone_number
    await state.update_data(user_phone=phone)
    await message.answer(
        "📍 Ketish manzilingizni yuboring (lokatsiya yoki matn):",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(TaxiOrder.waiting_for_start_location)


@dp.message(TaxiOrder.waiting_for_phone, F.text)
async def process_order_phone_text(message: types.Message, state: FSMContext):
    # Qo'lda kiritilgan telefon raqam
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(user_phone=message.text)
    await message.answer(
        "📍 Ketish manzilingizni yuboring (lokatsiya yoki matn):",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(TaxiOrder.waiting_for_start_location)


@dp.message(TaxiOrder.waiting_for_start_location, F.location)
async def process_start_location_location(message: types.Message, state: FSMContext):
    location = message.location
    await state.update_data(
        start_location=f"Lokatsiya: {location.latitude}, {location.longitude}",
        latitude=location.latitude,
        longitude=location.longitude
    )
    await message.answer(
        "🏁 Borish manzilingizni yozing:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(TaxiOrder.waiting_for_end_location)


@dp.message(TaxiOrder.waiting_for_start_location, F.text)
async def process_start_location_text(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(start_location=message.text, latitude=None, longitude=None)
    await message.answer(
        "🏁 Borish manzilingizni yozing:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(TaxiOrder.waiting_for_end_location)


@dp.message(TaxiOrder.waiting_for_end_location)
async def process_end_location(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    data = await state.get_data()
    await state.update_data(end_location=message.text)

    text = (
        f"🚖 **Buyurtma ma'lumotlari:**\n\n"
        f"👤 Ism: {data.get('user_name')}\n"
        f"📞 Telefon: {data.get('user_phone')}\n"
        f"📍 Ketish: {data.get('start_location')}\n"
        f"🏁 Borish: {message.text}\n\n"
        f"✅ Buyurtmani tasdiqlaysizmi?"
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
        end_location=data['end_location'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )

    await callback.message.edit_text(
        f"✅ **Buyurtmangiz qabul qilindi!**\n\n"
        f"Buyurtma raqami: #{order_id}\n"
        f"Tez orada haydovchi siz bilan bog'lanadi.",
        parse_mode="Markdown"
    )

    # Barcha tasdiqlangan haydovchilarga buyurtmani yuborish
    drivers = await get_all_approved_drivers()
    for driver in drivers:
        try:
            location_text = ""
            if data.get('latitude') and data.get('longitude'):
                location_text = f"https://maps.google.com/?q={data['latitude']},{data['longitude']}"

            await bot.send_message(
                driver['user_id'],
                f"🚖 **Yangi buyurtma!**\n\n"
                f"👤 Mijoz: {data['user_name']}\n"
                f"📞 Telefon: {data['user_phone']}\n"
                f"📍 Ketish: {data['start_location']}\n"
                f"{location_text}\n"
                f"🏁 Borish: {data['end_location']}\n\n"
                f"Buyurtma raqami: #{order_id}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Haydovchiga xabar yuborishda xatolik: {e}")
            continue

    await state.clear()


@dp.callback_query(TaxiOrder.waiting_for_confirmation, F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await callback.message.answer("Bosh menyu", reply_markup=get_main_keyboard())
    await state.clear()


# ==================== HAYDOVCHI BO'LISH ====================

@dp.message(F.text == "👨‍✈️ Haydovchi bo'lish")
async def driver_menu(message: types.Message):
    driver = await get_driver_by_user_id(message.from_user.id)

    if driver:
        status_text = {
            'pending': '🟡 Kutilmoqda',
            'approved': '🟢 Tasdiqlangan',
            'rejected': '🔴 Rad etilgan'
        }.get(driver['status'], '❌ Noma\'lum')

        await message.answer(
            f"👨‍✈️ **Profilingiz:**\n\n"
            f"Ism: {driver['full_name']}\n"
            f"Mashina: {driver['car_model']} ({driver['car_color']})\n"
            f"Raqam: {driver['car_number']}\n"
            f"Holat: {status_text}",
            reply_markup=get_driver_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👨‍✈️ **Haydovchi bo'lish**\n\n"
            "Ro'yxatdan o'tish uchun '📝 Ro'yxatdan o'tish' tugmasini bosing.",
            reply_markup=get_driver_keyboard(),
            parse_mode="Markdown"
        )


@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_driver_registration(message: types.Message, state: FSMContext):
    driver = await get_driver_by_user_id(message.from_user.id)
    if driver:
        await message.answer("❌ Siz allaqachon ro'yxatdan o'tgansiz!")
        return

    await message.answer(
        "1️⃣ Ism familiyangizni yozing:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(DriverRegistration.waiting_for_name)


@dp.message(DriverRegistration.waiting_for_name)
async def process_driver_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(full_name=message.text)
    await message.answer(
        "2️⃣ Telefon raqamingizni yozing:",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(DriverRegistration.waiting_for_phone)


@dp.message(DriverRegistration.waiting_for_phone, F.contact)
async def process_driver_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer(
        "3️⃣ Mashina modeli:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(DriverRegistration.waiting_for_car_model)


@dp.message(DriverRegistration.waiting_for_phone, F.text)
async def process_driver_phone_text(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(phone=message.text)
    await message.answer(
        "3️⃣ Mashina modeli:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(DriverRegistration.waiting_for_car_model)


@dp.message(DriverRegistration.waiting_for_car_model)
async def process_driver_car_model(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(car_model=message.text)
    await message.answer(
        "4️⃣ Mashina raqami:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(DriverRegistration.waiting_for_car_number)


@dp.message(DriverRegistration.waiting_for_car_number)
async def process_driver_car_number(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(car_number=message.text.upper())
    await message.answer(
        "5️⃣ Mashina rangi:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
    )
    await state.set_state(DriverRegistration.waiting_for_car_color)


@dp.message(DriverRegistration.waiting_for_car_color)
async def process_driver_car_color(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return

    await state.update_data(car_color=message.text)
    await message.answer(
        "6️⃣ Haydovchilik guvohnomasi rasmini yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
            resize_keyboard=True
        )
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
            "✅ Ro'yxatdan o'tdingiz! Admin tekshirib chiqadi.",
            reply_markup=get_main_keyboard()
        )

        # Haydovchi ma'lumotlarini olish
        driver = await get_driver_by_user_id(message.from_user.id)

        # Admin ga xabar
        admin_text = (
            f"🆕 **Yangi haydovchi arizasi!**\n\n"
            f"👤 Ism: {data['full_name']}\n"
            f"📞 Telefon: {data['phone']}\n"
            f"🚗 Mashina: {data['car_model']}\n"
            f"🔢 Raqam: {data['car_number']}\n"
            f"🎨 Rang: {data['car_color']}\n"
            f"🆔 User ID: {message.from_user.id}"
        )

        await bot.send_message(
            ADMIN_ID,
            admin_text,
            reply_markup=get_admin_keyboard(driver['id'] if driver else 0),
            parse_mode="Markdown"
        )
        await bot.send_photo(ADMIN_ID, photo.file_id, caption="Haydovchilik guvohnomasi")
    else:
        await message.answer("❌ Xatolik yuz berdi! Qaytadan urinib ko'ring.")

    await state.clear()


@dp.message(DriverRegistration.waiting_for_license_photo)
async def process_driver_license_photo_invalid(message: types.Message, state: FSMContext):
    if message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return
    await message.answer("❌ Iltimos, rasm yuboring!")


# ==================== ADMIN PANEL ====================

@dp.callback_query(F.data.startswith("approve_"))
async def approve_driver(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return

    driver_id = int(callback.data.split("_")[1])
    await update_driver_status(driver_id, 'approved')

    # Haydovchiga xabar yuborish
    async with aiosqlite.connect("taxi_bot.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, full_name FROM drivers WHERE id = ?", (driver_id,))
        driver = await cursor.fetchone()

        if driver:
            await bot.send_message(
                driver['user_id'],
                f"✅ **Tabriklaymiz, {driver['full_name']}!**\n\n"
                f"Sizning arizangiz tasdiqlandi. Endi siz haydovchi sifatida buyurtmalarni qabul qilishingiz mumkin.",
                parse_mode="Markdown"
            )

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ **Tasdiqlandi!**",
        parse_mode="Markdown"
    )
    await callback.answer("Haydovchi tasdiqlandi!")


@dp.callback_query(F.data.startswith("reject_"))
async def reject_driver(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return

    driver_id = int(callback.data.split("_")[1])
    await update_driver_status(driver_id, 'rejected')

    # Haydovchiga xabar yuborish
    async with aiosqlite.connect("taxi_bot.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id, full_name FROM drivers WHERE id = ?", (driver_id,))
        driver = await cursor.fetchone()

        if driver:
            await bot.send_message(
                driver['user_id'],
                f"❌ **Afsus, {driver['full_name']}!**\n\n"
                f"Sizning arizangiz rad etildi. Qo'shimcha ma'lumot olish uchun admin bilan bog'lanishingiz mumkin.",
                parse_mode="Markdown"
            )

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ **Rad etildi!**",
        parse_mode="Markdown"
    )
    await callback.answer("Haydovchi rad etildi!")


# ==================== BOSHQA HANDLERLAR ====================

@dp.message(F.text == "📞 Aloqa")
async def contact(message: types.Message):
    await message.answer(
        "📞 **Aloqa ma'lumotlari:**\n\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "📧 Email: support@taxibot.uz\n"
        "🌐 Website: www.taxibot.uz",
        parse_mode="Markdown"
    )


@dp.message(F.text == "ℹ️ Yordam")
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ **Yordam**\n\n"
        "🚖 Taksi chaqirish - taksi buyurtma qilish\n"
        "👨‍✈️ Haydovchi bo'lish - haydovchi sifatida ro'yxatdan o'tish\n"
        "👤 Profilim - shaxsiy ma'lumotlaringiz\n"
        "📞 Aloqa - admin bilan bog'lanish\n\n"
        "Muammo yuzaga kelsa, admin bilan bog'lanishingiz mumkin.",
        parse_mode="Markdown"
    )


@dp.message(F.text == "👤 Profilim")
async def profile(message: types.Message):
    await message.answer(
        f"👤 **Profilingiz:**\n\n"
        f"Ism: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username if message.from_user.username else 'mavjud emas'}\n"
        f"ID: {message.from_user.id}",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📊 Mening statistika")
async def driver_statistics(message: types.Message):
    driver = await get_driver_by_user_id(message.from_user.id)

    if not driver or driver['status'] != 'approved':
        await message.answer("❌ Siz tasdiqlangan haydovchi emassiz!")
        return

    async with aiosqlite.connect("taxi_bot.db") as db:
        # Haydovchining bajargan buyurtmalari statistikasi
        cursor = await db.execute(
            "SELECT COUNT(*) as total FROM orders WHERE driver_id = ? AND status = 'completed'",
            (driver['id'],)
        )
        stats = await cursor.fetchone()

        total_orders = stats[0] if stats[0] else 0

        await message.answer(
            f"📊 **Statistikangiz:**\n\n"
            f"🚖 Bajarilgan buyurtmalar: {total_orders}",
            parse_mode="Markdown"
        )


@dp.message(F.text == "🔙 Bosh menyu")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu", reply_markup=get_main_keyboard())


# ==================== ASOSIY ====================

async def main():
    await init_db()
    await create_test_driver()  # Test haydovchi yaratish
    print("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Bot to'xtatildi")