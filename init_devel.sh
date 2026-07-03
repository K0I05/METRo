#!/bin/bash
#
# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006

#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
#
# Code contributed by:
#  Francois Fortin - Canadian meteorological center
#
#  $LastChangedDate$
#  $LastChangedRevision$
#
########################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# prepare development environment

echo "* create logging directory ( mkdir -p var/log/ )"
if [ ! -d var/log/ ]; then
    mkdir -p var/log/
fi
echo ""

echo "* link to model ( src/frontend/model -> usr/share/metro/model )"
ln -sTf ../../usr/share/metro/model src/frontend/model
echo ""

echo "* link to metro.py ( usr/bin/metro -> src/frontend/metro.py )"
mkdir -p usr/bin
ln -sTf ../../src/frontend/metro.py usr/bin/metro
echo ""

if which python3-config >/dev/null; then
    PYTHON_INC=`python3-config --includes`
    echo "* Python include path = "$PYTHON_INC
fi

