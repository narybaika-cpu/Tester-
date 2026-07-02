import datetime
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from supabase import create_client, Client

# ==========================================
# 🛠️ НАСТРОЙКИ ПОДКЛЮЧЕНИЯ (Вставь свои данные)
# ==========================================
TOKEN = "ТВОЙ_ТОКЕН_ТЕЛЕГРАМ_БОТА"
SUPABASE_URL = "https://byfgtuqfoyupdtgxfvkr.supabase.co"  # Твой URL уже тут
SUPABASE_KEY = "sb_publishable_K7x2lDAPPDB7cIfyxxmWHQ_wnoxkyeM"

# Инициализируем бот и базу данных
bot = Bot(token=8943181005:AAExF8PnemnrRoZ7I6VLeGoqZbBbn8E68Kc)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Настройка секторов колеса (всего 10 позиций)
# 5 позиций по 1р (через одну), 2 сектора по 2р, 2 сектора по 3р, 1 сектор - кофе
WHEEL_SECTORS = [
    {"type": "money", "value": 1, "text": "💰 1 бонусный рубль"},
    {"type": "empty", "value": 0, "text": "💨 Пусто (повезет в следующий раз)"},
    {"type": "money", "value": 1, "text": "💰 1 бонусный рубль"},
    {"type": "empty", "value": 0, "text": "💨 Пусто (повезет в следующий раз)"},
    {"type": "money", "value": 1, "text": "💰 1 бонусный рубль"},
    {"type": "money", "value": 2, "text": "💵 2 бонусных рубля"},
    {"type": "money", "value": 2, "text": "💵 2 бонусных рубля"},
    {"type": "money", "value": 3, "text": "💳 3 бонусных рубля"},
    {"type": "money", "value": 3, "text": "💳 3 бонусных рубля"},
    {"type": "coffee", "value": 1, "text": "☕ Ароматный КОФЕ!"}
]

# Функция для расчета бонусов и лимитов в зависимости от уровня лояльности «Level Up»
def get_level_perks(level: int):
    # Тестовые бонусы от уровня (можно настроить любые цифры)
    perks = {
        1: "Начальный уровень. Колесо доступно!",
        2: "+5% к кэшбеку на баре",
        3: "+10% к кэшбеку на баре",
        4: "Бесплатный сироп к каждому кофе",
        5: "Скидка 5% на всё меню",
        6: "Скидка 10% на всё меню",
        7: "Каждая 7-я чашка в подарок автоматически",
        8: "Доступ к VIP-розыгрышам",
        9: "Персональный десерт в день рождения",
        10: "👑 МЕГА-СТАТУС: Пожизненный кэшбек 20%!"
    }
    return perks.get(level, "Бонусы уточняются")

# Функция получения или создания пользователя в Supabase
def get_or_create_user(user_id: int, username: str):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    if res.data:
        return res.data[0]
    
    # Если пользователя нет, создаем его (уровень 1, баланс 0)
    user_data = {
        "id": user_id,
        "username": username or "Пользователь",
        "bonus_balance": 0,
        "coffee_cups": 0,
        "hp": 0,
        "level": 1
    }
    supabase.table("users").insert(user_data).execute()
    return user_data

# Генерация главного экрана
def make_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎡 Крутить Колесо Фортуны", callback_data="spin_wheel")
    builder.button(text="🔄 Обновить профиль", callback_data="refresh_profile")
    builder.adjust(1)
    return builder.as_markup()

# Обработка команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username)
    
    # Считаем прогресс (например, для перехода на след. уровень нужно 10 HP)
    next_level_hp = 10
    progress_bar = "🟩" * user['hp'] + "⬜" * (next_level_hp - user['hp'])
    perks = get_level_perks(user['level'])

    text = (
        f"📱 **ГЛАВНЫЙ ЭКРАН СИСТЕМЫ ЛОЯЛЬНОСТИ**\n"
        f"----------------------------------------\n"
        f"👤 **Никнейм:** @{user['username']}\n"
        f"🆔 **Твой ID:** `{user['id']}`\n\n"
        f"📊 **Уровень:** {user['level']} [Уровень лояльности]\n"
        f"✨ **Прогресс:** [{progress_bar}] ({user['hp']}/{next_level_hp} HP)\n"
        f"💰 **Баланс рублей:** {user['bonus_balance']} руб.\n"
        f"☕ **Выиграно кофе:** {user['coffee_cups']} шт.\n"
        f"----------------------------------------\n"
        f"🎁 **Бонусы от твоего уровня:**\n"
        f"_{perks}_\n"
    )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=make_main_menu_keyboard())

# Обработка нажатий на кнопки
@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_or_create_user(user_id, callback.from_user.username)

    if callback.data == "refresh_profile":
        # Просто обновляем экран
        await callback.message.delete()
        # Имитируем команду старт для перерисовки
        message = callback.message
        message.from_user = callback.from_user
        await cmd_start(message)
        await callback.answer("Профиль обновлен!")

    elif callback.data == "spin_wheel":
        # Проверяем кулдаун (раз в 1 минуту для тестов)
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if user.get("last_spin"):
            # Supabase возвращает дату строкой, переводим в формат времени
            last_spin_time = datetime.datetime.fromisoformat(user["last_spin"].replace("Z", "+00:00"))
            time_passed = now - last_spin_time
            
            if time_passed < datetime.timedelta(minutes=1):
                seconds_left = 60 - int(time_passed.total_seconds())
                await callback.answer(f"⏳ Колесо остывает! Подожди еще {seconds_left} сек.", show_alert=True)
                return

        # Крутим колесо
        prize = random.choice(WHEEL_SECTORS)
        
        # Обновляем данные игрока на основе выигрыша
        new_balance = user["bonus_balance"]
        new_coffee = user["coffee_cups"]
        new_hp = user["hp"] + 1  # Даем +1 HP опыта за каждый круток для теста
        new_level = user["level"]

        if prize["type"] == "money":
            new_balance += prize["value"]
        elif prize["type"] == "coffee":
            new_coffee += prize["value"]

        # Логика повышения уровня (каждые 10 HP — новый уровень, максимум 10)
        if new_hp >= 10:
            if new_level < 10:
                new_level += 1
                new_hp = 0  # Сбрасываем опыт для нового уровня

        # Сохраняем всё в Supabase
        update_data = {
            "bonus_balance": new_balance,
            "coffee_cups": new_coffee,
            "hp": new_hp,
            "level": new_level,
            "last_spin": now.isoformat()
        }
        supabase.table("users").update(update_data).eq("id", user_id).execute()

        # Показываем результат анимацией alert
        await callback.answer(f"🎡 Колесо крутится...\n\n🎉 РЕЗУЛЬТАТ: {prize['text']}", show_alert=True)
        
        # Перерисовываем главный экран с новыми данными
        await callback.message.delete()
        message = callback.message
        message.from_user = callback.from_user
        await cmd_start(message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
