#!/usr/bin/env python3
#
# Copyright 2018 Clayton Smith (argilo@gmail.com)
#
# This file is part of gr-tenna.
#
# gr-tenna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gr-tenna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gr-tenna.  If not, see <http://www.gnu.org/licenses/>.
#

import binascii
import reedsolo
import struct
import time

CRC16_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]

CONTROL_CHANNELS = [903000000, 915000000, 927000000]

DATA_CHANNELS = [
    923500000, 923000000, 925500000, 926500000, 925000000, 908000000, 911500000, 905500000,
    903500000, 915500000, 909000000, 912000000, 922000000, 921000000, 924000000, 907500000,
    910000000, 912500000, 927500000, 910500000, 913000000, 918500000, 913500000, 914000000,
    902500000, 922500000, 907000000, 920000000, 919000000, 916500000, 919500000, 914500000,
    918000000, 911000000, 917500000, 916000000, 924500000, 909500000, 904500000, 904000000,
    917000000, 921500000, 920500000, 905000000, 908500000, 906500000, 926000000, 906000000
]

ONE_TO_ONE_GID = 0
GROUP_GID = 1
SHOUT_GID = 2
EMERGENCY_GID = 3

TEXT_MESSAGE = "0"
MESH_KEY_EXCHANGE_REQUEST = "14"
MESH_KEY_EXCHANGE_RESPONSE = "15"

ENCRYPTION_INFO = 251

PAYLOAD_SPLIT_LEN = 90
CONTROL_PREAMBLE_LEN = 93
DATA_PREAMBLE_LEN = 10
HOP_TIME_1 = 33
HOP_TIME_2 = 27

public_keys = {
    94011144312926: binascii.unhexlify("035c7706208dddea88cc414a2f81481243d41ad1ac1c5b43763bb54e47a7b9a6f33ad13153a5d5fb0ac0fa12d76fd45b26")
}


def compress_point(x, y):
    return bytes([2 | (y & 1)]) + x.to_bytes(48, byteorder="big")


