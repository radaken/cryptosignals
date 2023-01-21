# Telegram crypto scrapper
Parse/grab/scrap cryptosignals in Telegram channels, sort it and save in MongoDB and works on Telethon

## You wanna know

This isn't pet-project, I made this as order. Production build I cannot to upload (NDA), but some dev version I allowed to show. This code supplied "as is" and I just want to share this because it has "line-by-line" :ru: comments and maybe help you to understand Python, MongoDB, parsing, sorting etc. [Telegram me!](https://iamradaken.t.me/) :ru: :us:


## How to use it?

1. Create config.ini and enter to it data like

```
[Telegram]

api_id = 123456
api_hash=123456asdgh-your-hash

phone = +1235556677
username = iamradaken

#you can add comment with hash symbol
```

_You probably need to create telegram client. You can do this in [Telegram API Devtools](htttps://my.telegram.org)_

2. Install reqs w/ command

```
pip -r install requirements.txt
```
3. Download and install MongoDB. _As default script configured on localhost server with default port_

4. Open MongoDB Compass for monitoring stuff
5. Enter your channels in `channels[]` array in script
6. `python main.py`
7. Enjoy in MondoDB Compass

## Fork it and try by yourself!
- [ ] Rewrite code to async telethon lib
- [ ] --inline-args parser (e.g.: `python main.py --channels 'supercrypto' 'hypersignals'`)
- [ ] junk and duplicate cleaner (I think this should be CRON job)
- [ ] Parse more data, like entry points and add chatid to stream
- [ ] Make protection from 420 FloodWaitError
- [ ] Make multiaccount and proxy (for fault tolerance)
- [ ] Replace config.ini to .env
