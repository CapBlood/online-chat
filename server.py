import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js, go_app

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100


async def main():
    global chat_msgs

    put_markdown("## 🧊 Добро пожаловать в онлайн чат!")

    user_list = output()
    put_row([
        put_column([
            put_markdown("### Участники").style("text-align: center"), None,
            put_scrollable(user_list, height=200, keep_bottom=True),
        ], size="20%"), None,
        put_column([
            put_markdown("### Правила").style("text-align: center"),
            put_markdown("1. Не материться.\n")
        ], size="20%")
    ])

    put_markdown("### Чат")
    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Войти в чат", required=True, placeholder="Ваше имя",
                           validate=lambda n: "Такой ник уже используется!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    for user in online_users:
        user_list.append(put_markdown(user))

    chat_msgs.append(('📢', f'`{nickname}` присоединился к чату!'))

    for m in chat_msgs:
        if m[0] in online_users:
            msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
        else:
            msg_box.append(put_markdown(f"`{m[0]}` - {m[1]}"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 Новое сообщение", [
            input(placeholder="Текст сообщения ...", name="msg"),
            actions(name="cmd", buttons=[
                "Отправить",
                {'label': "Выйти из чата", 'type': 'cancel'}
                # {'label': "Test", 'value': 'test'}
            ])
        ], validate=lambda m: ('msg', "Введите текст сообщения!") if m["cmd"] == "Отправить" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    # user_list.put_row([nickname])
    toast("Вы вышли из чата!")
    msg_box.append(put_markdown(f'📢 Пользователь `{nickname}` покинул чат!'))
    chat_msgs.append(('📢', f'Пользователь `{nickname}` покинул чат!'))

    put_buttons(['Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)
