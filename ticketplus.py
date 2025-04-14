#!./venv/bin/python3

import re
import argparse
import datetime
import requests
import asyncio

import bot
import yaml

class tickets:
    def __init__(self, config, channel='@qwer_tks'):
        with open('env.yaml', 'r') as file:
            self.tgbot = bot.bot(yaml.safe_load(file).get('bot').get('token'))

        with open(config, 'r') as file:
            config_content = yaml.safe_load(file)
            self.event_url = config_content.get('api_url').get('event_url')
            self.session_url = config_content.get('api_url').get('session_url')
            self.area_url = config_content.get('api_url').get('area_url')
            self.ticket_url = config_content.get('event').get('url')

        if self.event_url is None or self.session_url is None or self.area_url is None:
            print('Error: Missing required URLs in the configuration file.')
            exit(1)

        self.event_name = ''
        self.channel = channel

        self.remain_tickets = { }

    async def fetchDay(self):
        try:
            response = requests.get(self.area_url)
            response.raise_for_status()
            data = response.json()
            sessions = data.get('result', {}).get('session', [])
            for i, session in enumerate(sessions):
                status = session.get('status')
                date = session.get('saleEnd').split('T')[0]
                print(f'{date}: {status}')
                if status != 'soldout' and status != 'unavailable':
                    await self.tgbot.send(self.channel, f'{date:8}: {status}')

        except requests.exceptions.RequestException as e:
            print('fetching url failed: ', e)

    async def fetchArea(self):
        try:
            response = requests.get(self.area_url)
            response.raise_for_status()
            data = response.json()
            sessions = data.get('result', {}).get('ticketArea', [])

            for i, session in enumerate(sessions):
                count = session.get('count')
                if type(count) != int:
                    count = 0

                area = session.get('ticketAreaName')
                if count > 0 and self.remain_tickets.get(area, 0) != count:
                    evt_name = self.escape_markdown(self.event_name)
                    await self.tgbot.send(self.channel, f'[{evt_name}]({self.ticket_url})\n**{area}**: {count}')

                print(f'{area}: {count} (remain: {self.remain_tickets.get(area, 0)})')
                self.remain_tickets[area] = count

        except requests.exceptions.RequestException as e:
            print('fetching url failed: ', e)

    async def fetchEvent(self):
        try:
            response = requests.get(self.session_url)
            response.raise_for_status()
            data = response.json()
            self.event_name = data['sessions'][0]['name']

            response = requests.get(self.event_url)
            response.raise_for_status()
            data = response.json()
            self.cover = data['picSmallActiveMain']

        except requests.exceptions.RequestException as e:
            print('fetching url failed: ', e)

    def escape_markdown(self, text):
        escape_chars = r'\_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def main(channel, config, need_header, interval):
    ticket_seeker = tickets(config=config, channel=channel)
    await ticket_seeker.fetchEvent()

    if need_header:
        await ticket_seeker.tgbot.send(ticket_seeker.channel, image=ticket_seeker.cover)
        await ticket_seeker.tgbot.send(ticket_seeker.channel, context=f'start seek seet for event: \n```\n{ticket_seeker.event_name}\n```')

    while True:
        print('\033c', end='')
        print(f'=========================== {ticket_seeker.event_name} ===========================')
        print('')
        await ticket_seeker.fetchArea()
        print('')
        print('last updated: ', datetime.datetime.now())
        print('')

        await asyncio.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seat Seeker script.')
    parser.add_argument('-i', '--interval', type=int, default=10, help='Interval in seconds between checks.')
    parser.add_argument('-H', '--header', type=bool, default=False, help='Send header imformation.')
    parser.add_argument('-C', '--channel', type=str, default='@qwer_tks', help='Telegram channel to send messages.')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the configuration file.')
    args = parser.parse_args()
    asyncio.run(main(args.channel, args.file, args.header, args.interval))
