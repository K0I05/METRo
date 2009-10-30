#
# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006

#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://gna.org/projects/metro/
#  Documentation: http://documentation.wikia.com/wiki/METRo
#
#
# Code contributed by:
#  Miguel Tremblay - Canadian meteorological center
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
#
#

from metro_data import Metro_data

import metro_config
from toolbox import metro_util

_ = metro_util.init_translation('metro_data_station')

#===============================================================================
#
# Name: Metro_dada_station
#
# Description: Contenue d'un fichier "station" . Les donnees sont contenus
#              dans un dictionnaire (header). La partie matrix de l'objet
#              contient les roadlayer.
#
#===============================================================================

class Metro_data_station(Metro_data):
    """Specialised class for station data.

    This class inherit Metro_data. It add some method facilating the
    manipulation of station data.
    """

    # Get the longitude of the station
    def get_longitude(self):
        """Get the longitude of the station."""
        dStation_header = self.get_header()
        tLatlon = dStation_header['COORDINATE']
        fLon = tLatlon[1]
        return fLon

    # Get the latitude of the station
    def get_latitude(self):
        """Get the latitude of the station."""
        dStation_header = self.get_header()
        tLatlon = dStation_header['COORDINATE']
        fLat = tLatlon[0]
        return fLat

    def get_station_name(self):
        """Get the station name"""
        dStation_header = self.get_header()
        return dStation_header['ROAD_STATION']
    
####################################################
# Name: get_station_type
#
# Parameters:
#
# Returns: bool bFlat : True if the station is on a bridge, False if it
#  is on a road.
#
# Functions Called:
#   . . .
#
# Description: Returns a boolean indicating if the RWIS station is on a 
#  road or a bridge
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 19th 2004
#####################################################
    def get_station_type(self):
        """Get the station type

        Return True if the station is on a bridge, False if on the road.
        """
        dStation_header = self.get_header()
        sStation_type = dStation_header['STATION_TYPE']
        if sStation_type == "road" or  sStation_type == "route":
            bFlat = False
        elif sStation_type == "bridge" or  sStation_type == "pont":
            bFlat = True
        else:
            sMessage =  _("Wrong argument in the station config file %s.") \
                       % (metro_config.get_value('FILE_STATION_FILENAME')) +\
                       _("Station type must be \"road\" or \"bridge\". ") + \
                       _( "Using \"road\" as default.")
            metro_logger.print_message(metro_logger.LOGGER_MSG_CRITICAL,\
                                      sMessage)
            bFlat = False
            
        return bFlat
