import logging
import re
import yaml
import requests

from . import bot

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

            self.event_base_name = config_content.get('event').get('name')

        if self.event_url is None or self.session_url is None or self.area_url is None:
            logging.error('Error: Missing required URLs in the configuration file.')
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
                logging.info(f'[{self.event_name}] {date}: {status}')
                if status != 'soldout' and status != 'unavailable':
                    await self.tgbot.send(self.channel, f'{date:8}: {status}')

        except requests.exceptions.RequestException as e:
            logging.error('fetching url failed: ', e)

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

                area = self.escape_markdown(session.get('ticketAreaName'))
                if count > 0 and self.remain_tickets.get(area, 0) != count:
                    await self.tgbot.send(self.channel, f'[{self.event_name_escape}]({self.ticket_url})\n**{area}**: {count}')

                logging.info(f'[{self.event_name}] {area}: {count} (remain: {self.remain_tickets.get(area, 0)})')
                self.remain_tickets[area] = count

        except requests.exceptions.RequestException as e:
            logging.error('fetching url failed: ', e)

    async def fetchEvent(self):
        try:
            response = requests.get(self.session_url)
            response.raise_for_status()
            data = response.json()
            self.event_name = data['sessions'][0]['name']
            self.event_name_escape = self.escape_markdown(data['sessions'][0]['name'])

            response = requests.get(self.event_url)
            response.raise_for_status()
            data = response.json()
            self.cover = data['picSmallActiveMain']

        except requests.exceptions.RequestException as e:
            logging.error('fetching url failed: ', e)

    def escape_markdown(self, text):
        escape_chars = r'\_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
