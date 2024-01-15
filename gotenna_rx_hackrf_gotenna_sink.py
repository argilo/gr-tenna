import numpy as np
from gnuradio import gr
import gotenna_packet


class blk(gr.sync_block):
    """Decode Gotenna Mesh packets"""

    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="Gotenna decoder",
            in_sig=[np.int8],
            out_sig=None
        )
        self.prefix = "10"*16 + "0010110111010100"
        self.bits = ""

    def work(self, input_items, output_items):
        self.bits += "".join([str(n) for n in input_items[0]])

        idx = self.bits[:-2048].find(self.prefix)
        while idx >= 0:
            self.bits = self.bits[idx + len(self.prefix):]
            length = int(self.bits[0:8], 2)

            packet = bytes(int(self.bits[i*8:i*8 + 8], 2) for i in range(length + 1))
            try:
                print()
                print("Raw bytes: " + packet.hex())

                packet = gotenna_packet.correct_packet(packet)
                print("Corrected: " + packet.hex())
                print()
                gotenna_packet.ingest_packet(packet)
            except Exception as err:
                print("Error decoding packet: " + str(err))

            self.bits = self.bits[(length + 1) * 8:]
            idx = self.bits[:-2048].find(self.prefix)

        self.bits = self.bits[-2048 - len(self.prefix) + 1:]
        return len(input_items[0])
