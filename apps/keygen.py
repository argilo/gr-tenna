#!/usr/bin/env python3

import argparse
import gotenna_packet
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

ASN1_PREFIX_PUBLIC = bytes.fromhex("3076301006072a8648ce3d020106052b81040022036200")

parser = argparse.ArgumentParser(description="Generate a key pair for Gotenna Pro.")
parser.add_argument("gid", type=int)
args = parser.parse_args()

curve = ec.SECP384R1()
private_key = ec.generate_private_key(curve)
private_key_bytes = private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
gotenna_packet.private_keys[args.gid] = private_key_bytes

public_key = private_key.public_key()
public_key_bytes = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
if public_key_bytes[:len(ASN1_PREFIX_PUBLIC)] == ASN1_PREFIX_PUBLIC:
    gotenna_packet.public_keys[args.gid] = public_key_bytes[len(ASN1_PREFIX_PUBLIC):]
else:
    print("Error: public key not in expected format")

gotenna_packet.save_keys()
