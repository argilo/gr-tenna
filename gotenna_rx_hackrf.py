#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Rx Hackrf
# GNU Radio version: 3.8.0.0-rc2

from gnuradio import analog
import math
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gotenna_sink
import osmosdr
import time

class gotenna_rx_hackrf(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gotenna Rx Hackrf")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 500000
        self.fsk_deviation_hz = fsk_deviation_hz = 12500
        self.chan_spacing = chan_spacing = 500000
        self.baud_rate = baud_rate = 24000

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=4,
                taps=None,
                fractional_bw=None)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(915000000, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_gain(1, 0)
        self.osmosdr_source_0.set_if_gain(16, 0)
        self.osmosdr_source_0.set_bb_gain(1, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(26000000, 0)
        self.gotenna_sink = gotenna_sink.blk()
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_DANDREA_AND_MENGALI_GEN_MSK,
            float(chan_spacing) / baud_rate / 4,
            0.05,
            1.5,
            1.0,
            0.001 * float(chan_spacing) / baud_rate / 4,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(512, True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(chan_spacing/(2*math.pi*fsk_deviation_hz))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.gotenna_sink, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.digital_symbol_sync_xx_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz
        self.analog_quadrature_demod_cf_0.set_gain(self.chan_spacing/(2*math.pi*self.fsk_deviation_hz))

    def get_chan_spacing(self):
        return self.chan_spacing

    def set_chan_spacing(self, chan_spacing):
        self.chan_spacing = chan_spacing
        self.analog_quadrature_demod_cf_0.set_gain(self.chan_spacing/(2*math.pi*self.fsk_deviation_hz))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate



def main(top_block_cls=gotenna_rx_hackrf, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
