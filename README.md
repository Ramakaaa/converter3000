\# Telegram Converter Bot



Telegram-бот для конвертации файлов и медиа:

\- 🖼 JPG → PDF

\- 🖼 PNG → JPG

\- 🎥 MP4 → GIF

\- 🎵 MP4 → MP3

\- 📄 DOCX → PDF



Бот работает на \*\*aiogram 3.x\*\*, использует \*\*FFmpeg\*\* и \*\*LibreOffice\*\*.



---



\## 🚀 Возможности

\- Удобный UX с индикатором процесса

\- Автоматическая конвертация файлов

\- Поддержка изображений, видео и документов

\- Готов к деплою 24/7

\- Безопасное хранение токена (через `config.py`)



---



\## 📁 Структура проекта



converter\_bot/

│

├── bot.py

├── handlers.py

├── converters.py

├── keyboards.py

├── config.example.py

├── requirements.txt

├── .gitignore

└── temp/



---



\## 🧩 Зависимости



\### Python

\- Python \*\*3.11+\*\*



\### Системные утилиты

\- \*\*FFmpeg\*\*

\- \*\*LibreOffice\*\*



Они должны быть доступны из командной строки:

```bash

ffmpeg -version

soffice --version



⚙️ Установка и запуск (локально)



git clone https://github.com/USERNAME/REPO.git

cd converter\_bot



python -m venv venv

venv\\Scripts\\activate   # Windows

pip install -r requirements.txt



cp config.example.py config.py

\# вставь токен в config.py



python bot.py



🔐 Конфигурация

Файл config.py не хранится в репозитории.

Используй config.example.py как шаблон.



TOKEN = "PUT\_YOUR\_TELEGRAM\_BOT\_TOKEN\_HERE"



👤 Автор:

@Ramakaa

