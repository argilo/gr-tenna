#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Gotenna Pro Rx Hackrf
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
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
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
from gnuradio import tenna
import sip



class gotenna_pro_rx_hackrf(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Gotenna Pro Rx Hackrf", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Gotenna Pro Rx Hackrf")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "gotenna_pro_rx_hackrf")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.baud_rate = baud_rate = 9600
        self.offset = offset = 250000
        self.lp_taps = lp_taps = firdes.low_pass(1.0, samp_rate, 25000 * (baud_rate / 9600),15000 * (baud_rate / 9600), window.WIN_HAMMING, 6.76)
        self.fsk_deviation_hz = fsk_deviation_hz = {2400: 800, 4800: 1500, 9600: 2200}[baud_rate]
        self.fsk_constellation = fsk_constellation = digital.constellation_calcdist([-1.5, -0.5, +1.5, +0.5], [0, 1, 2, 3],
        2, 1, digital.constellation.NO_NORMALIZATION).base()
        self.fsk_constellation.set_npwr(1.0)
        self.decim = decim = round(16 * (9600 / baud_rate))
        self.dc_block_symbols = dc_block_symbols = 128
        self.center_freq = center_freq = int(451.003e6)

        ##################################################
        # Blocks
        ##################################################

        self.tenna_pdu_to_pcapng_0 = tenna.pdu_to_pcapng('gotenna_pro.pcapng', True)
        self.tenna_gotenna_decoder_0 = tenna.gotenna_decoder(1)
        self.soapy_hackrf_source_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_hackrf_source_0.set_sample_rate(0, samp_rate)
        self.soapy_hackrf_source_0.set_bandwidth(0, 0)
        self.soapy_hackrf_source_0.set_frequency(0, (center_freq - offset))
        self.soapy_hackrf_source_0.set_gain(0, 'AMP', False)
        self.soapy_hackrf_source_0.set_gain(0, 'LNA', min(max(16, 0.0), 40.0))
        self.soapy_hackrf_source_0.set_gain(0, 'VGA', min(max(16, 0.0), 62.0))
        self.qtgui_waterfall_sink_x_1_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_FLATTOP, #wintype
            center_freq, #fc
            (samp_rate / decim), #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_1_0.set_update_time(0.01)
        self.qtgui_waterfall_sink_x_1_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_1_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_1_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_1_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_1_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_1_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_1_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_1_0_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            (samp_rate / decim), #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.01)
        self.qtgui_freq_sink_x_1.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(False)
        self.qtgui_freq_sink_x_1.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_win)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decim, lp_taps, offset, samp_rate)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_GARDNER,
            ((samp_rate / decim) / baud_rate),
            0.045,
            1.0,
            1.0,
            (0.001 * (samp_rate / decim) / baud_rate),
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(fsk_constellation)
        self.dc_blocker_xx_0 = filter.dc_blocker_ff((round(dc_block_symbols * ((samp_rate / decim) / baud_rate))), True)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(2, 1, "", False, gr.GR_MSB_FIRST)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(((samp_rate / decim) / (2 * math.pi * fsk_deviation_hz)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.tenna_gotenna_decoder_0, 'pdu'), (self.tenna_pdu_to_pcapng_0, 'pdu'))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.tenna_gotenna_decoder_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_freq_sink_x_1, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_waterfall_sink_x_1_0, 0))
        self.connect((self.soapy_hackrf_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "gotenna_pro_rx_hackrf")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lp_taps(firdes.low_pass(1.0, self.samp_rate, 25000 * (self.baud_rate / 9600), 15000 * (self.baud_rate / 9600), window.WIN_HAMMING, 6.76))
        self.analog_quadrature_demod_cf_0.set_gain(((self.samp_rate / self.decim) / (2 * math.pi * self.fsk_deviation_hz)))
        self.digital_symbol_sync_xx_0.set_sps(((self.samp_rate / self.decim) / self.baud_rate))
        self.qtgui_freq_sink_x_1.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))
        self.qtgui_waterfall_sink_x_1_0.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))
        self.soapy_hackrf_source_0.set_sample_rate(0, self.samp_rate)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_decim(round(16 * (9600 / self.baud_rate)))
        self.set_fsk_deviation_hz({2400: 800, 4800: 1500, 9600: 2200}[self.baud_rate])
        self.set_lp_taps(firdes.low_pass(1.0, self.samp_rate, 25000 * (self.baud_rate / 9600), 15000 * (self.baud_rate / 9600), window.WIN_HAMMING, 6.76))
        self.digital_symbol_sync_xx_0.set_sps(((self.samp_rate / self.decim) / self.baud_rate))

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
        self.analog_quadrature_demod_cf_0.set_gain(((self.samp_rate / self.decim) / (2 * math.pi * self.fsk_deviation_hz)))

    def get_fsk_constellation(self):
        return self.fsk_constellation

    def set_fsk_constellation(self, fsk_constellation):
        self.fsk_constellation = fsk_constellation
        self.digital_constellation_decoder_cb_0.set_constellation(self.fsk_constellation)

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.analog_quadrature_demod_cf_0.set_gain(((self.samp_rate / self.decim) / (2 * math.pi * self.fsk_deviation_hz)))
        self.digital_symbol_sync_xx_0.set_sps(((self.samp_rate / self.decim) / self.baud_rate))
        self.qtgui_freq_sink_x_1.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))
        self.qtgui_waterfall_sink_x_1_0.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))

    def get_dc_block_symbols(self):
        return self.dc_block_symbols

    def set_dc_block_symbols(self, dc_block_symbols):
        self.dc_block_symbols = dc_block_symbols

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.qtgui_freq_sink_x_1.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))
        self.qtgui_waterfall_sink_x_1_0.set_frequency_range(self.center_freq, (self.samp_rate / self.decim))
        self.soapy_hackrf_source_0.set_frequency(0, (self.center_freq - self.offset))




def main(top_block_cls=gotenna_pro_rx_hackrf, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
