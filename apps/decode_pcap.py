#!/usr/bin/env python3

import argparse
import pcapng
import gotenna_packet

parser = argparse.ArgumentParser(description="Decode Gotenna packets from a PcapNG file.")
parser.add_argument("filename")
args = parser.parse_args()

with open(args.filename, "rb") as f:
    scanner = pcapng.FileScanner(f)
    for block in scanner:
        if isinstance(block, pcapng.blocks.EnhancedPacket):
            packet = block.packet_data
            gotenna_packet.ingest_packet(packet)
