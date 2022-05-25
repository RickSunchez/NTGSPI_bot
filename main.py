import json
from typing import Tuple, Union
from telebot import TeleBot, types
from local_modules.path_worker.path_search import pathSearcher
from local_modules.site_parser.NTGSPIparser import Parser

from local_modules.vars.project_config import *
from local_modules.database_handler import dbHandler, router

# TODO:
# - add user create

def pp(o): print(json.dumps(o, indent=4, sort_keys=True, default=lambda o: o.__dict__))

with open(TELEGRAM_CRED, "r") as f:
    cred = json.load(f)

dbh = dbHandler.DBhandler(LOCAL_DATABASE, False)
r = router.Router(LOCAL_DATABASE)
bot = TeleBot(cred["telegram"]["token"])
np = Parser()

# np.sync()

bot.set_my_commands([
    types.BotCommand("/start", "Стоит начать с этой команды")
])

def workerPath(text:str, chat_id:int, user_id:int, message_id:Union[int, None]=None, serve:str="s", wai:object={}) -> None:
    kb = types.InlineKeyboardMarkup(row_width=5)
    answerText = wai["point"]["message"]
    onEdit = message_id is not None

    savedRowNum = 0
    savedRow = []
    serveAccords = {
        "s": "Выберите номер кабинета, который ближе всего к вам:",
        "d": "Выберите номер кабинета, который вам необходим:"
    }

    for key in wai["childs"]:
        child = wai["childs"][key]

        typeData = child["type"].split("?")

        if typeData[0] == "callback":
            kb.add(types.InlineKeyboardButton(
                    child["title"], callback_data=key))
        elif typeData[0] == "link":
            kb.add(
                types.InlineKeyboardButton(
                    child["title"], url=child["data"]))
        elif typeData[0] == "message":
            answerText = child["data"]
            onEdit = True
        elif typeData[0] == "grid":
            answerText = serveAccords[serve]
            
            typeGridData = typeData[1].split("&")
            grid = {}
            for tgd in typeGridData:
                tmp = tgd.split("=")
                grid[tmp[0]] = int(tmp[1])

            if savedRowNum == grid["row"]:
                savedRow.append(types.InlineKeyboardButton(
                    child["title"], 
                    callback_data=("%s%d" % (serve, grid["map"]))))
            else:
                savedRowNum = grid["row"]
                kb.add(*savedRow)
                savedRow = [
                    types.InlineKeyboardButton(
                        child["title"], 
                        callback_data=("%s%d" % (serve, grid["map"])))]

    return kb, answerText, onEdit

def workerService(text:str, chat_id:int, user_id:int, message_id:Union[int, None]=None, serve:str="s", wai:object={}) -> None:
    kb = types.InlineKeyboardMarkup(row_width=5)
    answerText = "none"

    if wai["action"] == "calcPath":
        us = dbh.getUserStorage(user_id)
        ps = pathSearcher()

        answerText = ps.getPathLegend(
            ps.minPath(us["source"], us["destination"])
        )

    return kb, answerText, True

def worker(text:str, chat_id:int, user_id:int, message_id:Union[int, None]=None, serve:str="s") -> None:
    kb = []

    dbh.addNewUser(user_id) # MOVE
    wai = r.pwd(user_id)

    if wai["type"] == "service":
        kb, answerText, onEdit = workerService(text, chat_id, user_id, message_id, serve, wai)
    elif wai["type"] == "path":
        kb, answerText, onEdit = workerPath(text, chat_id, user_id, message_id, serve, wai)


    if wai["type"] == "service" or wai["point"]["title"] != "root":
        kb.add(types.InlineKeyboardButton("Назад", callback_data="back"))
    if len(wai["full_path"].split("/")) > 2:
        kb.add(types.InlineKeyboardButton("Основное меню", callback_data="root"))
    
    if onEdit:
        bot.edit_message_text(
            text=answerText, 
            chat_id=chat_id, 
            message_id=message_id,
            reply_markup=kb
        )
    else:
        bot.send_message(
            text=answerText,
            chat_id=chat_id,
            reply_markup=kb)

@bot.message_handler(content_types=["text"])
def messageHandle(message):
    userId = int(message.from_user.id)
    chatId = int(message.chat.id)
    text = message.text.lower()

    worker(text, chatId, userId)
    

@bot.callback_query_handler(func=lambda call: True)
def callbackHandle(callback):
    userId = int(callback.from_user.id)
    chatId = int(callback.message.chat.id)
    messageId = int(callback.message.id)

    dbh.addNewUser(userId) # DEL

    onNav = True

    if "back" in callback.data:
        r.back(userId)
    elif "root" in callback.data:
        r.home(userId)
    elif "s" in callback.data:
        onNav = False
        pointId = int(callback.data.replace("s", ""))
        r.touch(userId, data={"source": pointId})
        serve = "d"
    elif "d" in callback.data:
        pointId = int(callback.data.replace("d", ""))
        r.touch(userId, data={"destination": pointId})
        r.cd(userId, 9999)
    elif callback.data.isdigit():
        r.cd(userId, int(callback.data))
    
    if onNav:
        worker(text="", chat_id=chatId, user_id=userId, message_id=messageId)
    else:
        worker(text="", chat_id=chatId, user_id=userId, message_id=messageId, serve=serve)

bot.polling()