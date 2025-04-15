#!./venv/bin/python3

import logging
import asyncio
import re
import yaml

from helper import ticketplus, dbus_service, bot

g_configs  = []
g_interval = 10

def add_config_cb(obj, config, tag, channel, header):
    global g_configs
    logging.info(f'adding config: {config}, tag: {tag}, channel: {channel}, header: {header}')

    g_configs.append({
        'config':  config,
        'tag':     tag,
        'channel': channel,
        'header':  header,
        'seeker':  None,
    })

def del_config_cb(obj, tag):
    global g_configs
    logging.info(f'deleting config: {tag}')

    for config in g_configs:
        if config['tag'] == tag:
            g_configs.remove(config)
            break

def set_interval_cb(obj, interval):
    global g_interval
    logging.info(f'setting interval: {interval}')

    g_interval = interval

def init_dbus_service():
    service = dbus_service.dbus_service()
    service.connect('add-config-signal', add_config_cb)
    service.connect('del-config-signal', del_config_cb)
    service.connect('set-interval',      set_interval_cb)
    return service

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def main():
    logging.basicConfig(
        format = '%(levelname)s - %(message)s',
        level  = logging.INFO,
    )

    with open('env.yaml', 'r') as file:
        tgbot = bot.bot(yaml.safe_load(file).get('bot').get('token'))

    service = init_dbus_service()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, service.start)

    while True:
        if len(g_configs) == 0:
            logging.info('waiting for config...')
            await asyncio.sleep(g_interval)
            continue

        for config in g_configs:
            if config['seeker'] is None:
                config['seeker'] = ticketplus.tickets(config = config['config'])
                await config['seeker'].fetch_event()
                if config['header']:
                    evt_name_escape = escape_markdown(config['seeker'].event_name)
                    await tgbot.send(
                        config['channel'],
                        image   = config['seeker'].cover,
                        context = f'start seek seat for event: \n[{evt_name_escape}]({config["seeker"].ticket_url})\n'
                    )

            ret_area = config['seeker'].fetch_area()
            if len(ret_area) > 0:
                for area in ret_area:
                    area_escape     = escape_markdown(area['area'])
                    evt_name_escape = escape_markdown(config['seeker'].event_name)

                    await tgbot.send(
                        config['channel'],
                        context = f'[{evt_name_escape}]({config["seeker"].ticket_url})\n**{area_escape}**: {area["count"]}'
                    )

        await asyncio.sleep(g_interval)

if __name__ == '__main__':
    asyncio.run(main())
