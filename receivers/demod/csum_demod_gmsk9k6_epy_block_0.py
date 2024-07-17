"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    pkt_cntr = 0

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',   # will show up in GRC
            in_sig=None,
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.message_port_register_in(pmt.intern("msgin"))
        self.set_msg_handler(pmt.intern('msgin'), self.msg_handler)

    def msg_handler(self, msg):
        self.pkt_cntr += 1
        print("--------------------------")
        print(bytearray(pmt.to_python(pmt.cdr(msg))).hex(" "))
        # print("Received "+str(self.pkt_cntr)+" packets.")

    def stop(self):
        print("Received "+str(self.pkt_cntr)+" packets.")


