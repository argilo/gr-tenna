# Copyright 2024 Clayton Smith.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Install python sources
########################################################################
gr_python_install(FILES
    __init__.py
    gotenna_packet.py
    DESTINATION ${GR_PYTHON_DIR}/gotenna_packet)


########################################################################
# Add subdirectories
########################################################################
add_subdirectory(proto)
