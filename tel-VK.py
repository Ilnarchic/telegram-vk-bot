import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

# 🔹 Настройки
TELEGRAM_TOKEN = "8116137907:AAH9mUJ3ycDiCD2-q30yd2c-8MgBsWLZzjo"
VK_ACCESS_TOKEN = "vk1.a.UMBKkFfVzBl9c5hEkRn8gFEurMfv_6EvnvPD5vNwbv3gxq3zYUmCabXdJ4wDWoE8nNfiZsjLQAaoffhNiFuAcHams6S8L2WVCZNCoNy3RbdVetFXPq2xPyjP0tcVhzGj1cTFncg2Rb8cLH0O9xDZCkMqdzPteJpVttnTegKwgpgLRF7TkIGY40N_I4_IjkCqjNWt5L7qQq7jjpdDcOIKDA"
VK_GROUP_ID = "-229441646"  # ID группы (с минусом)


# 🔹 Функция публикации поста в ВК
def post_to_vk(message):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "owner_id": VK_GROUP_ID,
        "from_group": 1,
        "message": message,
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131",
    }
    response = requests.post(url, data=params)
    return response.json()

# 🔹 Обработчик сообщений Телеграма
async def telegram_handler(update: Update, context):
    text = update.message.text  # Получаем текст сообщения
    if text:
        vk_response = post_to_vk(text)  # Отправляем в ВК
        await update.message.reply_text("✅ Пост опубликован в ВК!")

# 🔹 Запускаем бота
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))

print("✅ Бот запущен...")
app.run_polling()
