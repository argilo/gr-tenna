#!/usr/bin/env python3
#
# Copyright 2018 Clayton Smith (argilo@gmail.com)
#
# This file is part of gr-tenna.
#
# gr-tenna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gr-tenna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gr-tenna.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
from gotenna_rx_usrp import gotenna_rx_usrp
from gotenna_tx_usrp import gotenna_tx_usrp
from gotenna_rx_hackrf import gotenna_rx_hackrf
from gotenna_tx_hackrf import gotenna_tx_hackrf

parser = argparse.ArgumentParser(description='Receive or transmit goTenna messages.')
parser.add_argument('--device', choices=['usrp', 'hackrf'], default='usrp')
subparsers = parser.add_subparsers()
parser_rx = subparsers.add_parser('rx', help='receive messages')
parser_tx = subparsers.add_parser('tx', help='transmit a message')
parser_tx.add_argument('type', choices=['shout'], help='message type')
parser_tx.add_argument('gid', type=int, help='sender GID')
parser_tx.add_argument('initials')
parser_tx.add_argument('message')

args = parser.parse_args()
print(args)

if hasattr(args, 'message'):
    if args.device == 'usrp':
        tb = gotenna_tx_usrp()
    elif args.device == 'hackrf':
        tb = gotenna_tx_hackrf()
    tb.set_sender_gid(args.gid)
    tb.set_initials(args.initials)
    tb.set_message(args.message)
    tb.start()
    tb.wait()
else:
    if args.device == 'usrp':
        tb = gotenna_rx_usrp()
    elif args.device == 'hackrf':
        tb = gotenna_rx_hackrf()
    tb.start()
    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()
