# 🚀 Космический Телеграм Бот

Набор скриптов для автоматической публикации космических фотографий в Telegram-канал из различных источников: NASA APOD, NASA EPIC и SpaceX.

## 📦 Установка

### Требования
- Python 3.8+
- Аккаунты на [api.nasa.gov](https://api.nasa.gov/) и в Telegram

### Шаги установки
1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-репозиторий/космический-телеграм.git
cd космический-телеграм

2. Установите зависимости:

'''bash
pip install -r requirements.txt
'''
3. Создайте файл .env и добавьте ключи:

'''ini
NASA_API_KEY=ваш_ключ_nasa
TELEGRAM_TOKEN=ваш_токен_бота
TELEGRAM_CHANNEL=@ваш_канал
'''
## 🛠 Использование
### Скачивание фотографий
Скрипт	Описание	Пример
fetch_spacex_images.py	Скачивает фото последнего запуска SpaceX	python fetch_spacex_images.py --output spacex_photos
fetch_nasa_epic.py	Скачивает фото Земли от NASA EPIC	python fetch_nasa_epic.py --count 5
fetch_nasa_apod.py	Скачивает Astronomy Picture of Day	python fetch_nasa_apod.py --count 10
### Публикация в Telegram
Скрипт	Описание	Пример
publish_photo.py	Публикует одну случайную или указанную фотографию	python publish_photo.py --photo apod_20230101.jpg
publish_loop.py	Автопубликация с интервалом (по умолчанию 4 часа)	python publish_loop.py --interval 6
## 🔧 Настройка
Параметры .env
Переменная	Описание	Пример значения
NASA_API_KEY	Ключ API NASA	DEMO_KEY (для теста)
TELEGRAM_TOKEN	Токен бота Telegram	123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHANNEL	ID канала (начинается с @ или -100)	@my_space_channel
## 🎯 Цель проекта
Проект разработан в образовательных целях для:

Практики работы с API (NASA, SpaceX, Telegram)

Автоматизации публикации контента

Отработки обработки ошибок и логирования

Использования асинхронного программирования

Разработано в рамках обучения на dvmn.org

## 📂 Структура проекта
cosmic-telegram/
├── fetch_spacex_images.py    # Загрузка фото SpaceX
├── fetch_nasa_epic.py        # Загрузка NASA EPIC
├── fetch_nasa_apod.py        # Загрузка NASA APOD
├── publish_photo.py          # Публикация одной фото
├── publish_loop.py           # Автопубликация
├── space_utils.py            # Вспомогательные функции
├── requirements.txt          # Зависимости
├── .env.example              # Пример конфига
└── README.md                 # Документация
⚠️ Ограничения
Максимальный размер фото для Telegram: 20MB

Лимиты API NASA: 1000 запросов/час (DEMO_KEY: 30 запросов/час)

Для приватных каналов используйте ID канала (начинается с -100)

💡 Совет: Для обработки больших изображений можно добавить сжатие через Pillow в space_utils.py
