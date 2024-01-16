#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Tx Hackrf
# GNU Radio version: 3.10.9.2

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
import gotenna_tx_hackrf_gotenna_packet as gotenna_packet  # embedded python module
import math




class gotenna_tx_hackrf(gr.top_block):

    def __init__(self, app_id=0x3fff, initials='VE3IRR', message='Hello world!', sender_gid=1234567890):
        gr.top_block.__init__(self, "Gotenna Tx Hackrf", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.app_id = app_id
        self.initials = initials
        self.message = message
        self.sender_gid = sender_gid

        ##################################################
        # Variables
        ##################################################
        self.data_chan = data_chan = 2
        self.silence_time = silence_time = 5000
        self.samp_rate = samp_rate = 2000000
        self.samp_per_sym = samp_per_sym = 4
        self.packets = packets = gotenna_packet.encode_shout_packets(data_chan, app_id, sender_gid, initials, message)
        self.interp = interp = 20
        self.control_chan = control_chan = 2
        self.center_freq = center_freq = 926250000
        self.baud_rate = baud_rate = 24000

        ##################################################
        # Blocks
        ##################################################

        self.soapy_hackrf_sink_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_sink_0 = soapy.sink(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_hackrf_sink_0.set_sample_rate(0, samp_rate)
        self.soapy_hackrf_sink_0.set_bandwidth(0, 0)
        self.soapy_hackrf_sink_0.set_frequency(0, center_freq)
        self.soapy_hackrf_sink_0.set_gain(0, 'AMP', False)
        self.soapy_hackrf_sink_0.set_gain(0, 'VGA', min(max(24, 0.0), 47.0))
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=samp_rate,
                decimation=(baud_rate * samp_per_sym * interp),
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=interp,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
            samples_per_symbol=samp_per_sym,
            sensitivity=1.0,
            bt=0.5,
            verbose=False,
            log=False,
            do_unpack=True)
        self.blocks_vector_source_x_2 = blocks.vector_source_f([0]*silence_time+gotenna_packet.vco(center_freq, control_chan, data_chan, packets)+[0]*silence_time, False, 1, [])
        self.blocks_vector_source_x_1 = blocks.vector_source_c([0]*silence_time+gotenna_packet.envelope(packets)+[0]*silence_time, False, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b([0]*silence_time+gotenna_packet.gfsk_bytes(packets)+[0]*silence_time, False, 1, [])
        self.blocks_vco_c_0 = blocks.vco_c((baud_rate * samp_per_sym * interp), (2*math.pi), 0.9)
        self.blocks_repeat_1 = blocks.repeat(gr.sizeof_float*1, (8 * samp_per_sym * interp))
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, (8 * samp_per_sym))
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_repeat_1, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_vector_source_x_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.blocks_vector_source_x_1, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_vector_source_x_2, 0), (self.blocks_repeat_1, 0))
        self.connect((self.digital_gfsk_mod_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.soapy_hackrf_sink_0, 0))


    def get_app_id(self):
        return self.app_id

    def set_app_id(self, app_id):
        self.app_id = app_id
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.app_id, self.sender_gid, self.initials, self.message))

    def get_initials(self):
        return self.initials

    def set_initials(self, initials):
        self.initials = initials
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.app_id, self.sender_gid, self.initials, self.message))

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.app_id, self.sender_gid, self.initials, self.message))

    def get_sender_gid(self):
        return self.sender_gid

    def set_sender_gid(self, sender_gid):
        self.sender_gid = sender_gid
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.app_id, self.sender_gid, self.initials, self.message))

    def get_data_chan(self):
        return self.data_chan

    def set_data_chan(self, data_chan):
        self.data_chan = data_chan
        self.set_packets(gotenna_packet.encode_shout_packets(self.data_chan, self.app_id, self.sender_gid, self.initials, self.message))
        self.blocks_vector_source_x_2.set_data([0]*self.silence_time+gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_silence_time(self):
        return self.silence_time

    def set_silence_time(self, silence_time):
        self.silence_time = silence_time
        self.blocks_vector_source_x_0.set_data([0]*self.silence_time+gotenna_packet.gfsk_bytes(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_1.set_data([0]*self.silence_time+gotenna_packet.envelope(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_2.set_data([0]*self.silence_time+gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.soapy_hackrf_sink_0.set_sample_rate(0, self.samp_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.blocks_repeat_0.set_interpolation((8 * self.samp_per_sym))
        self.blocks_repeat_1.set_interpolation((8 * self.samp_per_sym * self.interp))

    def get_packets(self):
        return self.packets

    def set_packets(self, packets):
        self.packets = packets
        self.blocks_vector_source_x_0.set_data([0]*self.silence_time+gotenna_packet.gfsk_bytes(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_1.set_data([0]*self.silence_time+gotenna_packet.envelope(self.packets)+[0]*self.silence_time, [])
        self.blocks_vector_source_x_2.set_data([0]*self.silence_time+gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.blocks_repeat_1.set_interpolation((8 * self.samp_per_sym * self.interp))

    def get_control_chan(self):
        return self.control_chan

    def set_control_chan(self, control_chan):
        self.control_chan = control_chan
        self.blocks_vector_source_x_2.set_data([0]*self.silence_time+gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.blocks_vector_source_x_2.set_data([0]*self.silence_time+gotenna_packet.vco(self.center_freq, self.control_chan, self.data_chan, self.packets)+[0]*self.silence_time, [])
        self.soapy_hackrf_sink_0.set_frequency(0, self.center_freq)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--app-id", dest="app_id", type=intx, default=0x3fff,
        help="Set App ID [default=%(default)r]")
    parser.add_argument(
        "--initials", dest="initials", type=str, default='VE3IRR',
        help="Set Sender initials [default=%(default)r]")
    parser.add_argument(
        "--message", dest="message", type=str, default='Hello world!',
        help="Set Message [default=%(default)r]")
    parser.add_argument(
        "--sender-gid", dest="sender_gid", type=intx, default=1234567890,
        help="Set Sender GID [default=%(default)r]")
    return parser


def main(top_block_cls=gotenna_tx_hackrf, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(app_id=options.app_id, initials=options.initials, message=options.message, sender_gid=options.sender_gid)

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
