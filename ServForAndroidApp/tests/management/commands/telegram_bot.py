import os
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext
from django.core.management.base import BaseCommand
from django.apps import apps
from asgiref.sync import sync_to_async

# Получаем модель Student
Students = apps.get_model('stud', 'Students')

# Получаем токен бота
TELEGRAM_BOT_TOKEN = "7980000189:AAEh6pJh5QBx0UXagd_tsJJcWYjLh1jyRjg"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def start(update: Update, context: CallbackContext):
    """
    Обработчик команды /start.
    Сохраняет chat_id в поле connect_address.
    """
    chat_id = update.message.chat.id
    username = update.message.from_user.username

    if not username:
        await update.message.reply_text("У вас нет Telegram-username! Укажите его в настройках Telegram.")
        return

    # Используем sync_to_async для работы с БД
    student = await sync_to_async(Students.objects.filter, thread_sensitive=True)(connect_address=username)

    student = await sync_to_async(lambda: student.first(), thread_sensitive=True)()

    if student:
        student.connect_address = str(chat_id)
        await sync_to_async(student.save, thread_sensitive=True)()
        await update.message.reply_text(f"Привет, {username}! Ваш идентификатор чата сохранен!")
    else:
        await update.message.reply_text(f"Студент с таким ником не найден в базе данных {username}! Обратитесь к администратору.")


async def send_test_result(test_name, connect_address, points, mark, image=None):
    """
    Отправляет сообщение пользователю в Telegram.
    :param connect_address: chat_id студента
    :param points: Количество баллов
    :param mark: Полученная оценка
    :param image: Файл изображения (InMemoryUploadedFile)
    """

    chat_id = connect_address
    message = f"Ваши результаты теста «{test_name}»:\nБаллы: {points}\nОценка: {mark}"

    try:
        if image:
            image.seek(0)
            await bot.send_photo(chat_id=chat_id, photo=image, caption=message)
        else:
            await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        """Запускаем бота с использованием нового API"""
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))

        print("Бот запущен...")
        application.run_polling()
