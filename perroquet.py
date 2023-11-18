#!/usr/bin/env python
#
# Semaphore: A simple (rule-based) bot library for Signal Private Messenger.
# Copyright (C) 2020-2022 Lazlo Westerhof <semaphore@lazlo.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Signal Bot example, repeats received messages.
"""
import requests
import logging
import os
import signal
import sys
from collections import deque
import anyio
from semaphore import Bot, ChatContext

url = "https://mauceri--llama-cpp-python-nu-fastapi-app.modal.run"

class ChatHistory:
    def __init__(self, msg_limit):
        self.stack = deque(maxlen=msg_limit)

    def append(self, msg):
        return self.stack.append(msg)

    def get_as_list(self):
        return list(self.stack)

    def get_as_string(self):
        res = ""
        for e in self.get_as_list():
            res +=  e + "\n"
        return res

h = ChatHistory(5)

async def echo(ctx: ChatContext) -> None:
    if not ctx.message.empty():
        profile = await ctx.message.get_profile()
        number = profile.address.number
        name = profile.name
        await ctx.message.typing_started()
        question = ctx.message.get_body()
        logging.info(f"*******Question du {number} de {name} : {question} historique : {h.get_as_string()}")
        reponse = requests.post(f"{url}/question", json={"prompt":question,"context":h.get_as_string()})
        print(f'Response: {reponse.json()["choices"][0]["text"]}')
        r = reponse.json()["choices"][0]["text"]
        reponse_texte = f"N° {number} :\nRéponse: \n<v>{r}</v>\nhistorique: {h.get_as_string()}"
        logging.info(f"******* {reponse_texte}")
        h.append(f"[[SYS]]{question}[[/SYS]]")
        h.append(f"{r}</s>")
        await ctx.message.reply(reponse_texte)
        await ctx.message.typing_stopped()


async def main() -> None:
    """Start the bot."""
    # Connect the bot to number.
    async with Bot(os.environ["SIGNAL_PHONE_NUMBER"],
                   socket_path="/signald/signald.sock") as bot:
        bot.register_handler("", echo)
        logging.info("Lance le robot")
        # Run the bot until you press Ctrl-C.
        await bot.start()


if __name__ == '__main__':
    anyio.run(main)