def uncompress_point(bytes):
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
    a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc
    b = 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef

    x = int.from_bytes(bytes[1:], byteorder="big")
    y_squared = (pow(x, 3, p) + x * a + b) % p
    y = pow(y_squared, (p + 1) // 4, p)
    if (public_key_bytes[0] & 1) != (y & 1):
        y = p - y
    return x, y


def crc16(in_bytes):
    reg = 0x0000
    for b in in_bytes:
        reg = ((reg & 0xff) << 8) ^ CRC16_TABLE[(b ^ (reg >> 8)) & 0xff]
    return reg


def encode_packet(preamble_len, in_bytes):
    length = len(in_bytes) + 2 + 8
    packet = bytearray([length]) + in_bytes
    packet += struct.pack(">H", crc16(packet) ^ 0xabcd)
    rs = reedsolo.RSCodec(8)
    return bytearray([0xaa]*preamble_len + [0x2d, 0xd4]) + rs.encode(packet)


def encode_tlv(type, value):
    return bytearray([type, len(value)]) + value


def encode_encryption_info(encrypted, sender_gid, timestamp, enc_counter, resend_id):
    return struct.pack(">BQIHB", encrypted, sender_gid, timestamp, enc_counter, resend_id)


def encode_control_packet(channel, num_data_packets):
    return encode_packet(CONTROL_PREAMBLE_LEN, bytearray([9, channel, num_data_packets, 1, 1]))


def encode_data_packet(seq_no, segment):
    return encode_packet(DATA_PREAMBLE_LEN, bytearray([2, len(segment), seq_no]) + segment)


def encode_dest_gid(type, gid=None):
    bytes = bytearray([type, 0x3f, 0xff])
    if gid:
        bytes += struct.pack(">Q", gid)[2:]
    return bytes


def encode_shout_message(sender_gid, initials, message):
    packet = encode_tlv(1, TEXT_MESSAGE.encode("utf-8"))
    packet += encode_tlv(3, initials.encode("utf-8"))
    packet += encode_tlv(4, message.encode("utf-8"))
    packet += struct.pack(">H", crc16(packet))

    encryption_info = encode_encryption_info(False, sender_gid, int(time.time()), 0, 0)
    return encode_tlv(ENCRYPTION_INFO, encryption_info) + packet


def encode_key_exchange_response(sender_gid, initials, public_key):
    packet = encode_tlv(1, MESH_KEY_EXCHANGE_RESPONSE.encode("utf-8"))
    packet += encode_tlv(3, initials.encode("utf-8"))
    packet += encode_tlv(252, public_key)
    packet += struct.pack(">H", crc16(packet))

    encryption_info = encode_encryption_info(False, sender_gid, int(time.time()), 0, 0)
    return encode_tlv(ENCRYPTION_INFO, encryption_info) + packet


def encode_encrypted_payload(recipient_gid, sender_gid, counter, ciphertext):
    encryption_info = encode_encryption_info(True, sender_gid, int(time.time()), counter, 0)
    packet = encode_dest_gid(ONE_TO_ONE_GID, recipient_gid)
    packet += bytearray([0x00, 0xff, 0x00, 0x00])
    packet += encode_tlv(ENCRYPTION_INFO, encryption_info)
    packet += ciphertext
    return packet


def encode_packets(channel, payload):
    packets = []
    seq_no = 0
    for offset in range(0, len(payload), PAYLOAD_SPLIT_LEN):
        segment = payload[offset:offset+PAYLOAD_SPLIT_LEN]
        packets.append(encode_data_packet(seq_no, segment))
        seq_no += 1
    return [encode_control_packet(channel, seq_no)] + packets


def encode_shout_packets(channel, sender_gid, initials, message):
    payload = encode_dest_gid(SHOUT_GID) + encode_shout_message(sender_gid, initials, message)
    return encode_packets(channel, payload)


def gfsk_bytes(packets):
    bytes = [0]*HOP_TIME_1 + list(packets[0]) + [0]*HOP_TIME_1
    for packet in packets[1:]:
        bytes += list(packet) + [0]*HOP_TIME_2
    return bytes


def envelope(packets):
    envelope = [0]*HOP_TIME_1 + [1]*(len(packets[0])+1) + [0]*(HOP_TIME_1-1)
    for packet in packets[1:]:
        envelope += [1]*(len(packet)+1) + [0]*(HOP_TIME_2-1)
    return envelope


def vco(center_freq, control_chan, data_chan, packets):
    control_offset = CONTROL_CHANNELS[control_chan] - center_freq
    vco = [control_offset]*(HOP_TIME_1-3+len(packets[0])+HOP_TIME_1)
    for packet in packets[1:]:
        data_offset = DATA_CHANNELS[data_chan] - center_freq
        vco += [data_offset]*(len(packet)+HOP_TIME_2)
        data_chan = (data_chan + 1) % len(DATA_CHANNELS)
    vco += [data_offset]*3
    return vco


def decode_tlv(tag, value):
    if tag == 3:
        print("Initials: " + value.decode())
    elif tag == 4:
        if value[0] == 0xff:
            print("Message content: " + binascii.hexlify(value).decode())
        else:
            print("Message content: " + value.decode())
    elif tag == 5:
        print("Message:")
        decode_tlvs(value)
    elif tag == ENCRYPTION_INFO:
        encrypted, sender_gid, timestamp, enc_counter, resend_id = struct.unpack(">BQIHB", value)
        print("Encrypted: " + str(encrypted))
        print("Sender GID: " + str(sender_gid))
        print("Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))))
        print("Encryption Counter: " + str(enc_counter))
        print("Resend ID: " + str(resend_id))
    else:
        print("Tag: " + str(tag) + " value: " + binascii.hexlify(value).decode())


def decode_tlvs(bytes):
    while len(bytes) >= 2:
        tag = bytes[0]
        length = bytes[1]
        if 2 + length > len(bytes):
            break
        value = bytes[2:2+length]
        bytes = bytes[2+length:]
        decode_tlv(tag, value)
