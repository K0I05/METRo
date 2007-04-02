#!/bin/sh
#
# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) 2006 Environment Canada

#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://gna.org/projects/metro/
#  Documentation: http://documentation.wikia.com/wiki/METRo
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

# SETUP TRAP
ERRMSG="\nERR - METRo Install - $progname : Script terminated due to
error.  Correct error and restart.\n\n"

trap 'echo -e $ERRMSG; exit 1' ERR

progname=`basename $0`

installation_dir=`pwd`

metro_dir=metro

bCompile=0

# 'getopts' processes command line args to script.

# Usage: scriptname -options
# Note: dash (-) necessary

# Try invoking this script with
# 'scriptname -mn'
# 'scriptname -oq qOption'
# (qOption can be some arbitrary string.)

OPTERROR=33

if [ -z $1 ]
# Exit and complain if no argument(s) given.
then
    echo ""
    echo "Usage: $progname [-c] destination_path"
    echo ""
    echo "-c  : Will compile the METRo physic model instead of using"
    echo "      the provided binary. Need gfortran compiler."  
    echo ""      
    echo ""
    echo "The metro directory will be created in the destination_path"
    echo ""
    echo "Ex: ./setup.sh /usr/local/"
    echo "    ./setup.sh /home/user/program/"
    exit 0
fi  


while getopts "c" Option
do
  case $Option in
    c     ) bCompile=1;;
    *     ) echo ""
            echo "Usage: $progname [-c] destination_path"
            echo ""
            echo "-c  : Will compile the METRo physic model instead of using"
            echo "      the provided binary. Need gfortran compiler."  
            echo ""
            echo "The metro directory will be created in the destination_path"
            echo ""
            echo "Ex: ./setup.sh /usr/local/"
            echo "    ./setup.sh /home/user/program/"
            exit $OPTERROR;;
  esac
done

shift $(($OPTIND - 1))
# Decrements the argument pointer
# so it points to next argument.

destination_path=$1/$metro_dir

echo "* Starting METRo Installation *"
echo ""

if [ -d $destination_path ]; then
    echo "Warning target directory: $destination_path already exist."
    echo "Installing a different version of METRo over an existing one"
    echo "is not recommanded."
    echo "Do you want to continue? [y|n]"
    read answer
    if [ ! "$answer" = y ]; then
        echo "Exiting..."
        exit 0
    fi
fi

# check if gfortran library exist on the target system
echo "* Checking for libgfortran.so.1"
if ! locate libgfortran.so.1; then
    echo "----------------------------------------------------------"
    echo "WARNING!"
    echo "Could not find gfortran library on your system."
    echo "METRo model will be recompiled."
    echo "----------------------------------------------------------"
    echo ""
    bCompile=1
fi
    

if [ $bCompile == 1 ]; then
    if [ ! -n "$PYTHON_INCLUDE" ] ; then
        echo "----------------------------------------------------------"
        echo "WARNING!"
        echo "No python path defined. setup.sh may not be able"
        echo "to properly install METRo."
        echo "Please set environment variable PYTHON_INCLUDE to your"
        echo "python include directory."
        echo "Ex: export PYTHON_INCLUDE=\"/usr/local/include/python2.3\""
        echo "----------------------------------------------------------"
	echo ""
    fi
    cd src/model
    ../../scripts/do_macadam clean
    ../../scripts/do_macadam
    cd $installation_dir
else
    echo "* Use provided binary for physic model"
    if [ ! -d $installation_dir/src/frontend/model ]; then
        mkdir  $installation_dir/src/frontend/model
    fi
    touch $installation_dir/src/frontend/model/__init__.py
    cp $installation_dir/src/model/_macadam.so.prebuilt $installation_dir/src/frontend/model/_macadam.so
    cp $installation_dir/src/model/macadam.py.prebuilt $installation_dir/src/frontend/model/macadam.py
fi

echo ""
echo "* Creating destination directory: "$destination_path
mkdir -p $destination_path
echo ""
echo "* Copying METRo files..."
echo ""
echo "* Copying METRo programs files to: "$destination_path/bin
cp -r src/frontend $destination_path/bin

echo  "* Copying METRo data exemples to: "$destination_path/data
cp -r data $destination_path/

#echo  "* Copying METRo external lib to: "$destination_path/bin/external_lib/
#cp lib/* $destination_path/bin/external_lib/

echo  "* Copying METRo documentation to: "$destination_path/doc
cp -r doc $destination_path/

cd $installation_dir

echo "* Changing name of METRo executable:"
echo "  $destination_path/bin/metro.py -> $destination_path/bin/metro"
mv $destination_path/bin/metro.py $destination_path/bin/metro  

echo ""
echo "---------------------------------------------------"
echo "METRo successfully installed in '$destination_path'"
echo "---------------------------------------------------"
echo ""
echo "* Installation done *"
echo ""
echo "To test the installation of METRo"
echo "---------------------------------"
echo "Go into the METRo directory:"
echo " 'cd $destination_path/bin/'" 
echo "Launch METRo selftest:"
echo " 'python metro --selftest'"
echo "Compare the files:"
echo " 'diff ../data/roadcast/roadcast_selftest.xml ../data/roadcast/roadcast_selftest_reference.xml'"
echo "They should be identical except for the production-date."

