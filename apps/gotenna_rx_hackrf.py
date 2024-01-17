#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Rx Hackrf
# GNU Radio version: 3.10.9.2

from gnuradio import analog
import math
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
from gnuradio import tenna




class gotenna_rx_hackrf(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gotenna Rx Hackrf", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.chan_spacing = chan_spacing = 500000
        self.samp_rate = samp_rate = chan_spacing * 2
        self.offset = offset = chan_spacing // 2
        self.lp_taps = lp_taps = firdes.low_pass(1.0, chan_spacing, 75000,50000, window.WIN_HAMMING, 6.76)
        self.fsk_deviation_hz = fsk_deviation_hz = 12500
        self.center_freq = center_freq = 915000000
        self.baud_rate = baud_rate = 24000

        ##################################################
        # Blocks
        ##################################################

        self.tenna_pdu_to_pcapng_0 = tenna.pdu_to_pcapng('gotenna.pcapng', True)
        self.tenna_gotenna_decoder_0 = tenna.gotenna_decoder(0)
        self.soapy_hackrf_source_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_hackrf_source_0.set_sample_rate(0, samp_rate)
        self.soapy_hackrf_source_0.set_bandwidth(0, 28000000)
        self.soapy_hackrf_source_0.set_frequency(0, (center_freq - offset))
        self.soapy_hackrf_source_0.set_gain(0, 'AMP', False)
        self.soapy_hackrf_source_0.set_gain(0, 'LNA', min(max(16, 0.0), 40.0))
        self.soapy_hackrf_source_0.set_gain(0, 'VGA', min(max(16, 0.0), 62.0))
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=4,
                taps=[],
                fractional_bw=0)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, lp_taps, offset, chan_spacing)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_MENGALI_AND_DANDREA_GMSK,
            (float(chan_spacing) / baud_rate / 4),
            0.05,
            1.5,
            1.0,
            (0.001 * float(chan_spacing) / baud_rate / 4),
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(1024, False)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, (samp_rate // chan_spacing))
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((chan_spacing/(2*math.pi*fsk_deviation_hz)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.tenna_gotenna_decoder_0, 'pdu'), (self.tenna_pdu_to_pcapng_0, 'pdu'))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.tenna_gotenna_decoder_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.soapy_hackrf_source_0, 0), (self.blocks_keep_one_in_n_0, 0))


    def get_chan_spacing(self):
        return self.chan_spacing

    def set_chan_spacing(self, chan_spacing):
        self.chan_spacing = chan_spacing
        self.set_lp_taps(firdes.low_pass(1.0, self.chan_spacing, 75000, 50000, window.WIN_HAMMING, 6.76))
        self.set_offset(self.chan_spacing // 2)
        self.set_samp_rate(self.chan_spacing * 2)
        self.analog_quadrature_demod_cf_0.set_gain((self.chan_spacing/(2*math.pi*self.fsk_deviation_hz)))
        self.blocks_keep_one_in_n_0.set_n((self.samp_rate // self.chan_spacing))
        self.digital_symbol_sync_xx_0.set_sps((float(self.chan_spacing) / self.baud_rate / 4))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_keep_one_in_n_0.set_n((self.samp_rate // self.chan_spacing))
        self.soapy_hackrf_source_0.set_sample_rate(0, self.samp_rate)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.offset)
        self.soapy_hackrf_source_0.set_frequency(0, (self.center_freq - self.offset))

    def get_lp_taps(self):
        return self.lp_taps

    def set_lp_taps(self, lp_taps):
        self.lp_taps = lp_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.lp_taps)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz
        self.analog_quadrature_demod_cf_0.set_gain((self.chan_spacing/(2*math.pi*self.fsk_deviation_hz)))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.soapy_hackrf_source_0.set_frequency(0, (self.center_freq - self.offset))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.digital_symbol_sync_xx_0.set_sps((float(self.chan_spacing) / self.baud_rate / 4))




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
