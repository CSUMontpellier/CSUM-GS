#!/usr/bin/python3

from datetime import datetime
import time
import zmq
import sys
import argparse
from crccheck.crc import CrcX25

print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "Starting")

IP_DEFAULT = '127.0.0.1'
PUB_PORT = 5500
SUB_PORT = 5501
MIN_FLAG_COUNTER = 50

ASM = [0x5A, 0xF0, 0x7D, 0x66]

COMMAND_DEFAULT = b'\x20\x41\xCF\x00\x00\x09\x01\x00\x08\xE0\x13\x00\x04\x02\x02'

class Transmitter():

    def __init__(self):
        self.tx_buffer = None
        self._out_byte = 0
        self.frame = []

        self.connect_to_server()

    def run(self):
        while(1):
            # Listen to ZMQ Port to get CSP PAcket Data
            self.tx_buffer = self.subscriber.recv()
            self.tx_buffer = (len(self.tx_buffer) + 1).to_bytes(1, 'big') + self.tx_buffer
            # Compute CheckSum
            crc = CrcX25.calc(self.tx_buffer)
            crc_b1 = bytes([0x00FF & crc])
            crc_b2 = bytes([(0xFF00 & crc) >> 8])
            self.tx_buffer += crc_b1 + crc_b2

            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "Sending {} bytes of data: {}".format(len(self.tx_buffer), self.tx_buffer.hex()))
            self.transmit_preamble()
            self.transmit_asm()
            self.transmit_packet()
            self.transmit_postamble()
            self.transmit_frame()

    def connect_to_server(self):
        try:
            context = zmq.Context()
            self.subscriber = context.socket(zmq.SUB)
            self.subscriber.connect("tcp://{}:{}".format(IP_DEFAULT, SUB_PORT))
            self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "SUCCESS: Subscribed to address {} port {}".format(IP_DEFAULT, SUB_PORT))
        except:
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "ERROR: Could not connect to address {} port {}".format(IP_DEFAULT, SUB_PORT))
        try:
            context = zmq.Context()
            self.publisher = context.socket(zmq.PUB)
            self.publisher.bind("tcp://{}:{}".format(IP_DEFAULT, PUB_PORT))
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "SUCCESS: Publishing to address {} port {}".format(IP_DEFAULT, PUB_PORT))
        except Exception as e:
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "WARNING: Could not connect to address {} port {}. Not publishing".format(IP_DEFAULT, PUB_PORT))
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "Exception: ", e)

    def transmit_frame(self):
        sent = self.publisher.send(bytes(self.frame))
        self.frame = []
        return sent

    def transmit_byte(self):
        self.frame.append(self._out_byte)
        self._out_byte = 0

    def transmit_preamble(self):
        count = 0
        while count < 100:
            self._out_byte = 0x55
            self.transmit_byte()
            count += 1

    def transmit_postamble(self):
        count = 0
        while count < 32:
            self._out_byte = 0x55
            self.transmit_byte()
            count += 1

    def transmit_asm(self):
       for b in ASM:
            self._out_byte = b
            self.transmit_byte()

    def transmit_packet(self):
       for b in self.tx_buffer:
            self._out_byte = b
            self.transmit_byte()

if __name__ == "__main__":
    tx = Transmitter()
    tx.run()