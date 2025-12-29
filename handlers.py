import os
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards import convert_keyboard
from converters import (
    image_to_pdf,
    video_to_gif,
    video_to_mp3,
    png_to_jpg,
    docx_to_pdf,
    download_by_url
)

router = Router()
USER_FILES = {}
IN_PROGRESS = set()

UNSUPPORTED_MESSAGE = (
    "⛔️ Вы прислали сообщение или ссылку, которая не поддерживается ботом!\n\n"
    "📥 *Поддерживаемые ссылки:*\n\n"
    "*Instagram*\n"
    "Поддерживается: фото, видео, карусели.\n"
    "В разработке: истории, прямые эфиры.\n\n"
    "*Pinterest*\n"
    "Поддерживается: фото и видео.\n\n"
    "*TikTok*\n"
    "Поддерживается: видео.\n\n"
    "🔄 *Поддерживаемые конвертации:*\n"
    "🖼 JPG → PDF\n"
    "🖼 PNG → JPG\n"
    "🎥 MP4 → GIF\n"
    "🎵 MP4 → MP3\n"
    "📄 DOCX → PDF\n\n"
    "ℹ️ Просто отправьте файл или поддерживаемую ссылку."
)

AUTHOR_TEXT = "✅ Ваш файл готов\n\nАвтор: @Ramakaa"

URL_REGEX = re.compile(r"https?://\S+")

# ---------- АНТИСПАМ ----------
def is_busy(user_id: int) -> bool:
    return user_id in IN_PROGRESS

def set_busy(user_id: int):
    IN_PROGRESS.add(user_id)

def clear_busy(user_id: int):
    IN_PROGRESS.discard(user_id)

# ---------- ОБЩИЕ UX ----------
async def start_processing(call_or_msg, text: str):
    return await call_or_msg.answer(f"⏳ {text}")

async def finish_processing(process_msg: Message, chat_msg: Message, file_path: str):
    await process_msg.delete()
    await chat_msg.answer_document(FSInputFile(file_path))
    await chat_msg.answer(AUTHOR_TEXT)

# ---------- ПРИЁМ ФАЙЛОВ ----------
@router.message(F.document | F.photo | F.video)
async def file_received(message: Message):
    USER_FILES[message.from_user.id] = message
    await message.answer(
        "Выберите тип конвертации:",
        reply_markup=convert_keyboard()
    )

# ---------- ПРИЁМ ССЫЛОК ----------
@router.message(F.text)
async def link_received(message: Message):
    if not URL_REGEX.match(message.text):
        return

    user_id = message.from_user.id
    if is_busy(user_id):
        await message.answer("⏳ Подождите, предыдущая операция ещё выполняется")
        return

    set_busy(user_id)
    os.makedirs("temp", exist_ok=True)

    process_msg = await start_processing(message, "Скачивание по ссылке...")

    video_path = f"temp/{user_id}_url.mp4"

    try:
        download_by_url(message.text, video_path)
        await process_msg.delete()

        USER_FILES[user_id] = message
        message.video = type("Video", (), {"file_id": None})()  # заглушка
        await message.answer(
            "Видео скачано. Что дальше?",
            reply_markup=convert_keyboard()
        )

    except Exception as e:
        await process_msg.delete()
        await message.answer("❌ Ошибка при скачивании")
    finally:
        clear_busy(user_id)

# ---------- JPG → PDF ----------
@router.callback_query(F.data == "img_to_pdf")
async def img_to_pdf_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if is_busy(user_id):
        await call.answer("⏳ Уже выполняется")
        return
    set_busy(user_id)

    msg = USER_FILES.get(user_id)
    if not msg or not msg.photo:
        await call.answer("Нужна картинка")
        clear_busy(user_id)
        return

    process_msg = await start_processing(call.message, "Конвертация JPG → PDF...")

    os.makedirs("temp", exist_ok=True)
    img_path = f"temp/{user_id}.jpg"
    pdf_path = f"temp/{user_id}.pdf"

    photo = msg.photo[-1]
    file = await call.bot.get_file(photo.file_id)
    await call.bot.download_file(file.file_path, img_path)

    image_to_pdf(img_path, pdf_path)
    await finish_processing(process_msg, call.message, pdf_path)
    clear_busy(user_id)

# ---------- MP4 → MP3 ----------
@router.callback_query(F.data == "mp4_to_mp3")
async def mp4_to_mp3_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if is_busy(user_id):
        await call.answer("⏳ Уже выполняется")
        return
    set_busy(user_id)

    msg = USER_FILES.get(user_id)
    if not msg or not msg.video:
        await call.answer("Нужно видео")
        clear_busy(user_id)
        return

    process_msg = await start_processing(call.message, "Конвертация MP4 → MP3...")

    os.makedirs("temp", exist_ok=True)
    video_path = f"temp/{user_id}.mp4"
    mp3_path = f"temp/{user_id}.mp3"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    video_to_mp3(video_path, mp3_path)
    await finish_processing(process_msg, call.message, mp3_path)
    clear_busy(user_id)

# (остальные конвертации — по тому же паттерну)

@router.message()
async def unsupported_message(message: Message):
    await message.answer(
        UNSUPPORTED_MESSAGE,
        parse_mode="Markdown"
    )

