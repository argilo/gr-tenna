#!/usr/bin/env python3

import base64
import gotenna_packet

# Define password below
password = b"0fo79vu6"

# Add information directly from the BROADCAST_QR message

header = {
  "senderGid": "95681472401029",
  "callsign": "Dollarhyde",
  "messageType": "BROADCAST_QR",
  "iv": "/AAAAA==",
  "timestamp": 1707450048.91588
}
data = {
  "name": "dGh1cnMgICAgIA==",
  "uuid": "Bw==",
  "salt": "kkn+R3vB2JaAr8BhZzFWJA==",
  "iv": "/AAAAA==",
  "keyData": "Ge12ZsekePbnBIEwAasXsZOpMyrPeoTut9FoIU2crhJgEx6aVRgraV1KCN6W0d0OhUWWGK53C/yzmWVJqdcbn9CfGbjAHc4C4fKOeyGyZm0="
}

data = {key: base64.b64decode(value.encode()) for key, value in data.items()}
payload = gotenna_packet.decrypt_qr_message(password, data["salt"], data["iv"], int(header["senderGid"]), data["keyData"])
name = data["name"].decode('utf-8').strip()
key_UUID = data["uuid"].hex() + hex(gotenna_packet.gid_hash(int(header["senderGid"])))[2:].upper().zfill(4)

print(f"Key \"{name}\", UUID \"{key_UUID}\": {payload.hex()}")
#print(f"Add below to gotenna_packet broadcast_keys:")
#print(f"\"{key_UUID}\": bytes.fromhex(\"{payload.hex()}\")")

gotenna_packet.broadcast_keys[key_UUID] = payload
gotenna_packet.save_keys()

