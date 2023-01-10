import configparser
import json
from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import GetMessagesRequest
from telethon import functions, types
import pymongo



short_dict = {} #Dictionary for short
mid_dict = {} #Dictionary for medium
long_dict = {} #Dictionary for long
all_dict = {} #Dictionary for all

class Signal:
 
    def __init__(self):
        self.signal_type = "undefined"      # long/short
        self.sourceChannel = "undefined"    # Канал-источник    
        self.lever = "undefined"            # Рычаг (х10/x2)
        self.target = "undefined"           # Контрольные точки
        self.stoploss = "undefined"         # Стоплосс
        self.coin = "undefined"             # Валюта
        self.date = "undefined"             # Дата
    # def scrap_and_set_val(self, line, _dict, value):
    #     for keyword in _dict:
    #                     if line.find(keyword):
    #                         try:
    #                             self.value = line.split(':')[1].upper()
    #                         except IndexError:
    #                             self.value = line.upper()
    #                         except:
    #                             print('Throwing unknown exeption in scrap_and_set_val')
                            
    def upload(self, mydb, mycol='mycol'):
        mydb.mycol.insert(self.__dict__)
def main():

    connection_url="mongodb://localhost:27017/"
    dbclient=pymongo.MongoClient(connection_url)
    dblist = dbclient.list_database_names()
    mydb = dbclient["cryptosignals"]
    mycol = mydb["customers"]
    mydb.mycol.insert_one({"test": 'test'})
    dblist = dbclient.list_database_names()
    if "mydatabase" in dblist:
        print("The database exists.")
    
    # Reading Configs
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Setting configuration values
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']

    api_hash = str(api_hash)

    phone = config['Telegram']['phone']
    username = config['Telegram']['username']

    # Create the client and connect
    client = TelegramClient(username, api_id, api_hash)
    client.start()
    print("Client Created")
    # Ensure you're authorized
    client_auth_status = client.is_user_authorized()
    if not client_auth_status:
        client.send_code_request(phone)
        try:
            client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Password: '))
    #channel = 'fatpig_cryptosignals'
    channel = 'carprism'
    client(JoinChannelRequest(channel))
    channelMessages = client.get_messages(channel, limit=50)

    
    triggersCoin = ['USDT', 'BTC', 'ETH', 'LTC', 'XRP', 'DOGE']
    triggersType = ['LONG', 'Long', 'SHORT', 'Short']
    triggersLever = ['LONG', 'Long', 'SHORT', 'Short']
    triggersStoploss = ['Stoploss', 'Stop loss']
    triggers = triggersCoin + triggersLever + triggersType + triggersLever + triggersStoploss
    i=0
    while (i != 10):        #Идёт прогонка (итерация) всех сообщений
        
        #Поиск на совпадения по словарю имени крипты и позиции LONG/SHORT (2 значения, чтобы было меньше мусора)
        if isTriggered(triggersCoin, channelMessages[i].message) and isTriggered(triggersType, channelMessages[i].message):
            #Создаём экземпляр класса
            signal_instance = Signal()
            print(f'Found this! in ', i)
            #Для удобства обрабатываемое сообщение записываем в переменную message
            message = channelMessages[i].message
            #Начало поиска по строкам, разбивка строк
            for line in message.splitlines():
                #Если в строке мы нашли любое значение связанное с криптой из словаря
                if isTriggered(triggers, line):
                    #print('Triggerd line ->', line)
                    #print('***')
                    #print(line.split(':')[1])
                    

                    
                    for keyword in triggersCoin:
                        print ('KEYWORD IS' , keyword)
                        if line.find(keyword):
                            print ('FOUND ' , keyword, 'ON LINE ', line)
                            try:
                                signal_instance.coin = line.split(':')[1].upper()
                                print ('WRITING IN CLASS THIS' , signal_instance.coin)
                            except IndexError:
                                signal_instance.coin = line.upper()
                                print('EXEPTION WORKED WRITING ',signal_instance.coin )
                            finally:
                                #print(vars(signal_instance))
                                break

                    # for keyword in triggersLever:
                    #     if line.find(keyword):
                    #         signal_instance.lever = line.split(':')[1].upper()
                    # for keyword in triggersType:
                    #     if line.find(keyword):
                    #         signal_instance.signal_type = line.split(':')[1].upper()
                    # for keyword in triggersStoploss:
                    #     if line.find(keyword):
                    #         signal_instance.coin = line.split(':')[1].upper()
                    
                    # signal_instance.scrap_and_set_val(line, triggersCoin, 'coin')
                    # signal_instance.scrap_and_set_val(line, triggersLever, 'lever')
                    # signal_instance.scrap_and_set_val(line, triggersType, 'signal_type')
                    # signal_instance.scrap_and_set_val(line, triggersStoploss, 'stoploss')

                    # scrap_and_set_val(signal_instance, line, triggersCoin, 'coin')
                    # scrap_and_set_val(signal_instance, line, triggersLever, 'lever')
                    # scrap_and_set_val(signal_instance, line, triggersType, 'signal_type')
                    # scrap_and_set_val(signal_instance, line, triggersStoploss, 'stoploss')

                    #signal_instance.upload(mydb)
                    #mydb.mycol.insertMany(signal_instance.__dict__)
                    #print('***')
            ## DEV ONLY ##
            # print('do yo want to display it?')
            # answ = input()
            # if (answ == '1'):
            #     print(channelMessages[i].message)
            ## DEV END ##
        i=i+1

def scrap_and_set_val(_class, line, _dict, value):
    for keyword in _dict:
                    if line.find(keyword):
                        try:
                            _class.value = line.split(':')[1].upper()
                        except IndexError:
                            _class.value = line.upper()
                        except:
                            print('Throwing unknown exeption in scrap_and_set_val')
def isTriggered(triggers, message):
    for trigger in triggers:
        if (trigger in message):
            return True
def create_signal(message):
    pass
main()
