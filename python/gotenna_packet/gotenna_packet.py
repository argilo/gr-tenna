#!/usr/bin/env python3
#
# Copyright 2018-2024 Clayton Smith (argilo@gmail.com)
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

import enum
import struct
import time
import reedsolo
import json
import base64
import csv
import os
import google
from .proto import base_message_pb2
from .proto import data_type_pb2
from .proto import message_pb2
from google.protobuf import json_format
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import load_der_private_key


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

WHITENING = [
    0x03, 0x96, 0x6a, 0x0f, 0xe7, 0xe5, 0x09, 0xde, 0xc4, 0xd8, 0x52, 0x3d, 0x76, 0x68, 0xbe, 0x2b,
    0x03, 0x8e, 0x1f, 0x09, 0x0e, 0x07, 0x6b, 0x4b, 0x61, 0x78, 0xb2, 0xfb, 0x81, 0x78, 0x36, 0x2a,
    0x1e, 0xcd, 0x8a, 0x76, 0x30, 0x85, 0x59, 0x32, 0xe1, 0x3c, 0xc9, 0xae, 0x34, 0x5c, 0x27, 0x98,
    0x34, 0x70, 0xcd, 0x88, 0x0c, 0xd4, 0x46, 0x0c, 0x62, 0x7d, 0xfc, 0x52, 0xe4, 0x03, 0x15, 0xb9,
    0x8a, 0x9f, 0x46, 0x64, 0x60, 0xe5, 0x98, 0x2c, 0x3e, 0x4b, 0x2e, 0xb7, 0x0f, 0xd9, 0xf2, 0x88,
    0xcf, 0xde, 0x8f, 0x31, 0xa2, 0x18, 0xb5, 0x0c, 0x20, 0x8f, 0x8c, 0x9f, 0x53, 0xa0, 0x6b, 0x4e,
    0x60, 0x78, 0x43, 0x88, 0x30, 0xb8, 0xd5, 0xfa, 0x13, 0xdf, 0x59, 0x41, 0xea, 0x85, 0x2a, 0xf3,
    0xc9, 0x27, 0xc2, 0x00, 0x69, 0xee, 0xb2, 0x4e, 0xd5, 0x09, 0x93, 0x93, 0x36, 0xff, 0xf5, 0xae,
    0xf2, 0xdf, 0x01, 0x1c, 0xb1, 0x9e, 0xa4, 0x73, 0x87, 0xf1, 0xa1, 0xcb, 0xae, 0x2e, 0x60, 0x1b,
    0x36, 0x0b, 0x45, 0xd0, 0xf0, 0xc8, 0x8d, 0xe9, 0x51, 0x25, 0xb4, 0x7e, 0x9b, 0x21, 0x02, 0x20,
    0xcb, 0x22, 0x46, 0x5a, 0xf2, 0x0c, 0xcb, 0x07, 0x17, 0x03, 0xde, 0x52, 0x96, 0x5a, 0x6e, 0x7d,
    0x14, 0x76, 0xc7, 0x1d, 0x01, 0xd4, 0x60, 0xf4, 0x5a, 0x12, 0xed, 0x6a, 0x7b, 0x6a, 0xd8, 0x41,
    0x93, 0xd3, 0x42, 0xfd, 0x46, 0x44, 0xaf, 0xda, 0x13, 0x3e, 0x25, 0x6a, 0x88, 0xbb, 0x4c, 0x65,
    0xac, 0x37, 0x7c, 0x6d, 0x9f, 0xd3, 0x3c, 0x17, 0xdc, 0x8a, 0x57, 0x4f, 0xcf, 0xb9, 0x0d, 0x96,
    0x18, 0xa6, 0x7b, 0xb2, 0xa6, 0x78, 0x33, 0xe1, 0x8f, 0xc4, 0xaf, 0x94, 0xd6, 0x31, 0x84, 0xb4,
    0x8c, 0xe9, 0x66, 0xb6, 0xd3, 0xd1, 0xca, 0x46, 0x3d, 0xd0, 0x62, 0x8d, 0x37, 0xc8, 0x84, 0x1c,
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

TAG_TYPE = 1
TAG_INITIALS = 3
TAG_MESSAGE_CONTENT = 4
TAG_MESSAGE = 5
TAG_ENCRYPTION_INFO = 251
TAG_PUBLIC_KEY = 252

MESH_SYNC = 0x01
MESH_DATA = 0x02
MESH_ACK = 0x03
PRO_SYNC = 0x10
PRO_DATA = 0x20


class ConversationType(enum.Enum):
    PRIVATE = 0
    GROUP = 1
    BROADCAST = 2
    EMERGENCY = 3
    UNKNOWN = 4
    ACTIVE_NODE = 5


TEXT_MESSAGE = b"0"
MESH_KEY_EXCHANGE_REQUEST = b"14"
MESH_KEY_EXCHANGE_RESPONSE = b"15"

type_names = {
    TEXT_MESSAGE: "Text message",
    MESH_KEY_EXCHANGE_REQUEST: "Mesh key exchange request",
    MESH_KEY_EXCHANGE_RESPONSE: "Mesh key exchange response",
}

PAYLOAD_SPLIT_LEN = 90
CONTROL_PREAMBLE_LEN = 93
DATA_PREAMBLE_LEN = 10
HOP_TIME_1 = 33
HOP_TIME_2 = 27

PRO_PAYLOAD_SPLIT_LEN = 94
PRO_CONTROL_PREAMBLE_LEN = 58
PRO_DATA_PREAMBLE_LEN = 30
PRO_HOP_TIME = 33

public_keys = {}
private_keys = {}
group_keys = {}
broadcast_keys = {}

key_types = {
    "public": public_keys,
    "private": private_keys,
    "group": group_keys,
    "broadcast": broadcast_keys,
}

mesh_fragments = []


def compress_point(x, y):
    return bytes([2 | (y & 1)]) + x.to_bytes(48, byteorder="big")


def uncompress_point(data):
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
    a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc
    b = 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef

    x = int.from_bytes(data[1:], byteorder="big")
    y_squared = (pow(x, 3, p) + x * a + b) % p
    y = pow(y_squared, (p + 1) // 4, p)
    if (data[0] & 1) != (y & 1):
        y = p - y
    return x, y


def crc16(in_bytes):
    reg = 0x0000
    for b in in_bytes:
        reg = ((reg & 0xff) << 8) ^ CRC16_TABLE[(b ^ (reg >> 8)) & 0xff]
    return reg


def encode_packet(preamble_len, in_bytes):
    length = len(in_bytes) + 2 + 8
    packet = bytes([length]) + in_bytes
    packet += struct.pack(">H", crc16(packet) ^ 0xabcd)
    rs = reedsolo.RSCodec(nsym=8, fcr=1)
    return bytes([0xaa]*preamble_len + [0x2d, 0xd4]) + rs.encode(packet)


def encode_tlv(type, value):
    return bytes([type, len(value)]) + value


def encode_encryption_info(encrypted, sender_gid, timestamp, enc_counter, resend_id):
    return struct.pack(">BQIHB", encrypted, sender_gid, timestamp, enc_counter, resend_id)


def encode_control_packet(channel, num_data_packets):
    return encode_packet(CONTROL_PREAMBLE_LEN, bytes([9, channel, num_data_packets, 1, 1]))


def encode_data_packet(seq_no, segment):
    return encode_packet(DATA_PREAMBLE_LEN, bytes([2, len(segment), seq_no]) + segment)


def encode_dest_gid(app_id, type, gid=None):
    data = struct.pack(">BH", type, app_id)
    if gid:
        data += struct.pack(">Q", gid)[2:]
    return data


def encode_shout_message(sender_gid, initials, message):
    packet = encode_tlv(TAG_TYPE, TEXT_MESSAGE)
    packet += encode_tlv(TAG_INITIALS, initials.encode("utf-8"))
    packet += encode_tlv(TAG_MESSAGE_CONTENT, message.encode("utf-8"))
    packet += struct.pack(">H", crc16(packet))

    encryption_info = encode_encryption_info(False, sender_gid, int(time.time()), 0, 0)
    return encode_tlv(TAG_ENCRYPTION_INFO, encryption_info) + packet


def encode_key_exchange_response(sender_gid, initials, public_key):
    packet = encode_tlv(TAG_TYPE, MESH_KEY_EXCHANGE_RESPONSE)
    packet += encode_tlv(TAG_INITIALS, initials.encode("utf-8"))
    packet += encode_tlv(TAG_PUBLIC_KEY, public_key)
    packet += struct.pack(">H", crc16(packet))

    encryption_info = encode_encryption_info(False, sender_gid, int(time.time()), 0, 0)
    return encode_tlv(TAG_ENCRYPTION_INFO, encryption_info) + packet


def encode_encrypted_payload(app_id, recipient_gid, sender_gid, counter, ciphertext):
    encryption_info = encode_encryption_info(True, sender_gid, int(time.time()), counter, 0)
    packet = encode_dest_gid(app_id, ONE_TO_ONE_GID, recipient_gid)
    packet += bytes([0x00, 0xff, 0x00, 0x00])
    packet += encode_tlv(TAG_ENCRYPTION_INFO, encryption_info)
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


def encode_shout_packets(channel, app_id, sender_gid, initials, message):
    payload = encode_dest_gid(app_id, SHOUT_GID) + encode_shout_message(sender_gid, initials, message)
    return encode_packets(channel, payload)


def gfsk_bytes(packets):
    data = [0]*HOP_TIME_1 + list(packets[0]) + [0]*HOP_TIME_1
    for packet in packets[1:]:
        data += list(packet) + [0]*HOP_TIME_2
    return data


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
    if tag == TAG_TYPE:
        print(f"Type: {value.decode()} ({type_names[value]})")
    elif tag == TAG_INITIALS:
        print("Initials: " + value.decode())
    elif tag == TAG_MESSAGE_CONTENT:
        if value[0] == 0xff:
            print("Message content: " + value.hex())
        else:
            print("Message content: " + value.decode())
    elif tag == TAG_MESSAGE:
        print("Message:")
        decode_tlvs(value)
    elif tag == TAG_ENCRYPTION_INFO:
        encrypted, sender_gid, timestamp, enc_counter, resend_id = struct.unpack(">BQIHB", value)
        print("Encrypted: " + str(encrypted))
        print("Sender GID: " + str(sender_gid))
        print("Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))))
        print("Encryption Counter: " + str(enc_counter))
        print("Resend ID: " + str(resend_id))
    elif tag == TAG_PUBLIC_KEY:
        print("Public key: " + value.hex())
    else:
        print("Tag: " + str(tag) + " value: " + value.hex())


def decode_tlvs(data):
    while len(data) >= 2:
        tag = data[0]
        length = data[1]
        if 2 + length > len(data):
            break
        value = data[2:2+length]
        data = data[2+length:]
        decode_tlv(tag, value)


def gid_hash(gid):
    reg = 170
    output = 0
    for i in range(40, -8, -8):
        reg += (gid >> i) & 0xff
        reg *= 48271
        reg %= 2**32
        reg += 1
        reg %= (2**31 - 1)
        output ^= reg
    return (output >> 16) ^ (output & 0xffff)


def encode_pro_packet(preamble_len, in_bytes):
    packet_type = in_bytes[0] & 0x3f
    nsym = 4 if packet_type == PRO_SYNC else 8

    length = len(in_bytes) + 2 + nsym
    packet = bytes([length]) + in_bytes
    packet += struct.pack(">H", crc16(packet))
    rs = reedsolo.RSCodec(nsym=nsym, fcr=1)
    packet = bytes(p ^ w for p, w in zip(rs.encode(packet), WHITENING))
    symbols = [2, 0]*preamble_len + [0, 2, 3, 1, 3, 1, 1, 0]
    for p in packet:
        symbols.append(p >> 6)
        symbols.append((p >> 4) & 0b11)
        symbols.append((p >> 2) & 0b11)
        symbols.append(p & 0b11)
    return symbols


def encode_pro_control_packet(num_data_packets, transmitter_gid):
    packet = bytes([(num_data_packets << 6) | PRO_SYNC, 0x00, 0x00, 0x60, 0xff, 0xff]) \
           + struct.pack("<H", gid_hash(transmitter_gid)) \
           + bytes([0xff, 0xff, 0x00])
    return encode_pro_packet(PRO_CONTROL_PREAMBLE_LEN, packet)


def encode_pro_data_packet(seq_no, segment):
    return encode_pro_packet(PRO_DATA_PREAMBLE_LEN, bytes([(seq_no << 6) | PRO_DATA]) + segment)


def encode_pro_packets(payload, transmitter_gid):
    packets = []
    seq_no = 0
    for offset in range(0, len(payload), PRO_PAYLOAD_SPLIT_LEN):
        segment = payload[offset:offset+PRO_PAYLOAD_SPLIT_LEN]
        packets.append(encode_pro_data_packet(seq_no, segment))
        seq_no += 1
    return [encode_pro_control_packet(seq_no, transmitter_gid)] + packets


def encode_pro_broadcast_packets(message_type, counter_num, sender_gid, recipient_gid, callsign, message, publickey_data):
    mode = 0
    counter = counter_num

    base_message = base_message_pb2.PBBaseMessage()
    base_message.header.sender_gid = sender_gid

    if message_type == "BROADCAST":
        base_message.header.callsign = callsign
        base_message.header.messageType = data_type_pb2.TEXT
        base_message.header.timestamp = time.time()
    
        text_message = message_pb2.PBTextMessageData()
        text_message.text = message
        base_message.messageData = text_message.SerializeToString()

        payload = bytes([(ConversationType.BROADCAST.value << 2) | 2, 0x80, 0x00, mode, counter, 0x00, 0x56, 0x28]) \
            + struct.pack(">H", gid_hash(sender_gid)) \
            + base_message.SerializeToString()

    if message_type == "PUBLICKEY":
        base_message.header.messageType = data_type_pb2.PUBLIC_KEY_REQUEST
        publickey = message_pb2.PBPublicKeyMessageData()
        publickey.public_key = base64.b64decode(publickey_data)
        base_message.messageData = publickey.SerializeToString()

        payload = bytes([(ConversationType.PRIVATE.value << 2) | 2, 0x80, 0x00, mode, counter, 0x00, 0x56, 0x28]) \
            + struct.pack(">H", gid_hash(sender_gid)) \
            + struct.pack(">H", gid_hash(recipient_gid)) \
            + base_message.SerializeToString()
    
        
    return encode_pro_packets(payload, sender_gid)


def pro_gfsk_symbols(packets):
    data = [4]*PRO_HOP_TIME
    for packet in packets:
        data += packet + [4]*PRO_HOP_TIME
    return data


def decrypt_qr_message(password, salt, iv, sender_gid, key_data):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA1(), length=32, salt=salt, iterations=10000)
    key = kdf.derive(password)

    full_iv = iv + struct.pack("<Q", sender_gid)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(full_iv, key_data, None)
    except InvalidTag:
        raise Exception("Invalid AES-GCM authentication tag")

    payload = plaintext[:-32]
    expected_hmac = plaintext[-32:]

    h = hmac.HMAC(payload, hashes.SHA256())
    h.update(salt)
    received_hmac = h.finalize()

    if received_hmac != expected_hmac:
        raise Exception("Invalid HMAC")

    return payload


def decrypt_pro(ciphertext, encryption_key, gid, iv):
    aesgcm = AESGCM(encryption_key)
    full_iv = iv + struct.pack("<Q", gid)
    try:  # TODO: Use correct length threshold to decide between GCM and CTR
        plaintext = aesgcm.decrypt(full_iv, ciphertext, None)
    except InvalidTag:
        cipher = Cipher(algorithms.AES(encryption_key), modes.CTR(full_iv + bytes([0, 0, 0, 2])))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext


def decrypt_broadcast(ciphertext, shared_key, gid, iv):
    h = hmac.HMAC(shared_key, hashes.SHA256())
    h.update(struct.pack("<Q", gid) + shared_key)
    encryption_key = h.finalize()
    return decrypt_pro(ciphertext, encryption_key, gid, iv)


def decrypt_p2p_group(ciphertext, shared_key, gid, iv):
    if gid not in public_keys:
        raise Exception(f"Could not find public key for gid {gid}")

    h = hmac.HMAC(shared_key, hashes.SHA256())
    h.update(struct.pack("<Q", gid) + public_keys[gid] + shared_key)
    encryption_key = h.finalize()
    return decrypt_pro(ciphertext, encryption_key, gid, iv)


def decode_coords(data):
    return struct.unpack("<dd", data)


def decode_coords_list(data):
    return [decode_coords(data[i:i+16]) for i in range(0, len(data), 16)]


def process_data_frag(data, fragIDX, pro=False):
    """
    Process a fragment of a data PDU
    """

    if fragIDX >= len(mesh_fragments):
        print(f"Invalid fragment index: {fragIDX}")
        return

    mesh_fragments[fragIDX] = data
    if all(mesh_fragments):
        data = b"".join(mesh_fragments)
        if pro:
            process_data_pro(data)
        else:
            process_data_mesh(data)


def process_data_mesh(data):
    """Process a reassembled Gotenna Mesh packet"""

    offset = 0

    conv_type = ConversationType(data[offset])
    print(f"Conversation type: {conv_type.name}")
    offset += 1

    app_id = struct.unpack(">H", data[offset:offset+2])[0]
    print(f"App ID: {app_id:04x}")
    offset += 2

    if conv_type in (ConversationType.PRIVATE, ConversationType.GROUP):
        gid_hi, gid_lo = struct.unpack(">HL", data[offset:offset+6])
        gid = (gid_hi << 32) | gid_lo
        print(f"Dest. GID: {gid}")
        offset += 6

        print(f"Unknown: {data[offset:offset+4].hex()}")
        offset += 4

    decode_tlvs(data[offset:])


def process_data_pro(data):
    """Process a reassembled Gotenna Pro packet"""

    print(f"Reassembled packet: {data.hex()}")

    offset = 0

    conv_type = ConversationType(data[offset] >> 2)
    print(f"Conversation type: {conv_type.name}")
    offset += 1

    print(f"Unknown: {data[offset:offset+2].hex()}")
    offset += 2
    mode = data[offset]
    print(f"mode: {hex(data[offset])}")
    offset += 1
    print(f"Counter: {data[offset]}")
    offset += 1
    print(f"Unknown: {data[offset:offset+3].hex()}")
    offset += 3
    print(f"Sender GID hash: {data[offset:offset+2].hex()}")
    offset += 2

    if conv_type in (ConversationType.PRIVATE, ConversationType.GROUP):
        recipient_gid_hash = struct.unpack(">H", data[offset:offset+2])[0]
        offset += 2
        print(f"Recipient GID hash: {recipient_gid_hash:04x}")
        recipient_gid = None
        key_store = public_keys if conv_type == ConversationType.PRIVATE else group_keys
        for gid in key_store.keys():
            if gid_hash(gid) == recipient_gid_hash:
                recipient_gid = gid
                print(f"Found recipient GID: {recipient_gid}")
                break

    if mode == 0x80:
        print(f"Unknown: {data[offset:].hex()}")
        return
    elif mode == 0x20:
        print(f"Unknown: {data[offset:].hex()}")
        return
    else:
        base_message = base_message_pb2.PBBaseMessage()
        try:
            base_message.ParseFromString(data[offset:])
        except google.protobuf.message.DecodeError:
            print("Error parsing base message")
            return

        print(json_format.MessageToJson(base_message.header))

        message_type = base_message.header.messageType

        if message_type == data_type_pb2.PBMessageDataType.GROUP_CREATION:
            message = None
            priv_key = private_keys.get(base_message.header.sender_gid)
            pub_key = public_keys.get(recipient_gid)
            if not (priv_key and pub_key):
                priv_key = private_keys.get(recipient_gid)
                pub_key = public_keys.get(base_message.header.sender_gid)

            if priv_key and pub_key:
                ec_priv_key = load_der_private_key(priv_key, None)
                curve = ec.SECP384R1()
                ec_pub_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, pub_key)

                shared_key = ec_priv_key.exchange(ec.ECDH(), ec_pub_key)
                base_message.messageData = decrypt_p2p_group(base_message.messageData,
                                                             shared_key,
                                                             base_message.header.sender_gid,
                                                             base_message.header.iv)
                message = message_pb2.PBGroupCreationMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.MAP_OBJECT:
            message = message_pb2.PBMapObjectMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.REQUEST:
            message = message_pb2.PBRequestMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.TEXT:
            if base_message.header.iv:
                message = None
                if conv_type == ConversationType.BROADCAST:
                    uuid = base_message.header.keyUuid
                    if uuid in broadcast_keys:
                        shared_key = broadcast_keys[uuid]
                        base_message.messageData = decrypt_broadcast(base_message.messageData,
                                                                     shared_key,
                                                                     base_message.header.sender_gid,
                                                                     base_message.header.iv)
                        message = message_pb2.PBTextMessageData()
                if conv_type == ConversationType.GROUP:
                    shared_key = group_keys.get(recipient_gid)
                    if shared_key:
                        base_message.messageData = decrypt_p2p_group(base_message.messageData,
                                                                     shared_key,
                                                                     base_message.header.sender_gid,
                                                                     base_message.header.iv)
                        message = message_pb2.PBTextMessageData()
                if conv_type == ConversationType.PRIVATE:
                    priv_key = private_keys.get(base_message.header.sender_gid)
                    pub_key = public_keys.get(recipient_gid)
                    if not (priv_key and pub_key):
                        priv_key = private_keys.get(recipient_gid)
                        pub_key = public_keys.get(base_message.header.sender_gid)

                    if priv_key and pub_key:
                        ec_priv_key = load_der_private_key(priv_key, None)
                        curve = ec.SECP384R1()
                        ec_pub_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, pub_key)

                        shared_key = ec_priv_key.exchange(ec.ECDH(), ec_pub_key)
                        base_message.messageData = decrypt_p2p_group(base_message.messageData,
                                                                     shared_key,
                                                                     base_message.header.sender_gid,
                                                                     base_message.header.iv)
                        message = message_pb2.PBTextMessageData()
            else:
                message = message_pb2.PBTextMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.FREQUENCY:
            message = message_pb2.PBFrequencyMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.PING:
            message = None
        elif message_type == data_type_pb2.PBMessageDataType.EMERGENCY_BEACON:
            message = None
        elif message_type == data_type_pb2.PBMessageDataType.PUBLIC_KEY_REQUEST:
            message = message_pb2.PBPublicKeyMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.PUBLIC_KEY_RESPONSE:
            message = message_pb2.PBPublicKeyMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.BROADCAST_QR:
            message = message_pb2.PBBroadcastQrMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.PLI:
            message = None
        elif message_type == data_type_pb2.PBMessageDataType.SHARED_LOCATION:
            message = message_pb2.PBLocationMessageData()
        elif message_type == data_type_pb2.PBMessageDataType.COMMS_CHECK:
            message = None
        elif message_type == data_type_pb2.PBMessageDataType.MANUAL_PLI:
            message = None

        if message:
            message.ParseFromString(base_message.messageData)

            if isinstance(message, message_pb2.PBLocationMessageData):
                json_dict = json.loads(json_format.MessageToJson(message))
                json_dict['coordinate'] = decode_coords(message.coordinate)
                print(json.dumps(json_dict, indent=2))
            elif isinstance(message, message_pb2.PBMapObjectMessageData):
                json_dict = json.loads(json_format.MessageToJson(message))
                if message.HasField("pin"):
                    json_dict['pin']['coordinate'] = decode_coords(message.pin.coordinate)
                elif message.HasField("shape"):
                    if message.shape.HasField("circle_data"):
                        json_dict['shape']['circleData']['center'] = decode_coords(message.shape.circle_data.center)
                    elif message.shape.HasField("rectangle_data"):
                        json_dict['shape']['rectangleData']['cornerOne'] = decode_coords(message.shape.rectangle_data.cornerOne)
                        json_dict['shape']['rectangleData']['cornerTwo'] = decode_coords(message.shape.rectangle_data.cornerTwo)
                        json_dict['shape']['rectangleData']['depth'] = decode_coords(message.shape.rectangle_data.depth)
                    elif message.shape.HasField("perimeter_data"):
                        json_dict['shape']['perimeterData']['dataPoints'] = decode_coords_list(message.shape.perimeter_data.data_points)
                    elif message.shape.HasField("route_data"):
                        json_dict['shape']['routeData']['dataPoints'] = decode_coords_list(message.shape.route_data.data_points)
                print(json.dumps(json_dict, indent=2))
            elif isinstance(message, message_pb2.PBPublicKeyMessageData):
                curve = ec.SECP384R1()
                public_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, message.public_key)
                print(public_key.public_numbers())
                print(json_format.MessageToJson(message))
            else:
                print(json_format.MessageToJson(message))

            # Store any observed keys
            if isinstance(message, message_pb2.PBGroupCreationMessageData):
                group_keys[message.group_gid] = message.group_shared_key
                save_keys()
            elif isinstance(message, message_pb2.PBPublicKeyMessageData):
                public_keys[base_message.header.sender_gid] = message.public_key
                save_keys()

        else:
            print(f"Encrypted/unknown message: {base_message.messageData.hex()}")


