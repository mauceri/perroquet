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
import logging
import os
import anyio
from semaphore import Bot, ChatContext
from interrogationMixtralAnyscale import InterrogationMixtral

from sqlite_handler import SQLiteHandler

url = "https://api.endpoints.anyscale.com/v1"
iv = InterrogationMixtral(db_path='/amicusdb/amicus.sqlite',url=url)

async def echo(ctx: ChatContext) -> None:
    if not ctx.message.empty():
        profile = await ctx.message.get_profile()
        numero = profile.address.number
        name = profile.name
        await ctx.message.typing_started()
        question = ctx.message.get_body()
        logging.info(f"La question posée est : \"{question}\"")    
        transaction_id = iv.sqliteh.ajout_question(numero,question).lastrowid
        reponse_texte = ""
        try:
            reponse = iv.interroge_mixtral(numero,question);
            logging.info(f"Réponse de Mixtral \"{reponse}\"")
            r = reponse.json()["choices"][0]["message"]["content"]
            logging.info(f"Voici la réponse: {r}")
            iv.sqliteh.modification_reponse(numero, transaction_id,r)
            reponse_texte = f"N° {numero} :\nRéponse: \n<v>{r}</v>"
        except BaseException as e:
            print(f"Quelque chose n'a pas fonctionné au niveau de l'interrogation de Vigogne {e}")
            iv.sqliteh.remove_transaction(transaction_id)
            reponse_texte = f"N° {numero} :\nRéponse: \n<v>Erreur : Quelque chose n'a pas fonctionné</v>"
        logging.info(f"L'id de la transaction pour la question {question} est {transaction_id}")
        logging.info(f"******* {reponse_texte}")
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
