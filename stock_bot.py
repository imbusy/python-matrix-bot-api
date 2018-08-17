"""
A bot that queries stock data.

Test it out by adding it to a group chat and saying "!aapl" for AAPL
stock info.
"""

import json
import os
import random
import sys
import time
import urllib.request

from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler

for var in ['USERNAME', 'PASSWORD', 'SERVER']:
  if var not in os.environ:
    print('{} environment variable is missing.'.format(var))
    sys.exit(1)

# Global variables
USERNAME = os.environ['USERNAME']  # Bot's username
PASSWORD = os.environ['PASSWORD']  # Bot's password
SERVER = os.environ['SERVER']  # Matrix server URL


def tick_callback(room, event):
    tick = event['content']['body'].lstrip('!').upper()
    if len(tick) > 10:
        room.send_text('Per ilgas pavadinimas gal? Astibusk.')
        return

    try:
        response = urllib.request.urlopen(
            'https://api.iextrading.com/1.0/stock/{}/batch?types=quote'.format(tick)
        ).read()
    except:
        room.send_text('Nepavyko gauti duomenų iš serviso.')
        return

    try:
        quote = json.loads(response.decode('utf-8'))['quote']
    except:
        room.send_text('Servisas atsiuntė kažkokią nesąmonę.')
        return

    text_format = """## {symbol} ({companyName})
  - paskutinė kaina: {latestPrice}
  - daily change: {change} ({changePercent:+.2f}%)
  - extended change: {extendedChange} ({extendedChangePercent:+.2f}%)"""

    html_format = """<h2>{symbol} ({companyName})</h2>
<ul>
  <li> paskutinė kaina: {latestPrice}</li>
  <li> daily change: {change} ({changePercent:+.2f}%)</li>
  <li> extended change: {extendedChange} ({extendedChangePercent:+.2f}%)
</ul>"""

    try:    
        quote['changePercent'] *= 100
        quote['extendedChangePercent'] *= 100

        room.send_html(
            html_format.format(**quote), body=text_format.format(**quote))
    except Exception as e:
        room.send_text('Paslydau :(\n\n' + e.__class__.__name__ + ': ' + str(e))
        print(json.dumps(quote, indent=2))

def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)

    # Add a regex handler waiting for the ! symbol at the beginning of the
    # message.
    tick_handler = MRegexHandler("^!.*", tick_callback)
    bot.add_handler(tick_handler)

    # Start polling.
    bot.start_polling()

    # Infinite sleep while the bot runs in other threads.
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()

