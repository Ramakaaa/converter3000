import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards import convert_keyboard
from converters import image_to_pdf, video_to_gif

router = Router()
USER_FILES = {}

@router.message(F.document | F.photo | F.video)
async def file_received(message: Message):
    USER_FILES[message.from_user.id] = message
    await message.answer(
        "Что сделать с файлом?",
        reply_markup=convert_keyboard()
    )

@router.callback_query(F.data == "img_to_pdf")
async def img_to_pdf(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.photo:
        await call.answer("Нужна картинка")
        return

    os.makedirs("temp", exist_ok=True)
    img_path = f"temp/{call.from_user.id}.jpg"
    pdf_path = f"temp/{call.from_user.id}.pdf"

    photo = msg.photo[-1]
    file = await call.bot.get_file(photo.file_id)
    await call.bot.download_file(file.file_path, img_path)

    image_to_pdf(img_path, pdf_path)

    document = FSInputFile(pdf_path)
    await call.message.answer_document(document)

@router.callback_query(F.data == "mp4_to_gif")
async def mp4_to_gif(call: CallbackQuery):
    msg = USER_FILES.get(call.from_user.id)
    if not msg or not msg.video:
        await call.answer("Нужно видео")
        return

    os.makedirs("temp", exist_ok=True)
    video_path = f"temp/{call.from_user.id}.mp4"
    gif_path = f"temp/{call.from_user.id}.gif"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    video_to_gif(video_path, gif_path)

    document = FSInputFile(gif_path)
    await call.message.answer_document(document)
