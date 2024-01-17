#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
import gotenna_packet
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

ASN1_PREFIX_PUBLIC = bytes.fromhex("3076301006072a8648ce3d020106052b81040022036200")
ASN1_PREFIX_PRIVATE = bytes.fromhex("3081b6020100301006072a8648ce3d020106052b8104002204819e30819b0201010430")

parser = argparse.ArgumentParser(description="Decrypt keys stored in Android SharedPreferences.")
parser.add_argument("filename")
args = parser.parse_args()

tree = ET.parse(args.filename)
map = tree.getroot()

# Load keys into a dictionary
keys = {}
for child in map:
    name = child.attrib["name"]
    key = bytes.fromhex(child.text)
    keys[name] = key

# Look for a known public or private key
target_name = None
target_key = None
for name, key in sorted(keys.items(), key=lambda item: -len(item[1])):
    if name.startswith("PRIVATE"):
        gid = int(name[7:])
        if gid in gotenna_packet.private_keys:
            target_name = name
            target_key = gotenna_packet.private_keys[gid]
            break
    elif name.startswith("PUBLIC_SELF"):
        gid = int(name[11:])
        if gid in gotenna_packet.public_keys:
            target_name = name
            target_key = ASN1_PREFIX_PUBLIC + gotenna_packet.public_keys[gid]
            break
    elif name.startswith("PUBLIC_OTHER"):
        gid = int(name[12:])
        if gid in gotenna_packet.public_keys:
            target_name = name
            target_key = gotenna_packet.public_keys[gid]
            break

if not target_name:
    raise Exception("No known public or private key found")

known_plaintext = target_key.hex().upper().encode("ASCII")
ciphertext = keys[target_name]
keystream = bytes(p ^ c for p, c in zip(known_plaintext, ciphertext))

for name, key in keys.items():
    plaintext = bytes(k ^ c for k, c in zip(keystream, key[:-16])).decode("ASCII").lower()
    plaintext_bytes = bytes.fromhex(plaintext)

    if len(keystream) < len(key[:-16]):
        plaintext += "?" * (len(key[:-16]) - len(keystream))

        # Attempt to recover partial private keys
        if name.startswith("PRIVATE") and len(plaintext_bytes) >= len(ASN1_PREFIX_PRIVATE) + 48:
            gid = int(name[7:])
            if plaintext_bytes[:len(ASN1_PREFIX_PRIVATE)] == ASN1_PREFIX_PRIVATE:
                curve = ec.SECP384R1()
                private_value = int.from_bytes(plaintext_bytes[len(ASN1_PREFIX_PRIVATE):len(ASN1_PREFIX_PRIVATE) + 48])
                private_key = ec.derive_private_key(private_value, curve)
                private_key_bytes = private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
                if plaintext_bytes == private_key_bytes[:len(plaintext_bytes)]:
                    gotenna_packet.private_keys[gid] = private_key_bytes
                else:
                    print(f"Error: Recovered {name} has incorrect prefix")
            else:
                print(f"Error: {name} has unexpected prefix")
    else:
        # Got the entire plaintext. Store it for future use.
        if name.startswith("PRIVATE"):
            gid = int(name[7:])
            gotenna_packet.private_keys[gid] = plaintext_bytes
        elif name.startswith("PUBLIC_SELF"):
            gid = int(name[11:])
            if plaintext_bytes[:len(ASN1_PREFIX_PUBLIC)] == ASN1_PREFIX_PUBLIC:
                gotenna_packet.public_keys[gid] = plaintext_bytes[len(ASN1_PREFIX_PUBLIC):]
            else:
                print(f"Error: {name} has unexpected prefix")
        elif name.startswith("PUBLIC_OTHER"):
            gid = int(name[12:])
            gotenna_packet.public_keys[gid] = plaintext_bytes
        elif len(name) == 6:
            gotenna_packet.broadcast_keys[name] = plaintext_bytes

    print(f"{name}: {plaintext}")

gotenna_packet.save_keys()
