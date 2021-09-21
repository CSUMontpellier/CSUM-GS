#!/usr/bin/python3

from datetime import datetime
import struct
from time import sleep
import zmq
import sys

print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "Starting")

PUB_IP_DEFAULT = '127.0.0.1'
PUB_PORT_DEFAULT = '5500'


try:
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://{}:{}".format(PUB_IP_DEFAULT,PUB_PORT_DEFAULT))
    print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "SUCCESS: Publishing to address {} port {}".format(PUB_IP_DEFAULT, PUB_PORT_DEFAULT))
except Exception as e:
    print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "WARNING: Could not connect to address {} port {}. Not publishing".format(PUB_IP_DEFAULT, PUB_PORT_DEFAULT))
    print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "Exception: ", e)
    sys.exit()

frame = [0x55, 0x55, 0x11, 0x11, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33]

while True:
    print("\033[0;36m["+datetime.utcnow().isoformat()+"+UTC]","["+sys.argv[0]+"]\033[0m", "Sending {} bytes of Data {} ".format(len(frame), frame))
    publisher.send(bytes(frame))
    sleep(1)