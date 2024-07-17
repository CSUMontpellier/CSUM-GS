#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: GMSK2k4 demodulator and AX.25 deframer for CSUM satellites.
# Author: CSUM
# Copyright: CSUM
# Description: Demodulates signals from CSUM satellites in GMSK 2400 bps and deframe their AX.25 packets.
# GNU Radio version: 3.10.7.0

from gnuradio import analog
import math
from gnuradio import blocks
import pmt
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
import csum_demod_gmsk2k4_epy_block_0 as epy_block_0  # embedded python block
import satellites.components.deframers


def snipfcn_snippet_0(self):
    print("\033[38;5;70mDemodulator GMSK2k4 started.\033[0m")


def snippets_main_after_start(tb):
    snipfcn_snippet_0(tb)


class csum_demod_gmsk2k4(gr.top_block):

    def __init__(self, iqs_file_path="", throttle_test=153600):
        gr.top_block.__init__(self, "GMSK2k4 demodulator and AX.25 deframer for CSUM satellites.", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.iqs_file_path = iqs_file_path
        self.throttle_test = throttle_test

        ##################################################
        # Variables
        ##################################################
        self.in_samp_rate = in_samp_rate = 153600
        self.demod_samp_rate = demod_samp_rate = 9600
        self.baudrate = baudrate = 2400

        ##################################################
        # Blocks
        ##################################################

        self.satellites_ax25_deframer_0 = satellites.components.deframers.ax25_deframer(g3ruh_scrambler=False, options="")
        self.root_raised_cosine_filter_0 = filter.fir_filter_ccf(
            (in_samp_rate//demod_samp_rate),
            firdes.root_raised_cosine(
                1,
                in_samp_rate,
                (baudrate*1),
                0.707,
                (in_samp_rate//baudrate*8)))
        self.epy_block_0 = epy_block_0.blk()
        self.digital_symbol_sync_xx_1 = digital.symbol_sync_ff(
            digital.TED_ZERO_CROSSING,
            (demod_samp_rate/baudrate),
            0.0455,
            0.27,
            0.17,
            0.01,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, throttle_test, True, 0 if "auto" == "auto" else max( int(float(0.1) * throttle_test) if "auto" == "time" else int(0.1), 1) )
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, iqs_file_path, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.analog_quadrature_demod_cf_0_0 = analog.quadrature_demod_cf((demod_samp_rate/(2*math.pi*baudrate/4)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.satellites_ax25_deframer_0, 'out'), (self.epy_block_0, 'msgin'))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.digital_symbol_sync_xx_1, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.digital_symbol_sync_xx_1, 0), (self.satellites_ax25_deframer_0, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.analog_quadrature_demod_cf_0_0, 0))


    def get_iqs_file_path(self):
        return self.iqs_file_path

    def set_iqs_file_path(self, iqs_file_path):
        self.iqs_file_path = iqs_file_path
        self.blocks_file_source_0.open(self.iqs_file_path, False)

    def get_throttle_test(self):
        return self.throttle_test

    def set_throttle_test(self, throttle_test):
        self.throttle_test = throttle_test
        self.blocks_throttle2_0.set_sample_rate(self.throttle_test)

    def get_in_samp_rate(self):
        return self.in_samp_rate

    def set_in_samp_rate(self, in_samp_rate):
        self.in_samp_rate = in_samp_rate
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.in_samp_rate, (self.baudrate*1), 0.707, (self.in_samp_rate//self.baudrate*8)))

    def get_demod_samp_rate(self):
        return self.demod_samp_rate

    def set_demod_samp_rate(self, demod_samp_rate):
        self.demod_samp_rate = demod_samp_rate
        self.analog_quadrature_demod_cf_0_0.set_gain((self.demod_samp_rate/(2*math.pi*self.baudrate/4)))

    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        self.analog_quadrature_demod_cf_0_0.set_gain((self.demod_samp_rate/(2*math.pi*self.baudrate/4)))
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.in_samp_rate, (self.baudrate*1), 0.707, (self.in_samp_rate//self.baudrate*8)))



def argument_parser():
    description = 'Demodulates signals from CSUM satellites in GMSK 2400 bps and deframe their AX.25 packets.'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-f", "--iqs-file-path", dest="iqs_file_path", type=str, default="",
        help="Set Path to the IQs file. [default=%(default)r]")
    parser.add_argument(
        "-t", "--throttle-test", dest="throttle_test", type=intx, default=153600,
        help="Set Set this value to in_samp_rate to run it in real-time. The higher the throttle, the quicker the file is processed. [default=%(default)r]")
    return parser


def main(top_block_cls=csum_demod_gmsk2k4, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(iqs_file_path=options.iqs_file_path, throttle_test=options.throttle_test)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    snippets_main_after_start(tb)
    tb.wait()


if __name__ == '__main__':
    main()
