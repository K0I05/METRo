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

####################################################
# Name:	       Metro_postprocess_display_roadcast
# Description:  Display the roadcast on a graphic.
# Notes: Uses gnuplot.
# Auteur: Miguel Tremblay
# Date: 10 septembre 2004
####################################################

from metro_postprocess import Metro_postprocess

import sys

from toolbox import metro_util

_ = metro_util.init_translation('metro_postprocess_display_roadcast')

class Metro_postprocess_display_roadcast(Metro_postprocess):

    # Attributs
    
    module_roadcast_graphics = None

####################################################
# Name: __init__
#
# Parameters: 
#
# Returns: None
#
# Functions Called:  __import__
#
# Description: import the package that uses gnuplot in the directory
#  "graphics".
#
# Notes:
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      September 11th 2004
#####################################################
    def __init__(self, lData_types=[]):
        try:
            pathInclude = sys.path[0] + '/executable_module/graphics'
            sys.path.append(pathInclude)
            self.module_roadcast_graphics = __import__("metro_graphics_roadcast")

        except ImportError, sError:
            sImportError = _("Error when importing the package ") +\
                           _("metro_graphics.\nCheck if the directory %s ") \
                           % (pathInclude) +\
                           _("exists and if the file ") +\
                           _("metro_graphics_roadcast.py is in this ") + \
                           _("this directory.\nPython return the following") +\
                           _("error:'%s'") % (sError)
            raise sImportError

    def start(self):
        Metro_postprocess.start(self)

        #
        # fetch data
        #
        pRoadcast = self.get_infdata_reference('ROADCAST')
        roadcast_data = pRoadcast.get_data_collection()        
        pForecast = self.get_infdata_reference('FORECAST')
        forecast_data = pForecast.get_data_collection()
        pStation = self.get_infdata_reference('STATION')
        station_data = pStation.get_data()
        if self.infdata_exist('OBSERVATION_REF'):
            pObservation_ref = self.get_infdata_reference('OBSERVATION_REF')
            observation_ref_data = pObservation_ref.get_data_collection()
        else:
            observation_ref_data = None
        
        self.module_roadcast_graphics.show_roadcast_temperature(\
            roadcast_data.get_controlled_data(),\
            forecast_data.get_controlled_data(), station_data)
        if observation_ref_data != None:

            self.module_roadcast_graphics.compare_roadcast_temperature(\
            roadcast_data.get_subsampled_data(),
            observation_ref_data.get_controlled_data(), \
            forecast_data.get_original_data(),station_data)

#            self.module_roadcast_graphics.bare_display2(\
#            forecast_data.get_controlled_data().get_matrix_col('SF'),
#            forecast_data.get_controlled_data().get_matrix_col('IR'),
#            'Solar and infra-red flux', \
#            '/users/dor/afsg/mit/METRo/archive/images/flux.ps')

