#!/usr/bin/python3

from datetime import datetime
import time
import zmq
import sys
import argparse
from crccheck.crc import CrcX25

print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "Starting")

PUB_IP_DEFAULT = '127.0.0.1'
PUB_PORT = 5500
MIN_FLAG_COUNTER = 50

ASM = [0x5A, 0x0F, 0xBE, 0x66]

class Transmitter():

    def __init__(self):
        self.tx_buffer = None
        self._out_byte = 0
        self.frame = []
        self.pub_ip = PUB_IP_DEFAULT
        self.pub_port = PUB_PORT

        self.connect_to_server()

    def run(self):
        while(1):
            self.tx_buffer = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19'
            self.tx_buffer = len(self.tx_buffer).to_bytes(1, 'big') + self.tx_buffer
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
            time.sleep(2)

    def connect_to_server(self):
        try:
            context = zmq.Context()
            self.publisher = context.socket(zmq.PUB)
            self.publisher.bind("tcp://{}:{}".format(self.pub_ip,self.pub_port))
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "SUCCESS: Publishing to address {} port {}".format(self.pub_ip, self.pub_port))
        except Exception as e:
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[send_csp_frame]\033[0m", "WARNING: Could not connect to address {} port {}. Not publishing".format(self.pub_ip, self.pub_port))
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
        while count < 20:
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