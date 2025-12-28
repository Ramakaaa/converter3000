from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def convert_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 JPG → PDF", callback_data="img_to_pdf")],
        [InlineKeyboardButton(text="🎥 MP4 → GIF", callback_data="mp4_to_gif")]
    ])
