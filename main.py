import configparser                                             #Библиотека парсера config.ini конфигурационного файла

from telethon.sync import TelegramClient, events                #Библиотека для синхронной обработки кода и событий
from telethon.errors import SessionPasswordNeededError          #Библиотека для обработки исключений (если на аккаунте 2FA)
from telethon.tl.functions.channels import JoinChannelRequest   #Библиотека для входа в канал
from telethon.tl.functions.channels import GetMessagesRequest   #Библиотека для получения сообщений
from telethon import functions, types                           #Получаем в общем все типы и функции
import pymongo                                                  #Библиотека для MongoDB

import datetime                                                 #Библиотека для даты и времени



class Signal:                        # Объявляем класс
 
    def __init__(self):              # Объявляем конструктор и туда вносим переменные класса
        self.signal_type = None      # long/short
        self.sourceChannel = None    # Канал-источник    
        self.lever = None            # Рычаг (х10/x2)
        self.stoploss = None         # Стоплосс
        self.coin = None             # Валюта
        self.date = None             # Дата
        self.entry = None            # Entry
                            
def main():                          # Главная функция

    connection_url="mongodb://localhost:27017/"         #Адрес для монги
    dbclient=pymongo.MongoClient(connection_url)        #Создаём клиент
    mydb = dbclient["cryptosignals"]                    #Говорим, какую базу данных будем использовать
    mycol = mydb["junk"]                                #Говорим, какой столбец будем использовать (по умолчанию junk), если не сработает сортировка
    
    # Читаем конфиг
    config = configparser.ConfigParser()                #создаём парсер конфига
    config.read("config.ini")                           #название файла конфигурации

    # Задача значений из парсера: api_id, api_hash и т.д. данные конфиденциальны, поэтому мы должны доверять папке и среде, где храним конфиг
    api_id = config['Telegram']['api_id']               #my.telegram.org > my apps
    api_hash = config['Telegram']['api_hash']           #там же

    api_hash = str(api_hash)                            #явно преобразуем хэш в строку

    phone = config['Telegram']['phone']
    username = config['Telegram']['username']

    # Создаем клиент и подключаемся к Telegram
    client = TelegramClient(username, api_id, api_hash)
    client.start()
    print("Telegram client Created")
    # EУдостоверяемся, что мы вошли
    client_auth_status = client.is_user_authorized()
    if not client_auth_status:
        client.send_code_request(phone)                 #Если не вошли (нет файла %username%.session или возникли проблемы)
        try:
            client.sign_in(phone, input('Enter the code: '))        #Пробеум войти, требуем код подтверждения
        except SessionPasswordNeededError:                          #Если поймали исключение о том, что стоит 2FA
            client.sign_in(password=input('Password: '))            #Просим пароль

    channels = ['carprism', 'coincodecap', 'fatpig_cryptosignals', 'Coin_Signals', 'coincodecap']  #Создаём лист каналов для парсинга
    for channel in channels:
        parseChannel(client, channel, mydb, mycol)     #Вызываем функцию ниже, куда передаём клиент, канал (в порядке итерации), базу данных и столбец по-умолчанию
    
