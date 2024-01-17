#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Clayton Smith.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from gnuradio import gr
import time
import pmt
import pcapng


class pdu_to_pcapng(gr.sync_block):
    """Write PDUs to PcapNG file"""

    def __init__(self, filename="gotenna.pcapng", append=True):
        gr.sync_block.__init__(
            self,
            name="pdu_to_pcapng",
            in_sig=None,
            out_sig=None
        )
        self.message_port_register_in(pmt.intern("pdu"))
        self.set_msg_handler(pmt.intern("pdu"), self.handle_msg)

        self.shb = pcapng.blocks.SectionHeader(
            options={
                "shb_userappl": "gr-tenna",
            }
        )
        idb = self.shb.new_member(
            pcapng.blocks.InterfaceDescription,
            link_type=147,
            options={
                "if_description": "Gotenna receiver",
            },
        )
        self.file = open(filename, "ab" if append else "wb")
        self.writer = pcapng.FileWriter(self.file, self.shb)

    def handle_msg(self, msg):
        metadata = pmt.car(msg)
        packet = bytes(pmt.u8vector_elements(pmt.cdr(msg)))

        spb = self.shb.new_member(pcapng.blocks.EnhancedPacket)
        spb.packet_data = packet

        if pmt.dict_has_key(metadata, pmt.intern("system_time")):
            system_time = pmt.to_double(pmt.dict_ref(metadata, pmt.intern("system_time"), pmt.PMT_NIL))
        else:
            system_time = time.time()

        pcap_time = int(system_time * 1000000)
        spb.timestamp_high = pcap_time >> 32
        spb.timestamp_low = pcap_time & 0xffffffff

        self.writer.write_block(spb)
        self.file.flush()
