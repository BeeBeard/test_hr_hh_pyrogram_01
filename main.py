import re
import sqlite3
import asyncio
from icecream import ic
from datetime import datetime


from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatType


import settings
from conn import sql
from conn.engines import db_name, check_tables, rebuild_tables


client = Client(name='me_client', api_id=settings.api_id, api_hash=settings.api_hash)


@client.on_message()
def check_user_messages(_client: Client, msg: Message):
    """
    Проверяем обновления pyrogram
    :param _client:
    :param msg:
    :return:
    """

    if msg.chat.type != ChatType.PRIVATE or not msg.from_user:
        return

    if msg.from_user.is_self:  # Обработка сообщений бота
        ic("Сообщение от бота")
        text = msg.text or msg.caption
        if text:
            find_word = re.findall(settings.key_words, text, flags=re.I)
            if find_word:
                sql.update_user_data(id=msg.chat.id, status="finished", status_updated_at=datetime.now())

    else:  # Обработка сообщений от любого пользователя
        ic(msg)
        ic("Сообщение от пользователя")
        result = sql.get_user_data(msg.chat.id)
        if not result:  # Если пользователя нет в базе, записываем
            sql.update_user_data(
                id=msg.chat.id,
                status="alive",
                message_num=0,
                created_at=datetime.now(),  # Прописываем дополнительно, на случай разного разных часовых поясов
                status_updated_at=datetime.now())


async def send_message_to_user(chat_id: int = None, _num: int = 0) -> [bool, None]:
    """
    Функция отправки сообщения пользователю. Результат - успешно или нет
    :param chat_id:
    :param _num:
    :return:
    """

    if not chat_id or not settings.messages.get(_num):
        return None

    try:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(1)
        await client.send_message(chat_id=chat_id, text=settings.messages.get(_num))
        return True
    except Exception as e:
        ic(e)
        return False


async def task_send_messages():
    """
    Задача в цикле, для отправки сообщений по времени
    :return:
    """

    while True:
        try:

            user_list = sql.get_user_data_by_time()
            for i in user_list:

                msg_id_to_send = i.message_num + 1
                data_to_udate = {
                    "id": i.id,
                    "message_num": msg_id_to_send,
                    "status_updated_at": datetime.now()
                }

                if i.status == "finished" and i.message_num == 1:  # Если необходимо пропустить
                    sql.update_user_data(**data_to_udate)
                    continue

                min_interval = settings.intervals.get(msg_id_to_send)
                time_passed = ((datetime.now() - i.created_at).total_seconds()) / 60
                ic(min_interval, time_passed)
                if not min_interval or min_interval > time_passed:
                    print(f"Для чата {i.id} время для отправки не наступило")
                    continue
                print(f"Готовлю отправку сообщения в чат  {i.id}")

                result = await send_message_to_user(chat_id=i.id, _num=msg_id_to_send)

                if result is False:
                    data_to_udate["status"] = "dead"
                elif msg_id_to_send == 3:
                    data_to_udate["status"] = "finished"

                sql.update_user_data(**data_to_udate)

            await asyncio.sleep(settings.freq_check)  # Проверять на рассылку сообщения каждые N секунд
        except:
            pass


async def main():
    if not settings.api_id:
        while True:
            print(f"Введите корректный api_id здесь, или в файл с настройками settings")
            settings.api_id = input()
            if settings.api_id:
                break

    if not settings.api_hash:
        while True:
            print(f"Введите корректный api_hash здесь, или в файл с настройками settings")
            settings.api_hash = input()
            if settings.api_hash:
                break

    try:
        await client.start()
    except Exception as e:
        print(f"Возможно введены не коректные данные для api_id или api_hash")
        ic(e)
    asyncio.create_task(task_send_messages())


if __name__ == "__main__":
    connection = sqlite3.connect(db_name)
    check_tables()
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
