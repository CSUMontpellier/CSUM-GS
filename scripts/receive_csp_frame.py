#!/usr/bin/python3

from datetime import datetime
import sys
import zmq
import argparse
from crccheck.crc import CrcX25

print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[receive_csp_frame]\033[0m", "Starting")

SUB_IP_DEFAULT = '127.0.0.1'
SUB_PORT = 5600

ASM = [0x5A, 0x0F, 0xBE, 0x66]

# RX state machine states
RX_STATE_INIT = 1
RX_STATE_WAIT_ASM_0 = 2
RX_STATE_WAIT_ASM_1 = 3
RX_STATE_WAIT_ASM_2 = 4
RX_STATE_WAIT_ASM_3 = 5
RX_STATE_RECEIVE_LENGTH = 6
RX_STATE_READ_DATA = 7
RX_STATE_DELIVER_PACKET = 8


VERBOSE = False


class Receiver():
    '''
        Class for receiving bytes and parsing the data for CSP packets.
        The bytes are received after subscribing to a ZMQ topic. The packets 
        with valid CRC are published to another topic.

    '''
    def __init__(self):
        self.verbose = VERBOSE
        self.taskState = RX_STATE_INIT
        self.frameIndex = 0
        self.rx_buffer = b''
        self.bit_counter = 0
        self.byte = 0 
        self._bit_slide_counter = 8
        self._byte_counter = 0
        self._tcp_byte = 0
        self._in_buffer = b''

        self.sub_ip = SUB_IP_DEFAULT
        self.sub_port = SUB_PORT

        self.connect_to_server()
            
    def run(self):
        while(1):
            if self.receive_task(300):
                if len(self.rx_buffer):
                    print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]" + " [receive_csp_frame]\033[0m" + '\n\nReceived Packet of size ', int(self.packet_received_length), '!',  "\033[0m")
                    if self.is_ax5043_crc_valid(self.rx_buffer) == True: 
                        print("The CRC is valid !")
                    else:
                        print("Invalid CRC !!")
                    for b in self.rx_buffer:
                        print(hex(b), end=' ')
                    print()
                    sys.stdout.flush()
                    self.rx_buffer = b''

    def receive_bit(self):
        if self._bit_slide_counter == 8:
            self._bit_slide_counter = 0
            if self._byte_counter >= len(self._in_buffer):
                self._in_buffer = self.subscriber.recv()
                self._byte_counter = 0

            self._tcp_byte = self._in_buffer[self._byte_counter]
            self._byte_counter += 1
        
        out_bit = 0
        if self._tcp_byte & (0x80 >> self._bit_slide_counter): out_bit = 1

        self._bit_slide_counter += 1


        return out_bit

    def connect_to_server(self):
        try:
            context = zmq.Context()
            self.subscriber = context.socket(zmq.SUB)
            self.subscriber.connect("tcp://{}:{}".format(self.sub_ip, self.sub_port))
            self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[receive_csp_frame]\033[0m", "SUCCESS: Subscribed to address {} port {}".format(self.sub_ip, self.sub_port))
        except:
            print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","[receive_csp_frame]\033[0m", "ERROR: Could not connect to address {} port {}".format(self.sub_ip, self.sub_port))

    def receive_task(self, max_length):
        if self.taskState == RX_STATE_INIT: # Init all variable for a new RX Process
            self.byte = 0x00
            self.bit_counter = 0
            self.frameIndex = 0
            self.rx_buffer = b''
            self.taskState = RX_STATE_WAIT_ASM_0
            return 0

        elif self.taskState == RX_STATE_WAIT_ASM_0:
            # Monitor bitstream and try to find first byte of ASM
            in_bit = self.receive_bit()
            self.byte = (self.byte >> 1) & 0xFF
            if (in_bit == 0):
                self.byte = self.byte & ~(0x80)
            else:
                self.byte = self.byte | 0x80 

            # Check if byte matches first byte of ASM
            if (self.byte == ASM[0]):
                # If so, go to wait second ASM byte state
                self.taskState = RX_STATE_WAIT_ASM_1
                self.bit_counter = 0;
            return 0

        elif self.taskState == RX_STATE_WAIT_ASM_1:
            # Monitor bitstream and try to find second byte of ASM
            in_bit = self.receive_bit()
            self.byte = (self.byte >> 1) & 0xFF
            if (in_bit == 0):
                self.byte = self.byte & ~(0x80)
            else:
                self.byte = self.byte | 0x80 
            
            # increment the bit counter for this step
            self.bit_counter+=1

            # If a full byte was received...
            if self.bit_counter == 8:
                # Check if byte matches second byte of ASM
                if (self.byte == ASM[1]):
                    # If so, go to wait third ASM byte state
                    self.taskState = RX_STATE_WAIT_ASM_2
                    self.bit_counter = 0
                else:
                    # If not, go back to init state
                    self.taskState = RX_STATE_INIT
            return 0

        elif self.taskState == RX_STATE_WAIT_ASM_2:
            # Monitor bitstream and try to find third byte of ASM
            in_bit = self.receive_bit()
            self.byte = (self.byte >> 1) & 0xFF
            if (in_bit == 0):
                self.byte = self.byte & ~(0x80)
            else:
                self.byte = self.byte | 0x80 

            # increment the bit counter for this step
            self.bit_counter+=1

            # If a full byte was received...
            if self.bit_counter == 8:

                # Check if byte matches third byte of ASM
                if (self.byte == ASM[2]):
                    # If so, go to wait fourth ASM byte state
                    self.taskState = RX_STATE_WAIT_ASM_3
                    self.bit_counter = 0
                else:
                    # If not, go back to init state
                    self.taskState = RX_STATE_INIT

            return 0

        elif self.taskState == RX_STATE_WAIT_ASM_3:
            # Monitor bitstream and try to find fourth byte of ASM
            in_bit = self.receive_bit()
            self.byte = (self.byte >> 1) & 0xFF
            if (in_bit == 0):
                self.byte = self.byte & ~(0x80)
            else:
                self.byte = self.byte | 0x80

            # increment the bit counter for this step
            self.bit_counter+=1

            # If a full byte was received...
            if self.bit_counter == 8:
                # Check if byte matches third byte of ASM
                if (self.byte == ASM[3]):
                    # If so, ASM found! Go to get packet length state
                    self.taskState = RX_STATE_RECEIVE_LENGTH
                    self.bit_counter = 0
                else:
                    # If not, go back to init state
                    self.taskState = RX_STATE_INIT

            return 0

        elif self.taskState == RX_STATE_RECEIVE_LENGTH: # Get length of packet after ASM
            in_bit = self.receive_bit()
            self.bit_counter += 1
            self.byte = (self.byte >> 1) & 0xFF

            if (in_bit):
                self.byte |= 0x80
            else:
                self.byte &= ~(0x80)

            if (self.bit_counter == 8):
                self.bit_counter = 0
                self.packet_received_length = int(self.byte)
                # Check if received packet length is lower than max packet length allowed   
                if (self.packet_received_length < max_length):
                    # Add the radio packet length byte to the buffer
                    self.rx_buffer += bytes([self.byte])
                    self.frameIndex += 1
                    self.byte = 0
                    # Go to receive data state
                    self.taskState = RX_STATE_READ_DATA
                else:
                    self.taskState = RX_STATE_INIT
                    self.frameIndex = 0

            return 0

        elif self.taskState == RX_STATE_READ_DATA: 
            # Get bistream bit after bit until we reach received packet length
            in_bit = self.receive_bit()
            self.bit_counter += 1
            self.byte = (self.byte >> 1) & 0xFF

            if (in_bit):
                self.byte |= 0x80
            else:
                self.byte &= ~(0x80)

            if (self.bit_counter == 8):
                self.bit_counter = 0
                # Check if we reached the end of the packet
                # We look for a 2 bytes CRC that is not counted in RADIO LENGTH.
                if (self.frameIndex <= self.packet_received_length + 2): 
                    self.rx_buffer += bytes([self.byte])
                    self.frameIndex += 1
                    self.byte = 0
                else:
                    # If yes, deliver the packet
                    self.taskState = RX_STATE_DELIVER_PACKET
                    self.frameIndex = 0

            return 0

        elif self.taskState == RX_STATE_DELIVER_PACKET:
            #  Deliver full self.frameIndex and go back to INIT State
            sys.stdout.flush()
            self.taskState = RX_STATE_INIT
            #  reset local variables
            self.byte = 0x00
            self.bit_counter = 0
            #  save value of frame index to be returned
            #  reset self.frameIndex
            self.frameIndex = 0
            return 1

        else:
            self.taskState = RX_STATE_INIT
            return 0

    def is_ax5043_crc_valid(self, rx_radio_packet):
        if (rx_radio_packet == b'') or (rx_radio_packet is None):
            return False

        received_crc = rx_radio_packet[-2:]
        crc = CrcX25.calc(rx_radio_packet[:-2])
        if crc == int.from_bytes(received_crc, byteorder='little', signed=False):
            return True
        else:
            return False

if __name__ == "__main__":

    rx = Receiver()
    rx.run()





