#!./venv/bin/python3

import argparse
import datetime
import asyncio

from helper import ticketplus

async def main(channel, config, need_header, interval):
    ticket_seeker = ticketplus.tickets(config=config, channel=channel)
    await ticket_seeker.fetchEvent()

    if need_header:
        await ticket_seeker.tgbot.send(
            ticket_seeker.channel,
            image=ticket_seeker.cover,
            context=f'start seek seat for event: \n[{ticket_seeker.event_name}]({ticket_seeker.ticket_url})\n'
        )

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
    parser.add_argument('-H', '--header',   action='store_true',           help='Send header information.')
    parser.add_argument('-i', '--interval', type=int, default=10,          help='Interval in seconds between checks.')
    parser.add_argument('-C', '--channel',  type=str, default='@qwer_tks', help='Telegram channel to send messages.')
    parser.add_argument('-f', '--file',     type=str, required=True,       help='Path to the configuration file.')
    args = parser.parse_args()
    asyncio.run(main(args.channel, args.file, args.header, args.interval))
