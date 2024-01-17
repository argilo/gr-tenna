```
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
```

gr-tenna
========

The goal of this project is to implement the goTenna Mesh protocol in GNU Radio.
So far there are flow graphs for receiving and transmitting "Shout" messages
using a USRP B200 or HackRF.

## Installation

```
mkdir build
cd build
cmake ..
make
sudo make install
```

## Usage

To receive messages using a USRP:
```
apps/gotenna_rx_usrp.py
```

To receive messages using a HackRF:
```
apps/gotenna_rx_hackrf.py
```

To transmit a shout message using a USRP:
```
apps/gotenna_tx_usrp.py --app-id=0x3fff --sender-gid=1234567890 --initials=XYZ --message="Hello world!"
```

To transmit a shout message using a HackRF:
```
apps/gotenna_tx_hackrf.py --app-id=0x3fff --sender-gid=1234567890 --initials=XYZ --message="Hello world!"
```

## Protocol Buffers

If `.proto` files are updated, the corresponding Python code can be regenerated as follows:

```
protoc -Iprotobuf --python_out=python protobuf/gotenna_packet/proto/*.proto
```

## Credits

This project builds on reverse engineering work done by Woody [@tb69rr](https://twitter.com/tb69rr)
and Tim [@bjt2n3904](https://twitter.com/bjt2n3904), and presented in the
Wireless Village at DEF CON 25: https://www.youtube.com/watch?v=pKP74WGa_s0

[`reedsolo.py`](https://github.com/tomerfiliba/reedsolomon) was written by Tomer
Filiba and released into the public domain.
