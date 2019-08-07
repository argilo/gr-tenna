#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Tx Hackrf
# GNU Radio version: 3.8.0.0-rc2

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gotenna_packet
import math
import osmosdr
import time

class gotenna_tx_hackrf(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gotenna Tx Hackrf")

        ##################################################
        # Variables
        ##################################################
        self.sender_gid = sender_gid = 1234567890
        self.samp_per_sym = samp_per_sym = 4
        self.message = message = "Hello world!"
        self.interp = interp = 20
        self.initials = initials = "VE3IRR"
        self.data_chan = data_chan = 2
        self.silence_time = silence_time = 5000
        self.samp_rate = samp_rate = 24000 * samp_per_sym * interp
        self.packets = packets = gotenna_packet.encode_shout_packets(data_chan, sender_gid, initials, message)
        self.control_chan = control_chan = 2
        self.center_freq = center_freq = 926250000

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=interp,
                decimation=1,
                taps=None,
                fractional_bw=None)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(1, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
            samples_per_symbol=samp_per_sym,
            sensitivity=1.0,
            bt=0.5,
            verbose=False,
            log=False)
        self.blocks_vector_source_x_2 = blocks.vector_source_f(gotenna_packet.vco(center_freq, control_chan, data_chan, packets)+[0]*silence_time, False, 1, [])
        self.blocks_vector_source_x_1 = blocks.vector_source_c(gotenna_packet.envelope(packets)+[0]*silence_time, False, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b(gotenna_packet.gfsk_bytes(packets)+[0]*silence_time, False, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, 2*math.pi, 0.9)
        self.blocks_repeat_1 = blocks.repeat(gr.sizeof_float*1, 8 * samp_per_sym * interp)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, 8 * samp_per_sym)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_repeat_1, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_vector_source_x_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.blocks_vector_source_x_1, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_vector_source_x_2, 0), (self.blocks_repeat_1, 0))
        self.connect((self.digital_gfsk_mod_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_1, 0))

    def get_sender_gid(self):
        return self.sender_gid

    def set_sender_gid(self, sender_gid):
        self.sender_gid = sender_gid
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.sender_gid, self.initials, self.message))

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_samp_rate(24000 * self.samp_per_sym * self.interp)
        self.blocks_repeat_0.set_interpolation(8 * self.samp_per_sym)
        self.blocks_repeat_1.set_interpolation(8 * self.samp_per_sym * self.interp)

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.sender_gid, self.initials, self.message))

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.set_samp_rate(24000 * self.samp_per_sym * self.interp)
        self.blocks_repeat_1.set_interpolation(8 * self.samp_per_sym * self.interp)

    def get_initials(self):
        return self.initials

    def set_initials(self, initials):
        self.initials = initials
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.sender_gid, self.initials, self.message))

    def get_data_chan(self):
        return self.data_chan

    def set_data_chan(self, data_chan):
        self.data_chan = data_chan
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.sender_gid, self.initials, self.message))
        self.blocks_vector_source_x_2.set_data(gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_silence_time(self):
        return self.silence_time

    def set_silence_time(self, silence_time):
        self.silence_time = silence_time
        self.blocks_vector_source_x_0.set_data(gotenna_packet.gfsk_bytes(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_1.set_data(gotenna_packet.envelope(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_2.set_data(gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_packets(self):
        return self.packets

    def set_packets(self, packets):
        self.packets = packets
        self.blocks_vector_source_x_0.set_data(gotenna_packet.gfsk_bytes(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_1.set_data(gotenna_packet.envelope(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_2.set_data(gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_control_chan(self):
        return self.control_chan

    def set_control_chan(self, control_chan):
        self.control_chan = control_chan
        self.blocks_vector_source_x_2.set_data(gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.blocks_vector_source_x_2.set_data(gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])
        self.osmosdr_sink_0.set_center_freq(self.center_freq, 0)



def main(top_block_cls=gotenna_tx_hackrf, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
