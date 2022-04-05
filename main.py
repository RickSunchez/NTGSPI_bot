import telebot
import json

from telebot import types

from parse import NTGSPIparser
from map_worker import pathSearcher
from simple_router import Router

try:
    with open("./credentials.json", "r") as f:
        cred = json.load(f)
except Exception as ex:
    print(ex)
    exit()

bot = telebot.TeleBot(cred["telegram"]["token"])
np = NTGSPIparser()
ps = pathSearcher(file="map.csv", titles=True)
ps.legendFromFile("map_titles.json")
router = Router()

np.sync()

def atStart(chatID):
    kb = types.ReplyKeyboardMarkup()
    text = ["Показать расписание", "Контакты для связи", "Шаблоны документов", "Навигация"]

    for t in text:
        kb.add(types.KeyboardButton(text=t))

    bot.send_message(chatID, text="Что-то делать:", reply_markup=kb)
def showFacultet(chatID):
    kb = types.ReplyKeyboardMarkup()
    for name in np.getFacultetList():
        kb.add(types.KeyboardButton(text=name))
    
    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Выбрать факультет", reply_markup=kb)

def showGroups(chatID, facultet):
    kb = types.ReplyKeyboardMarkup()
    for f in np.getFacultetGroups(facultet):
        kb.add(types.KeyboardButton(text=f))

    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Выбрать группу", reply_markup=kb)

def sendShedule(chatID, group):
    print(group)
    l = ""
    for f in np.shedule():
        if f["facultet"] == router.whereAmI():
            for s in f["shedule"]:
                if s["group"] == group:
                    l = s["link"]
            break

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(group, url=l))
    
    bot.send_message(chatID, text="Вот твое расписание:", reply_markup=kb)

def showDepartment(chatID):
    kb = types.ReplyKeyboardMarkup()
    for t in np.getContactsDepartment():
        kb.add(types.KeyboardButton(text=t))

    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Выберите отдел:", reply_markup=kb)

def sendContacts(chatID, department):
    kb = types.ReplyKeyboardMarkup()
    for t in np.getContactsDepartment():
        kb.add(types.KeyboardButton(text=t))

    kb.add(types.KeyboardButton(text="Назад"))

    messages = []
    for n in np.numbers():
        if n["title"] == department:
            for s in n["subs"]:
                msg  = "Отдел: %s\n" % s["name"]
                msg += "Ответственный: %s\n" % s["head"]
                msg += "Телефон: %s\n" % s["phone"]
                msg += "email: %s\n" % s["mail"]
                msg += "сайт: %s\n" % s["site"]

                messages.append(msg)
            break

    bot.send_message(chatID, text="\n\n".join(messages), reply_markup=kb)

def showTemplates(chatID):
    kb = types.ReplyKeyboardMarkup()

    for t in np.getTemplatesTitles():
        kb.add(types.KeyboardButton(text=t))

    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Тип шаблонов", reply_markup=kb)

def showTemplatesList(chatID, tt):
    messages = []

    for temp in np.templates():
        if temp["title"] == tt:
            for i, doc in enumerate(temp["docs"]):
                if i % 10 == 0: messages.append(types.InlineKeyboardMarkup())

                n = doc["name"].replace("образец заявления_", "")
                messages[i // 10].add(types.InlineKeyboardButton(n, url=doc["link"]))
            break
    
    bot.send_message(chatID, text="Доступные шаблоны")
    for i, kb in enumerate(messages):
        bot.send_message(chatID, text="Страница: %d" % (i+1), reply_markup=kb)

def showEntryPoints(chatID):
    kb = types.ReplyKeyboardMarkup()

    for key in ps.legend:
        if "e" in ps.legend[key]: continue

        kb.add(types.KeyboardButton(text=ps.legend[key]))

    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Выберите ближайший от вас кабинет:", reply_markup=kb)

def showDestinationPoints(chatID, entryPoint):
    kb = types.ReplyKeyboardMarkup()
    
    for key in ps.legend:
        if "e" in ps.legend[key]: continue
        if ps.legend[key] == entryPoint:
            ps.entry = int(key)
            continue

        kb.add(types.KeyboardButton(text=ps.legend[key]))

    kb.add(types.KeyboardButton(text="Назад"))

    bot.send_message(chatID, text="Выберите куда вам надо:", reply_markup=kb)

def sendRoute(chatID, destPoint):
    for key in ps.legend:
        if ps.legend[key] == destPoint:
            ps.dest = int(key)
            break
    
    kb = types.ReplyKeyboardMarkup()
    kb.add(types.KeyboardButton(text="Новый поиск"))

    bot.send_message(chatID, text=ps.calc(), reply_markup=kb)

@bot.message_handler(content_types=["text"])
def handle(message):
    if message.text.lower() == "/start":
        pass
    # Расписание:
    elif message.text == "Показать расписание":
        router.moveTo("shedule")
    elif message.text in np.getFacultetList():
        router.moveTo(message.text)
    elif message.text in np.getFacultetGroups(router.whereAmI()):
        router.lock(message.text)
    # Контакты:
    elif message.text == "Контакты для связи":
        router.moveTo("contacts")
    elif message.text in np.getContactsDepartment():
        router.lock(message.text)
    # Шаблоны
    elif message.text == "Шаблоны документов":
        router.moveTo("templates")
    elif message.text in np.getTemplatesTitles():
        router.lock(message.text)
    # Навигация
    elif message.text == "Навигация":
        router.moveTo("navigation")
    elif router.whereAmI() == "navigation" and message.text.isdigit():
        router.moveTo("entry")
    elif router.whereAmI() == "entry" and message.text.isdigit():
        router.lock(message.text)
    elif message.text == "Новый поиск":
        router.back()
    # Общее
    elif message.text == "Назад":
        router.back()
    else:
        bot.send_message(message.chat.id, text="Неизвестная команда")
        return

    wai = router.whereAmI()
    isLocked = not router.status

    if wai == "root":
        atStart(message.chat.id)
    # Расписание:
    elif wai == "shedule":
        showFacultet(message.chat.id)
    elif (not isLocked) and (wai in np.getFacultetList()):
        showGroups(message.chat.id, wai)
    elif isLocked and (router.data in np.getFacultetGroups(wai)):
        sendShedule(message.chat.id, router.data)
        router.unlock()
    # Контакты:
    elif (not isLocked) and (wai == "contacts"):
        showDepartment(message.chat.id)
    elif isLocked and (wai == "contacts"):
        sendContacts(message.chat.id, router.data)
        router.unlock()
    # Шаблоны:
    elif (not isLocked) and (wai == "templates"):
        showTemplates(message.chat.id)
    elif isLocked and (wai == "templates"):
        showTemplatesList(message.chat.id, router.data)
        router.unlock()
    # Навигация
    elif wai == "navigation":
        showEntryPoints(message.chat.id)
    elif (not isLocked) and (wai == "entry"):
        showDestinationPoints(message.chat.id, message.text)
    elif isLocked and (wai == "entry"):
        sendRoute(message.chat.id, router.data)
        router.unlock()

bot.polling()