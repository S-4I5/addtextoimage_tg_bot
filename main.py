import asyncio
import os
import random
import string
import subprocess

import logging

from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token='')
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)


async def anti_flood(*args, **kwargs):
    ans = args[0]
    await ans.answer("Не спеши, бот никуда не убежит :)")


@dp.throttled(anti_flood, rate=1)
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n"
                     f"Отправь фото и задай теги для расположения на нём текста\n"
                     f"Список тегов можно посмотреть командой /tags")


@dp.throttled(anti_flood, rate=1)
@dp.message_handler(commands=['about'])
async def send_about(message: types.Message):
    await message.answer(f"Author: Полуэктов Яков 3530904/10005\n"
                     f"Source: https://github.com/S-4I5/addtextoimage_tg_bot\n")


@dp.throttled(anti_flood, rate=1)
@dp.message_handler(commands=['tags'])
async def get_tags(message: types.Message):
    await message.answer(f"Список тегов:"
                     f"text - текст, который будет изображён (DEFAULT: Place for your textXD)\n"
                     f"fontsize - размер шрифта (DEFAULT: 20)\n"
                     f"fontcolor - цвета шрифта (DEFAULT: white)\n"
                     f"x - x координата текста (DEFAULT: (w-text_w)/2)\n"
                     f"y - x координата текста (DEFAULT: (h-text_h)/2)\n"
                     f"Координаты могут быть заданы формулами вида (w-text_w)/2, где w - ширина изображения, а h - высота\n"
                     f"Теги должны быть заданы в формате tag:value и разделены запятыми\n"
                     f"Пример: text : I love Telegram!, fontsize : 20, fontcolor : red")


@dp.throttled(anti_flood, rate=1)
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def add_text(message: Message):
    random_name = get_random_file_name(10)
    await message.photo[-1].download(f'{random_name}.jpg')

    text_config = message.md_text.replace(" ", "")
    text_config = text_config.split(',')

    text = "Place for your textXD"
    fontsize = '20'
    x = '(w-text_w)/2'
    y = '(h-text_h)/2'
    fontcolor = 'white'

    for param in text_config:
        cur = param.split(':')

        match cur[0]:
            case 'text':
                text = cur[1]
            case 'fontsize':
                fontsize = cur[1]
            case 'x':
                x = cur[1]
            case 'y':
                y = cur[1]
            case 'fontcolor':
                fontcolor = cur[1]

    input_image = f'{random_name}.jpg'
    output_image = f'{random_name}_edit.jpg'

    subprocess.call([
        "ffmpeg", "-i", input_image, "-vf",
        f"drawtext=fontfile=arial.ttf:text='{text}':fontcolor={fontcolor}:fontsize={fontsize}:x={x}:y={y}",
        "-q:v", "1", output_image
    ])

    if not os.path.exists(output_image):
        await message.answer("Произошла ошибка при генерации изображения: "
                               "попробуйте перепроверить правильность написания тегов")

    with open(output_image, "rb") as photo:
        await bot.send_photo(message.chat.id, photo)

    os.remove(input_image)
    os.remove(output_image)


async def main():
    await dp.start_polling(bot)


def get_random_file_name(length):
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(length))


if __name__ == "__main__":
    asyncio.run(main())
