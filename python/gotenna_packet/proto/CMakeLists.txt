# Copyright 2024 Clayton Smith.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Install python sources
########################################################################
gr_python_install(FILES
    __init__.py
    base_message_pb2.py
    data_type_pb2.py
    frequency_pb2.py
    header_pb2.py
    location_pb2.py
    message_pb2.py
    DESTINATION ${GR_PYTHON_DIR}/gotenna_packet/proto)
