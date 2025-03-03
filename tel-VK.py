import requests
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 🔹 Настройки
TELEGRAM_TOKEN = "8116137907:AAH9mUJ3ycDiCD2-q30yd2c-8MgBsWLZzjo"
VK_ACCESS_TOKEN = "vk1.a.UMBKkFfVzBl9c5hEkRn8gFEurMfv_6EvnvPD5vNwbv3gxq3zYUmCabXdJ4wDWoE8nNfiZsjLQAaoffhNiFuAcHams6S8L2WVCZNCoNy3RbdVetFXPq2xPyjP0tcVhzGj1cTFncg2Rb8cLH0O9xDZCkMqdzPteJpVttnTegKwgpgLRF7TkIGY40N_I4_IjkCqjNWt5L7qQq7jjpdDcOIKDA"
VK_GROUP_ID = "-229441646"
VK_API_VERSION = "5.131"

# 🔹 Функция публикации текста в ВК
def post_to_vk(message):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "owner_id": VK_GROUP_ID,
        "from_group": 1,
        "message": message,
        "access_token": VK_ACCESS_TOKEN,
        "v": VK_API_VERSION,
    }
    response = requests.post(url, data=params)
    return response.json()

# 🔹 Функция загрузки фото в ВК
def upload_photo_to_vk(photo_url):
    upload_url = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params={"group_id": abs(int(VK_GROUP_ID)), "access_token": VK_ACCESS_TOKEN, "v": VK_API_VERSION},
    ).json()["response"]["upload_url"]

    photo_data = requests.get(photo_url).content
    upload_response = requests.post(upload_url, files={"photo": ("image.jpg", photo_data)}).json()

    save_photo = requests.get(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params={
            "group_id": abs(int(VK_GROUP_ID)),
            "photo": upload_response["photo"],
            "server": upload_response["server"],
            "hash": upload_response["hash"],
            "access_token": VK_ACCESS_TOKEN,
            "v": VK_API_VERSION,
        },
    ).json()

    photo_info = save_photo["response"][0]
    return f"photo{photo_info['owner_id']}_{photo_info['id']}"

# 🔹 Функция публикации фото в ВК
def post_photo_to_vk(photo_url, message=""):
    attachment = upload_photo_to_vk(photo_url)
    url = "https://api.vk.com/method/wall.post"
    params = {
        "owner_id": VK_GROUP_ID,
        "from_group": 1,
        "message": message,
        "attachments": attachment,
        "access_token": VK_ACCESS_TOKEN,
        "v": VK_API_VERSION,
    }
    response = requests.post(url, data=params)
    return response.json()

# 🔹 Функция загрузки видео в ВК
def upload_video_to_vk(video_url, title="Видео"):
    upload_server = requests.get(
        "https://api.vk.com/method/video.save",
        params={
            "group_id": abs(int(VK_GROUP_ID)),
            "name": title,
            "access_token": VK_ACCESS_TOKEN,
            "v": VK_API_VERSION,
        },
    ).json()["response"]["upload_url"]

    video_data = requests.get(video_url).content
    upload_response = requests.post(upload_server, files={"video_file": ("video.mp4", video_data)}).json()

    return f"video{upload_response['owner_id']}_{upload_response['video_id']}"

# 🔹 Функция публикации видео в ВК
def post_video_to_vk(video_url, message=""):
    attachment = upload_video_to_vk(video_url)
    url = "https://api.vk.com/method/wall.post"
    params = {
        "owner_id": VK_GROUP_ID,
        "from_group": 1,
        "message": message,
        "attachments": attachment,
        "access_token": VK_ACCESS_TOKEN,
        "v": VK_API_VERSION,
    }
    response = requests.post(url, data=params)
    return response.json()

# 🔹 Обработчик текстовых сообщений
async def telegram_text_handler(update: Update, context):
    text = update.message.text
    if text:
        post_to_vk(text)
        await update.message.reply_text("✅ Пост опубликован в ВК!")

# 🔹 Обработчик фото
async def telegram_photo_handler(update: Update, context):
    photo_file = update.message.photo[-1]
    file = await photo_file.get_file()
    photo_url = file.file_path
    post_photo_to_vk(photo_url, update.message.caption or "")
    await update.message.reply_text("📸 Фото опубликовано в ВК!")

# 🔹 Обработчик видео
async def telegram_video_handler(update: Update, context):
    video_file = update.message.video
    file = await video_file.get_file()
    video_url = file.file_path
    post_video_to_vk(video_url, update.message.caption or "")
    await update.message.reply_text("🎥 Видео опубликовано в ВК!")

# 🔹 Функция выключения бота
async def stop_bot():
    print("⏳ Остановка бота...")
    await app.shutdown()

# 🔹 Запускаем бота
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_text_handler))
app.add_handler(MessageHandler(filters.PHOTO, telegram_photo_handler))
app.add_handler(MessageHandler(filters.VIDEO, telegram_video_handler))

# 🔹 Настраиваем автоматическое выключение в 23:00
scheduler = AsyncIOScheduler()
scheduler.add_job(stop_bot, "cron", hour=23, minute=0)
scheduler.start()

print("✅ Бот запущен...")
app.run_polling()
