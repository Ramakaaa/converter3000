import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards import convert_keyboard
from converters import (
    image_to_pdf,
    video_to_gif,
    video_to_mp3,
    png_to_jpg,
    docx_to_pdf
)

router = Router()
USER_FILES = {}

AUTHOR_TEXT = "✅ Ваш файл готов\n\nАвтор бота: @Ramakaa"

@router.message(F.document | F.photo | F.video)
async def file_received(message: Message):
    USER_FILES[message.from_user.id] = message
    await message.answer(
        "Выберите тип конвертации:",
        reply_markup=convert_keyboard()
    )

async def start_processing(call: CallbackQuery, text: str):
    msg = await call.message.answer(f"⏳ {text}")
    return msg

async def finish_processing(process_msg: Message, call: CallbackQuery, file_path: str):
    await process_msg.delete()

    await call.message.answer_document(
        FSInputFile(file_path)
    )

    await call.message.answer(AUTHOR_TEXT)

# ---------- JPG → PDF ----------
@router.callback_query(F.data == "img_to_pdf")
async def img_to_pdf_handler(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.photo:
        await call.answer("Нужна картинка")
        return

    process_msg = await start_processing(call, "Конвертация JPG → PDF...")

    os.makedirs("temp", exist_ok=True)
    img_path = f"temp/{call.from_user.id}.jpg"
    pdf_path = f"temp/{call.from_user.id}.pdf"

    photo = msg.photo[-1]
    file = await call.bot.get_file(photo.file_id)
    await call.bot.download_file(file.file_path, img_path)

    image_to_pdf(img_path, pdf_path)
    await finish_processing(process_msg, call, pdf_path)

# ---------- MP4 → GIF ----------
@router.callback_query(F.data == "mp4_to_gif")
async def mp4_to_gif_handler(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.video:
        await call.answer("Нужно видео")
        return

    process_msg = await start_processing(call, "Конвертация MP4 → GIF...")

    os.makedirs("temp", exist_ok=True)
    video_path = f"temp/{call.from_user.id}.mp4"
    gif_path = f"temp/{call.from_user.id}.gif"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    video_to_gif(video_path, gif_path)
    await finish_processing(process_msg, call, gif_path)

# ---------- MP4 → MP3 ----------
@router.callback_query(F.data == "mp4_to_mp3")
async def mp4_to_mp3_handler(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.video:
        await call.answer("Нужно видео")
        return

    process_msg = await start_processing(call, "Конвертация MP4 → MP3...")

    os.makedirs("temp", exist_ok=True)
    video_path = f"temp/{call.from_user.id}.mp4"
    mp3_path = f"temp/{call.from_user.id}.mp3"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    video_to_mp3(video_path, mp3_path)
    await finish_processing(process_msg, call, mp3_path)

# ---------- PNG → JPG ----------
@router.callback_query(F.data == "png_to_jpg")
async def png_to_jpg_handler(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.document:
        await call.answer("Нужен PNG файл")
        return

    process_msg = await start_processing(call, "Конвертация PNG → JPG...")

    os.makedirs("temp", exist_ok=True)
    png_path = f"temp/{call.from_user.id}.png"
    jpg_path = f"temp/{call.from_user.id}.jpg"

    file = await call.bot.get_file(msg.document.file_id)
    await call.bot.download_file(file.file_path, png_path)

    png_to_jpg(png_path, jpg_path)
    await finish_processing(process_msg, call, jpg_path)

# ---------- DOCX → PDF ----------
@router.callback_query(F.data == "docx_to_pdf")
async def docx_to_pdf_handler(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.document:
        await call.answer("Нужен DOCX файл")
        return

    process_msg = await start_processing(call, "Конвертация DOCX → PDF...")

    os.makedirs("temp", exist_ok=True)
    docx_path = f"temp/{call.from_user.id}.docx"

    file = await call.bot.get_file(msg.document.file_id)
    await call.bot.download_file(file.file_path, docx_path)

    docx_to_pdf(docx_path, "temp")
    pdf_path = docx_path.replace(".docx", ".pdf")

    await finish_processing(process_msg, call, pdf_path)
