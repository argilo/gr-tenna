#!/usr/bin/env python3
#
# Copyright 2024 Clayton Smith (argilo@gmail.com)
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

import base64
import hashlib
import random
import unittest
import gotenna_packet


class TestGotennaPacket(unittest.TestCase):
    def test_gid_hash(self):
        hashes = {
            7339731589953: 0x7c2f,
            91241030429057: 0x2401,
            91251136197976: 0x9b82,
            91341708520410: 0xe39d,
            95681472401029: 0x008c,
            100839877062356: 0x052c,
            243995255577472: 0x907a,
        }

        for gid, expected_hash in hashes.items():
            hash = gotenna_packet.gid_hash(gid)
            self.assertEqual(hash, expected_hash)

    def test_gid_hash_many(self):
        random.seed(1)
        h = hashlib.sha256()
        for n in range(100000):
            gid = random.randrange(0, 2**48)
            hash = gotenna_packet.gid_hash(gid)
            h.update(bytes([hash >> 8, hash & 0xff]))
        self.assertEqual(h.hexdigest(), "f475d7d672eaec0e42ba76a104833df3f9b26667cc45e054f50cda07d4a50219")

    def test_decrypt_qr_message_valid(self):
        password = b"tvhoy7z2"
        salt = base64.b64decode(b"+tnmT6KSlkxzbDvj37vhLA==")
        iv = base64.b64decode(b"VgAAAA==")
        sender_gid = 95681472401029
        key_data = base64.b64decode(b"r0f4ZohFV5TQQoi/Xt4jNNm8piRZBtU9tVGXVUPSIKX1SJhkGawdjidEQirlPVaFo8JU4VoSV7ui8bCNU+sj6v5PYRmhqItgEbHbX5rQJpw=")

        expected_payload = bytes.fromhex("4121c0677575fa79b55fcd000b650378aaed861e03ad9a16e79a2354d7c831c8")
        payload = gotenna_packet.decrypt_qr_message(password, salt, iv, sender_gid, key_data)
        self.assertEqual(payload, expected_payload)

    def test_decrypt_qr_message_incorrect_password(self):
        password = b"tvhoy7z3"
        salt = base64.b64decode(b"+tnmT6KSlkxzbDvj37vhLA==")
        iv = base64.b64decode(b"VgAAAA==")
        sender_gid = 95681472401029
        key_data = base64.b64decode(b"r0f4ZohFV5TQQoi/Xt4jNNm8piRZBtU9tVGXVUPSIKX1SJhkGawdjidEQirlPVaFo8JU4VoSV7ui8bCNU+sj6v5PYRmhqItgEbHbX5rQJpw=")

        with self.assertRaises(Exception):
            gotenna_packet.decrypt_qr_message(password, salt, iv, sender_gid, key_data)


if __name__ == "__main__":
    unittest.main()
