import os
import re
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile
)

from keyboards import convert_keyboard
from converters import (
    image_to_pdf,
    png_to_jpg,
    video_to_gif,
    video_to_mp3,
    docx_to_pdf,
    download_by_url
)

router = Router()

# ================== СОСТОЯНИЕ ==================
USER_FILES: dict[int, Message] = {}
IN_PROGRESS: set[int] = set()

AUTHOR_TEXT = "Автор: @Ramakaa"

UNSUPPORTED_MESSAGE = (
    "⛔️ Вы прислали сообщение или ссылку, которая не поддерживается ботом!\n\n"
    "📥 *Поддерживаемые ссылки:*\n"
    "• Pinterest — фото и видео\n"
    "• TikTok — видео (через VPN)\n"
    "• YouTube — видео (часто ограничено)\n\n"
    "🔄 *Поддерживаемые конвертации:*\n"
    "🖼 JPG → PDF\n"
    "🖼 PNG → JPG\n"
    "🎥 MP4 → GIF\n"
    "🎵 MP4 → MP3\n"
    "📄 DOCX → PDF\n\n"
    "ℹ️ Отправьте файл или поддерживаемую ссылку."
)

URL_RE = re.compile(r"https?://")


# ================== АНТИСПАМ ==================
def busy(uid: int) -> bool:
    return uid in IN_PROGRESS


def set_busy(uid: int):
    IN_PROGRESS.add(uid)


def clear_busy(uid: int):
    IN_PROGRESS.discard(uid)


# ================== UX ==================
async def start_processing(message: Message, text: str) -> Message:
    return await message.answer(f"⏳ {text}")


async def finish_processing(process_msg: Message, message: Message, path: str):
    try:
        await process_msg.delete()
    except:
        pass

    await message.answer_document(FSInputFile(path))
    await message.answer(f"✅ Готово\n\n{AUTHOR_TEXT}")


# ================== ПРИЁМ ФАЙЛОВ ==================
@router.message(F.document | F.photo | F.video)
async def file_received(message: Message):
    USER_FILES[message.from_user.id] = message
    await message.answer(
        "Выберите тип конвертации:",
        reply_markup=convert_keyboard()
    )


# ================== СКАЧИВАНИЕ ПО ССЫЛКЕ ==================
@router.message(F.text.regexp(r"https?://"))
async def link_received(message: Message):
    uid = message.from_user.id

    if busy(uid):
        await message.answer("⏳ Подождите, операция уже выполняется")
        return

    set_busy(uid)
    temp_dir = f"temp/{uid}"
    os.makedirs(temp_dir, exist_ok=True)

    status = await message.answer("⏳ Скачивание по ссылке...")

    try:
        result = download_by_url(message.text, temp_dir)
        await status.delete()

        if result["type"] == "photo":
            for p in result["files"]:
                await message.answer_photo(
                    FSInputFile(p),
                    caption=f"✅ Фото скачано\n\n{AUTHOR_TEXT}"
                )

        elif result["type"] == "video":
            for p in result["files"]:
                await message.answer_video(
                    FSInputFile(p),
                    caption=f"✅ Видео скачано\n\n{AUTHOR_TEXT}"
                )

    except Exception as e:
        try:
            await status.delete()
        except:
            pass

        text = str(e).lower()
        if "youtube" in text:
            await message.answer("⛔️ YouTube ограничил загрузку видео.")
        elif "tiktok" in text:
            await message.answer("⛔️ TikTok заблокировал IP (VPN помогает).")
        else:
            await message.answer(UNSUPPORTED_MESSAGE, parse_mode="Markdown")

    finally:
        clear_busy(uid)


# ================== КОНВЕРТАЦИИ ==================

@router.callback_query(F.data == "img_to_pdf")
async def img_to_pdf_handler(call: CallbackQuery):
    uid = call.from_user.id
    if busy(uid):
        await call.answer("⏳ Уже выполняется")
        return

    msg = USER_FILES.get(uid)
    if not msg or not msg.photo:
        await call.answer("Нужна картинка")
        return

    set_busy(uid)
    os.makedirs("temp", exist_ok=True)

    img_path = f"temp/{uid}.jpg"
    pdf_path = f"temp/{uid}.pdf"

    file = await call.bot.get_file(msg.photo[-1].file_id)
    await call.bot.download_file(file.file_path, img_path)

    process = await start_processing(call.message, "Конвертация JPG → PDF...")
    image_to_pdf(img_path, pdf_path)
    await finish_processing(process, call.message, pdf_path)
    clear_busy(uid)


@router.callback_query(F.data == "png_to_jpg")
async def png_to_jpg_handler(call: CallbackQuery):
    uid = call.from_user.id
    msg = USER_FILES.get(uid)

    if not msg or not msg.document:
        await call.answer("Нужен PNG файл")
        return

    set_busy(uid)
    os.makedirs("temp", exist_ok=True)

    png_path = f"temp/{uid}.png"
    jpg_path = f"temp/{uid}.jpg"

    file = await call.bot.get_file(msg.document.file_id)
    await call.bot.download_file(file.file_path, png_path)

    process = await start_processing(call.message, "Конвертация PNG → JPG...")
    png_to_jpg(png_path, jpg_path)
    await finish_processing(process, call.message, jpg_path)
    clear_busy(uid)


@router.callback_query(F.data == "mp4_to_mp3")
async def mp4_to_mp3_handler(call: CallbackQuery):
    uid = call.from_user.id
    msg = USER_FILES.get(uid)

    if not msg or not msg.video:
        await call.answer("Нужно видео")
        return

    set_busy(uid)
    os.makedirs("temp", exist_ok=True)

    video_path = f"temp/{uid}.mp4"
    mp3_path = f"temp/{uid}.mp3"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    process = await start_processing(call.message, "Конвертация MP4 → MP3...")
    video_to_mp3(video_path, mp3_path)
    await finish_processing(process, call.message, mp3_path)
    clear_busy(uid)


@router.callback_query(F.data == "mp4_to_gif")
async def mp4_to_gif_handler(call: CallbackQuery):
    uid = call.from_user.id
    msg = USER_FILES.get(uid)

    if not msg or not msg.video:
        await call.answer("Нужно видео")
        return

    set_busy(uid)
    os.makedirs("temp", exist_ok=True)

    video_path = f"temp/{uid}.mp4"
    gif_path = f"temp/{uid}.gif"

    file = await call.bot.get_file(msg.video.file_id)
    await call.bot.download_file(file.file_path, video_path)

    process = await start_processing(call.message, "Конвертация MP4 → GIF...")
    video_to_gif(video_path, gif_path)
    await finish_processing(process, call.message, gif_path)
    clear_busy(uid)


@router.callback_query(F.data == "docx_to_pdf")
async def docx_to_pdf_handler(call: CallbackQuery):
    uid = call.from_user.id
    msg = USER_FILES.get(uid)

    if not msg or not msg.document:
        await call.answer("Нужен DOCX файл")
        return

    set_busy(uid)
    os.makedirs("temp", exist_ok=True)

    docx_path = f"temp/{uid}.docx"

    file = await call.bot.get_file(msg.document.file_id)
    await call.bot.download_file(file.file_path, docx_path)

    process = await start_processing(call.message, "Конвертация DOCX → PDF...")
    docx_to_pdf(docx_path, "temp")

    pdf_path = docx_path.replace(".docx", ".pdf")
    await finish_processing(process, call.message, pdf_path)
    clear_busy(uid)


# ================== FALLBACK ==================
@router.message()
async def fallback(message: Message):
    await message.answer(UNSUPPORTED_MESSAGE, parse_mode="Markdown")
