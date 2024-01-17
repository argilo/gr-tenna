#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018-2024 Clayton Smith.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import pmt
import gotenna_packet


class gotenna_decoder(gr.sync_block):
    """Decode Gotenna Mesh packets"""

    def __init__(self, mode=0):
        gr.sync_block.__init__(
            self,
            name="gotenna_decoder",
            in_sig=[numpy.int8],
            out_sig=None
        )
        self.message_port_register_out(pmt.intern("pdu"))
        if mode == 0:
            self.prefix = "10"*16 + "0010110111010100"
            self.whitening = [0x00] * 256
        elif mode == 1:
            self.prefix = "1000"*8 + "0010110111010100"
            self.whitening = gotenna_packet.WHITENING
        self.bits = ""
        self.my_log = gr.logger(self.alias())

    def work(self, input_items, output_items):
        self.bits += "".join([str(n) for n in input_items[0]])

        idx = self.bits[:-2048].find(self.prefix)
        while idx >= 0:
            self.bits = self.bits[idx + len(self.prefix):]
            length = int(self.bits[0:8], 2) ^ self.whitening[0]

            packet = bytes(int(self.bits[i*8:i*8 + 8], 2) ^ self.whitening[i] for i in range(length + 1))
            self.my_log.debug(f"Raw packet: {packet.hex()}")
            try:
                packet = gotenna_packet.correct_packet(packet)
                pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(packet), list(packet)))
                self.message_port_pub(pmt.intern("pdu"), pdu)
                gotenna_packet.ingest_packet(packet)
            except Exception as err:
                self.my_log.warn(f"Error decoding packet: {err}")

            self.bits = self.bits[(length + 1) * 8:]
            idx = self.bits[:-2048].find(self.prefix)

        self.bits = self.bits[-2048 - len(self.prefix) + 1:]
        return len(input_items[0])
