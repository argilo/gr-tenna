#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Gotenna Rx
# Generated: Wed Sep 19 15:18:09 2018
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import gotenna_sink
import math
import time


class gotenna_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gotenna Rx")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000000
        self.fsk_deviation_hz = fsk_deviation_hz = 12500
        self.chan_spacing = chan_spacing = 500000
        self.baud_rate = baud_rate = 24000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "recv_frame_size=8192,num_recv_frames=128")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(915000000, 0)
        self.uhd_usrp_source_0.set_gain(25, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=4,
                taps=None,
                fractional_bw=None,
        )
        self.gotenna_sink = gotenna_sink.blk()
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(digital.TED_DANDREA_AND_MENGALI_GEN_MSK, float(chan_spacing) / baud_rate / 4, 0.05, 1.5, 1.0, 0.001 * float(chan_spacing) / baud_rate / 4, 1, digital.constellation_bpsk().base(), digital.IR_MMSE_8TAP, 128, ([]))
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, samp_rate / chan_spacing)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(chan_spacing/(2*math.pi*fsk_deviation_hz))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.gotenna_sink, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_keep_one_in_n_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate / self.chan_spacing)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz
        self.analog_quadrature_demod_cf_0.set_gain(self.chan_spacing/(2*math.pi*self.fsk_deviation_hz))

    def get_chan_spacing(self):
        return self.chan_spacing

    def set_chan_spacing(self, chan_spacing):
        self.chan_spacing = chan_spacing
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate / self.chan_spacing)
        self.analog_quadrature_demod_cf_0.set_gain(self.chan_spacing/(2*math.pi*self.fsk_deviation_hz))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate


def main(top_block_cls=gotenna_rx, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
