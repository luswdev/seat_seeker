import logging
import yaml
import requests

class tickets:
    def __init__(self, config):
        with open(config, 'r') as file:
            config_content = yaml.safe_load(file)
            self.event_url       = config_content.get('api_url').get('event_url')
            self.session_url     = config_content.get('api_url').get('session_url')
            self.area_url        = config_content.get('api_url').get('area_url')
            self.ticket_url      = config_content.get('event').get('url')
            self.event_base_name = config_content.get('event').get('name')

        if self.event_url is None or self.session_url is None or self.area_url is None:
            logging.error('Error: Missing required URLs in the configuration file.')
            exit(1)

        self.event_name = ''
        self.remain_tickets = { }

    def fetch_area(self):
        ret_area = []
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
                    ret_area.append({
                            'area': area,
                            'count': count,
                        })

                logging.info(f'[{self.event_name}] {area}: {count} (remain: {self.remain_tickets.get(area, 0)})')
                self.remain_tickets[area] = count

        except requests.exceptions.RequestException as e:
            logging.error('fetching url failed: ', e)

        return ret_area

    async def fetch_event(self):
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
            logging.error('fetching url failed: ', e)
