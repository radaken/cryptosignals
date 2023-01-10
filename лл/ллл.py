import configparser
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import GetMessagesRequest
from telethon import functions, types
async def main():
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
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if not client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))
    channel = 'carprism'
    await client(JoinChannelRequest(channel))
    channelMessages = await client.get_messages(channel, limit=50)
    print(channelMessages[0].message)
    i = 0
    while (i != 10):
        if ('hello' in channelMessages[i].message):
            print('found hello')
        i=i+1


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
  loop.close()