#Фунция парсинга каналов
def parseChannel(client, channel, mydb, mycol):
    client(JoinChannelRequest(channel))               #Делаем запрос на вступление в канал
    today = datetime.date.today()                     #Узнаем сегодняшнее число
    week_ago = today - datetime.timedelta(days=7)     #Осчитываем неделю назад

    channelMessages = client.get_messages(channel, limit=200, offset_date=week_ago)  #Записываем в переменную сообщения с канала за неделю с лимитом в 200 сообщ
    triggersCoin = ['USDT', 'BTC', 'ETH', 'LTC', 'XRP', 'DOGE']                      #Интересующие коины
    triggersType = ['LONG', 'Long', 'SHORT', 'Short']                                #Словарь типов сигнала
    triggersLever = ['Lever', 'LEVER', 'Leverage', 'LEVERAGE']                       #Словарь для нахождения плеча
    triggersStoploss = ['Stoploss', 'stoploss', 'Stop loss','STOP LOSS', 'Stop', 'stop']    #Словарь для стоп-позиции
    triggers = triggersCoin + triggersLever + triggersType + triggersLever + triggersStoploss  #Делаем набор триггеров для нужного сообщения
    i=0
    
    while (i != len(channelMessages)):        #Идёт прогонка (итерация) всех сообщений
    #Создаём экземпляр класса
        signal_instance = Signal()
        #Поиск на совпадения по словарю имени крипты и позиции LONG/SHORT (2 значения, чтобы было меньше мусора)
        if isTriggered(triggersCoin, channelMessages[i].message) and isTriggered(triggersType, channelMessages[i].message):
            
            print(f'Found this! in ', i)    #Можно убрать, показываем в каком сообщении затриггерились
            #Для удобства обрабатываемое сообщение записываем в переменную message
            message = channelMessages[i].message
            #Начало поиска по строкам, разбивка строк
            for line in message.splitlines():
                #Если в строке мы нашли любое значение связанное с криптой из словаря
                if isTriggered(triggersCoin, line):                                     # Поиск по коину
                    try:
                        signal_instance.coin = line.split(':')[1].upper()               # Запись КАПСОМ в класс нашего значения (после двоеточия)
                    except IndexError:                                                  # Если двоеточия не нашли
                        signal_instance.coin = line.upper()                             # , то записываем строку полностью
                if isTriggered(triggersLever, line):                                    # Поиск по плечу
                    try:
                        signal_instance.lever = line.split(':')[1].upper()
                    except IndexError:
                        signal_instance.lever = line.upper()
                if isTriggered(triggersType, line):                                     # Поиск по типу шорт/лонг
                    try:
                        signal_instance.signal_type = line.split(':')[1].upper()
                    except IndexError:
                        signal_instance.signal_type = line.upper()
                if isTriggered(triggersStoploss, line):                                 # Поиск по стоп-позиции
                    try:
                        signal_instance.stoploss = line.split(':')[1].upper()
                    except IndexError:
                        signal_instance.stoploss = line.upper()
                if 'Entry' in line:                                                     # Поиск по входным точкам, если есть
                    try:
                        signal_instance.entry = line.split(':')[1].upper()
                    except IndexError:
                        signal_instance.entry = line.upper()
            signal_instance.date = channelMessages[i].date                             # Запись даты сообщения в формате date
            signal_instance.sourceChannel = channel                                    # Запись канала, в котором нашли информацию
        #ENDIF isTriggered by 2 keyword -- Для удобства чтения
        try:
            if (signal_instance.coin is None) or (len(signal_instance.coin) > 35):     # Если мы затриггерились, но коин не нашли, или его значения больше 35 символов
                continue    # Не пишем в БД
            else:
                if Find(signal_instance.signal_type, 'LONG'):       #Иначе записываем ищем в строке с сигналом тип нашего сигнала
                    mydb.LONG.insert_one(vars(signal_instance))     #Пишем в БД все переменные класса
                if Find(signal_instance.signal_type, 'SHORT'):
                    mydb.SHORT.insert_one(vars(signal_instance))
                if Find(signal_instance.signal_type, 'MID'):
                    mydb.MID.insert_one(vars(signal_instance))
        except pymongo.errors.DuplicateKeyError:                   #Но если ID совпадает, то не пишем и выводим в консоль словленный exeption
            print('DuplicateKeyException')
        finally:                                                   # Но в любом случае удаляем наш класс и делаем шаг итерации
            del signal_instance 
            i=i+1
    #ENDWHILE -- Для удобства чтения

def isTriggered(triggers, message):            # Функция поиска триггеров в сообщении
    if message is None:                        # Если сообщение пустое, то возвращаем ЛОЖЬ
        return False
    for trigger in triggers:                   # Проходимся по триггерам
        try:
            if (trigger in message):           # Если находим, возращаем триггер (а в условия любое значение триггера вернет нам ИСТИНА)
                return trigger
        except:
            return False                       # Если возникнет ошибка: возвращаем ЛОЖЬ

def Find(obj, str):                            #Модифицированный поиск. Можно было воспользоваться "in", но магическим образом .find() работает лучше
    try:                                       #Поэтому пришлось писать костыль, может в новых версиях Python исправят
        if obj.find(str) == -1:                
            return False
        else:
            return True
    except:
        return False
        ### Если не находим, возращаем ЛОЖЬ, если находим ИСТИНА, если ошибка, то ЛОЖЬ

main()  #Вызов главной функции
