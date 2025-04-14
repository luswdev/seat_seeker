#!./venv/bin/python3

import logging
import asyncio

from helper import ticketplus, dbus_service

g_configs = []
g_interval = 10

def add_config_cb(obj, config, tag, channel, header):
    global g_configs
    logging.info(f'adding config: {config}, tag: {tag}, channel: {channel}, header: {header}')

    g_configs.append({
        'config': config,
        'tag': tag,
        'channel': channel,
        'header': header,
        'seeker': None,
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
    service.connect('set-interval', set_interval_cb)
    return service

async def main():
    logging.basicConfig(
        format='%(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

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
                seeker = ticketplus.tickets(config=config['config'], channel=config['channel'])
                await seeker.fetchEvent()
                if config['header']:
                    await seeker.tgbot.send(
                        seeker.channel,
                        image=seeker.cover,
                        context=f'start seek seat for event: \n[{seeker.event_name_escape}]({seeker.ticket_url})\n'
                    )

                config['seeker'] = seeker

            await config['seeker'].fetchArea()

        await asyncio.sleep(g_interval)

if __name__ == '__main__':
    asyncio.run(main())
