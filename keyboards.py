from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def convert_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 JPG → PDF", callback_data="img_to_pdf")],
        [InlineKeyboardButton(text="📄 DOCX → PDF", callback_data="docx_to_pdf")],
        [InlineKeyboardButton(text="🎥 MP4 → GIF", callback_data="mp4_to_gif")],
        [InlineKeyboardButton(text="🎵 MP4 → MP3", callback_data="mp4_to_mp3")],
        [InlineKeyboardButton(text="🖼 PNG → JPG", callback_data="png_to_jpg")]
    ])