def correct_packet(data):
    data = bytes(data)
    packet_type = data[1] & 0x3f

    # Reed-Solomon error correction
    nsym = 4 if packet_type == PRO_SYNC else 8
    rs = reedsolo.RSCodec(nsym=nsym, fcr=1)
    try:
        data, _, _ = rs.decode(data)
    except reedsolo.ReedSolomonError:
        raise Exception("Too many byte errors")

    # CRC check
    packetCRC, = struct.unpack(">H", data[-2:])
    diff = packetCRC ^ crc16(data[:-2])
    if diff not in (0x0000, 0xabcd):
        raise Exception("Invalid CRC")

    # Strip length header & CRC
    return data[1:-2]


def ingest_packet(data):
    global mesh_fragments

    print()
    print(data.hex())
    packet_type = data[0] & 0x3f

    if packet_type == MESH_SYNC:
        # Gotenna Mesh "SYNC" packet - contains data channel index and TTL data
        chIDX, frags, iniTTL, curTTL = struct.unpack("BBBB", data[1:5])
        print(f"RX SYNC (0x{packet_type:02x}): chIDX={chIDX}, frags={frags}, iniTTL={iniTTL}, curTTL={curTTL}")
        mesh_fragments = [None] * frags
        # in real life, hop to index ++chIDX in datachan map
        #  to receive first data packet of this transmission

    elif packet_type == MESH_DATA:
        # Gotenna Mesh "DATA" packet - contains message data, may be fragmented
        datalen, fragIDX = struct.unpack("BB", data[1:3])
        print(f"RX DATA (0x{packet_type:02x}): len={datalen}, fragIDX={fragIDX}")
        # strip first 4 bytes and send to reassembly
        process_data_frag(data[3:], fragIDX)
        # in real life, hop to index ++chIDX in datachan map
        #  to receive *next* data packet of this transmission

    elif packet_type == MESH_ACK:
        # Gotenna Mesh "ACK" packet - contains message hash ID and number of hops
        hashID, hopTTL, curTTL = struct.unpack(">HBB", data[1:5])
        print(f"RX ACK (0x{packet_type:02x}): hash=0x{hashID:04x}, TTL/hop(?)=0x{hopTTL:02x}, curTTL={curTTL}")

    elif packet_type == PRO_SYNC:
        # Gotenna Pro "SYNC" packet
        frags = data[0] >> 6
        print(f"RX SYNC (0x{packet_type:02x}): frags={frags} unknown={data[1:].hex()}")
        mesh_fragments = [None] * frags

    elif packet_type == PRO_DATA:
        # Gotenna Pro "DATA" packet
        fragIDX = data[0] >> 6
        print(f"RX DATA (0x{packet_type:02x}): fragIDX={fragIDX}")
        process_data_frag(data[1:], fragIDX, pro=True)

    else:
        print(f"RX TYPE 0x{packet_type:02x} UNKNOWN")


xdg_data = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
data_dir = os.path.join(xdg_data, "gr-tenna")
os.makedirs(data_dir, exist_ok=True)
keys_filename = os.path.join(data_dir, "keys.csv")


def save_keys(filename=keys_filename):
    with open(filename, "w", newline="") as csv_file:
        keys_writer = csv.DictWriter(csv_file, fieldnames=["key_type", "name", "value_base64"])
        keys_writer.writeheader()
        for key_type, key_store in key_types.items():
            for name, value in key_store.items():
                keys_writer.writerow({"key_type": key_type, "name": name, "value_base64": base64.b64encode(value).decode("ASCII")})


def load_keys(filename=keys_filename):
    if os.path.exists(keys_filename):
        with open(filename, newline="") as csv_file:
            keys_reader = csv.DictReader(csv_file)
            for row in keys_reader:
                key_type = row["key_type"]
                name = row["name"] if key_type == "broadcast" else int(row["name"])
                value = base64.b64decode(row["value_base64"])

                key_store = key_types[key_type]
                key_store[name] = value


load_keys()
