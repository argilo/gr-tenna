#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Pro Tx Usrp
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
from gnuradio import uhd
import time
import gotenna_packet
import math




class gotenna_pro_tx_usrp(gr.top_block):

    def __init__(self, baud_rate=9600, callsign='VE3IRR', counter_num=0, frequency=450000000, message='Hello world!', message_type='BROADCAST', publickey_data='base64key', recipient_gid=1234567891, sender_gid=1234567890):
        gr.top_block.__init__(self, "Gotenna Pro Tx Usrp", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.baud_rate = baud_rate
        self.callsign = callsign
        self.counter_num = counter_num
        self.frequency = frequency
        self.message = message
        self.message_type = message_type
        self.publickey_data = publickey_data
        self.recipient_gid = recipient_gid
        self.sender_gid = sender_gid

        ##################################################
        # Variables
        ##################################################
        self.samp_per_sym = samp_per_sym = 4
        self.offset = offset = 250000
        self.interp = interp = 480000 // baud_rate
        self.taps = taps = firdes.gaussian(1.0, samp_per_sym, 0.5, 64)
        self.samp_rate = samp_rate = baud_rate * samp_per_sym * interp
        self.packets = packets = gotenna_packet.encode_pro_broadcast_packets(message_type, counter_num, sender_gid, recipient_gid, callsign, message, publickey_data)
        self.fsk_deviation_hz = fsk_deviation_hz = {2400: 400, 4800: 750, 9600: 1100}[baud_rate]
        self.data_chan = data_chan = 2
        self.control_chan = control_chan = 2
        self.center_freq = center_freq = frequency - offset

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(70, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=interp,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_fff(1, taps)
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_map_bb_0 = digital.map_bb([-3, -1, 3, 1, 0])
        self.blocks_vector_source_x_2 = blocks.vector_source_f([offset], True, 1, [])
        self.blocks_vector_source_x_1 = blocks.vector_source_c([1], True, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b(gotenna_packet.pro_gfsk_symbols(packets), False, 1, [])
        self.blocks_vco_c_1 = blocks.vco_c((baud_rate * samp_per_sym), (2 * math.pi * fsk_deviation_hz), 1.0)
        self.blocks_vco_c_0 = blocks.vco_c(samp_rate, (2*math.pi), 0.9)
        self.blocks_repeat_2 = blocks.repeat(gr.sizeof_float*1, samp_per_sym)
        self.blocks_repeat_1 = blocks.repeat(gr.sizeof_float*1, (8 * samp_per_sym * interp))
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*1, (8 * samp_per_sym))
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_repeat_2, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_repeat_1, 0), (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_repeat_2, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.blocks_vco_c_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_vco_c_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.digital_map_bb_0, 0))
        self.connect((self.blocks_vector_source_x_1, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_vector_source_x_2, 0), (self.blocks_repeat_1, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.blocks_vco_c_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_1, 0))


    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_fsk_deviation_hz({2400: 400, 4800: 750, 9600: 1100}[self.baud_rate])
        self.set_interp(480000 // self.baud_rate)
        self.set_samp_rate(self.baud_rate * self.samp_per_sym * self.interp)

    def get_callsign(self):
        return self.callsign

    def set_callsign(self, callsign):
        self.callsign = callsign
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_counter_num(self):
        return self.counter_num

    def set_counter_num(self, counter_num):
        self.counter_num = counter_num
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.set_center_freq(self.frequency - self.offset)

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_message_type(self):
        return self.message_type

    def set_message_type(self, message_type):
        self.message_type = message_type
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_publickey_data(self):
        return self.publickey_data

    def set_publickey_data(self, publickey_data):
        self.publickey_data = publickey_data
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_recipient_gid(self):
        return self.recipient_gid

    def set_recipient_gid(self, recipient_gid):
        self.recipient_gid = recipient_gid
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_sender_gid(self):
        return self.sender_gid

    def set_sender_gid(self, sender_gid):
        self.sender_gid = sender_gid
        self.set_packets(gotenna_packet.encode_pro_broadcast_packets(self.message_type, self.counter_num, self.sender_gid, self.recipient_gid, self.callsign, self.message, self.publickey_data))

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_samp_rate(self.baud_rate * self.samp_per_sym * self.interp)
        self.set_taps(firdes.gaussian(1.0, self.samp_per_sym, 0.5, 64))
        self.blocks_repeat_0.set_interpolation((8 * self.samp_per_sym))
        self.blocks_repeat_1.set_interpolation((8 * self.samp_per_sym * self.interp))
        self.blocks_repeat_2.set_interpolation(self.samp_per_sym)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.set_center_freq(self.frequency - self.offset)
        self.blocks_vector_source_x_2.set_data([self.offset], [])

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.set_samp_rate(self.baud_rate * self.samp_per_sym * self.interp)
        self.blocks_repeat_1.set_interpolation((8 * self.samp_per_sym * self.interp))

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.interp_fir_filter_xxx_0.set_taps(self.taps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

    def get_packets(self):
        return self.packets

    def set_packets(self, packets):
        self.packets = packets
        self.blocks_vector_source_x_0.set_data(gotenna_packet.pro_gfsk_symbols(self.packets), [])

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz

    def get_data_chan(self):
        return self.data_chan

    def set_data_chan(self, data_chan):
        self.data_chan = data_chan

    def get_control_chan(self):
        return self.control_chan

    def set_control_chan(self, control_chan):
        self.control_chan = control_chan

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--baud-rate", dest="baud_rate", type=intx, default=9600,
        help="Set Baud rate [default=%(default)r]")
    parser.add_argument(
        "--callsign", dest="callsign", type=str, default='VE3IRR',
        help="Set Sender callsign [default=%(default)r]")
    parser.add_argument(
        "--counter-num", dest="counter_num", type=intx, default=0,
        help="Set Counter [default=%(default)r]")
    parser.add_argument(
        "--frequency", dest="frequency", type=eng_float, default=eng_notation.num_to_str(float(450000000)),
        help="Set Frequency [default=%(default)r]")
    parser.add_argument(
        "--message", dest="message", type=str, default='Hello world!',
        help="Set Message [default=%(default)r]")
    parser.add_argument(
        "--message-type", dest="message_type", type=str, default='BROADCAST',
        help="Set type [default=%(default)r]")
    parser.add_argument(
        "--publickey-data", dest="publickey_data", type=str, default='base64key',
        help="Set Sender Public Key [default=%(default)r]")
    parser.add_argument(
        "--recipient-gid", dest="recipient_gid", type=intx, default=1234567891,
        help="Set Recipient GID [default=%(default)r]")
    parser.add_argument(
        "--sender-gid", dest="sender_gid", type=intx, default=1234567890,
        help="Set Sender GID [default=%(default)r]")
    return parser


def main(top_block_cls=gotenna_pro_tx_usrp, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(baud_rate=options.baud_rate, callsign=options.callsign, counter_num=options.counter_num, frequency=options.frequency, message=options.message, message_type=options.message_type, publickey_data=options.publickey_data, recipient_gid=options.recipient_gid, sender_gid=options.sender_gid)

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
