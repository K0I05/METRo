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

"""
Name:	       Metro_preprocess_interpol_observation
Description: Interplation of data in order to be at every 30 seconds.
               Solar flux is a particular case.

Author: Miguel Tremblay
Date: August 2nd 2004
"""

from metro_preprocess import Metro_preprocess

import time
import numarray

import metro_config
import metro_logger
from toolbox import metro_util
from toolbox import metro_date
from toolbox import metro_constant

_ = metro_util.init_translation('metro_preprocess_interpol_observation')

##
# Class attributes
##
naTimeInterpolated = None # Array representing the time in seconds.
OneObservationException =  _("Not enough observation to do the interpolation")
NoObservationException = _("No valid observation.  Aborting")

class Metro_preprocess_interpol_observation(Metro_preprocess):

    def start(self):
        Metro_preprocess.start(self)

        pObservation = self.get_infdata_reference('OBSERVATION')
        observation_data = pObservation.get_data_collection()
        
        try: 
            self.__set_time(observation_data.get_controlled_data(), \
                            observation_data.get_interpolated_data(), \
                            observation_data)
            self.__interpolate_AT(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_TD(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_WS(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_ST(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_SST(observation_data.get_controlled_data(),\
                                   observation_data.get_interpolated_data())
            self.__interpolate_PI(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_SC(observation_data.get_controlled_data(), \
                                  observation_data.get_interpolated_data())
            self.__interpolate_validatation(observation_data.\
                                            get_controlled_data(), \
                                            observation_data)      
            
        except OneObservationException:
            print OneObservationException

        pObservation.set_data_collection(observation_data)

    def __set_time(self, ro_controlled_data, ro_interpolated_data,
                   observation_data):
        """
        Name: __set_time
        
        Parameters: metro_data controlled_data : controlled forecast data
        
        Returns: None
        
        Functions Called:  numarray.arange, astype
                           numarray.zeros
                           metro_data.set_matrix
                           metro_data.get_matrix_col
                           metro_data.append_matrix_col
                           observation_data.set_attribute
                           metro_config.get_value('FILE_OBSERVATION_FILENAME')

        Description: Set the time array in the interpolated matrix.

        Notes:

        Revision History:
        Author		Date		Reason
        Miguel Tremblay      August 5th 2004
        """

        # Set the time in the interpolated matrix.
        naTime =  ro_controlled_data.get_matrix_col('Time')
        self.naTimeInterpolated = numarray.arange(naTime[0], \
                                                  naTime[len(naTime)-1],
                                                  metro_constant.fTimeStep)

        # 1.1574e-5 is the conversion from seconds to day.
        #  1/(24*3600) = 1.1574e-5
        self.naTimeInterpolated =  self.naTimeInterpolated/3600 -\
                                  24*((self.naTimeInterpolated*1.1574e-5)\
                                      .astype(numarray.Int32))

        # Save the time array
        if len(self.naTimeInterpolated) > 1:
            ro_interpolated_data.append_matrix_col('Time', \
                                                self.naTimeInterpolated)
        # Only one observation, abort interpolation
        elif len(self.naTimeInterpolated) == 1:
            observation_data.set_attribute('NO_OBS',\
                                           [False, False, False, True])
            raise OneObservationException            
        else:
            observation_data.set_attribute('NO_OBS',\
                                           [True, True, True, True])
            sMessage = _("No valid observation in: ") +\
                       metro_config.get_value('FILE_OBSERVATION_FILENAME')
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                       sMessage)

            raise NoObservationException

####################################################
# Name: __interpolate_AT
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#
# Description: Does the interpolation of the air temperature
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 5th 2004
#####################################################
    # Air temperature
    def __interpolate_AT(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naAT = ro_controlled_data.get_matrix_col('AT')
        naAT = metro_util.interpolate(naTimeOrig, naAT, \
                                      metro_constant.fTimeStep)
        ro_interpolated_data.append_matrix_col('AT', naAT)

####################################################
# Name: __interpolate_TD
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#
# Description: Does the interpolation of the dew point
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 5th 2004
#####################################################
    def __interpolate_TD(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naTD = ro_controlled_data.get_matrix_col('TD')
        naTD = metro_util.interpolate(naTimeOrig, naTD, \
                                      metro_constant.fTimeStep)
        ro_interpolated_data.append_matrix_col('TD', naTD)

####################################################
# Name: __interpolate_WS
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#
# Description: Does the interpolation of the wind speed.
#               Wind is in km/h and is converted in
#               m/s by the product with 0.2777777
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 11th 2004
#####################################################
    def __interpolate_WS(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naWS = ro_controlled_data.get_matrix_col('WS')*0.2777777
        naWS = metro_util.interpolate(naTimeOrig, naWS, \
                                      metro_constant.fTimeStep)
        ro_interpolated_data.append_matrix_col('WS', naWS)

####################################################
# Name: __interpolate_ST
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#
# Description: Does the interpolation of road temperature
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 11th 2004
#####################################################
    def __interpolate_ST(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naST = ro_controlled_data.get_matrix_col('ST')
        naST = metro_util.interpolate(naTimeOrig, naST, \
                                      metro_constant.fTimeStep)
        ro_interpolated_data.append_matrix_col('ST', naST)

####################################################
# Name: __interpolate_SST
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#
# Description: Does the interpolation of road temperature under the surface.
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 11th 2004
#####################################################
    def __interpolate_SST(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naSST = ro_controlled_data.get_matrix_col('SST')

        naSST = metro_util.interpolate(naTimeOrig, naSST, \
                                      metro_constant.fTimeStep)
        ro_interpolated_data.append_matrix_col('SST', naSST)

####################################################
# Name: __interpolate_PI
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#                   numarray.where, around
#
# Description: Does the interpolation of presence of precipitation.
#
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 12th 2004
#####################################################
    def __interpolate_PI(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naPI = ro_controlled_data.get_matrix_col('PI')
        naPI = numarray.where(naPI != 1, 0, naPI)
        naPI = metro_util.interpolate(naTimeOrig, naPI, \
                                      metro_constant.fTimeStep)
        # Round
        naPI = numarray.around(naPI)
        # Store
        ro_interpolated_data.append_matrix_col('PI', naPI)

####################################################
# Name: __interpolate_SC
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   metro_data.get_matrix_col
#                   metro_data.append_matrix_col
#                   numarray.where, around
#
# Description: Does the interpolation of the Road Condition
#
# TODO MT: 33 c'est le code SSI.  Voir si on met le code NTCIP
#  (http://wikid.cmc.ec.gc.ca/tiki-index.php?page=met_Condition+du+pav%C3%A9e)
#  ou simplement un binaire qui devrait etre complete par la personne qui
#  encapsulera les observations dans un format XML.
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 12th 2004
#####################################################
    def __interpolate_SC(self, ro_controlled_data, ro_interpolated_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naSC = ro_controlled_data.get_matrix_col('SC')
        # Convert
        naSC = numarray.where(naSC == 33, 0, 1)
        naSC = numarray.where(naSC < 0, 0, naSC)
        naSC = numarray.where(naSC > 1, 0, naSC)
        naSC = metro_util.interpolate(naTimeOrig, naSC, \
                                      metro_constant.fTimeStep)
        # Round
        naSC = numarray.around(naSC)
        # Store
        ro_interpolated_data.append_matrix_col('SC', naSC)
 
####################################################
# Name: __interpolate_validatation
#
# Parameters:[I] metro_data ro_controlled_data : controlled data.  Read-only
#            [I] metro_data ro_interpolated_data : container of the interpolated
#                 data.
#
# Returns: None
#
# Functions Called: metro_util.interpolate,
#                   observation_data.get_attribute
#                   observation_data.set_attribute
#                   numarray.around
#
# Description: Does the interpolation all the attribute that were set in
#               metro_preprocess_qa_qc_observation
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 12th 2004
#####################################################
    def __interpolate_validatation(self,ro_controlled_data, observation_data):
        naTimeOrig = ro_controlled_data.get_matrix_col('Time')
        naSST = observation_data.get_attribute('SST_VALID')
        naAT = observation_data.get_attribute('AT_VALID')
        naTD = observation_data.get_attribute('TD_VALID')
        naWS = observation_data.get_attribute('WS_VALID')

        # Interpolate
        naSST = metro_util.interpolate(naTimeOrig, naSST, \
                                      metro_constant.fTimeStep)
        naAT = metro_util.interpolate(naTimeOrig, naAT, \
                                      metro_constant.fTimeStep)
        naTD = metro_util.interpolate(naTimeOrig, naTD, \
                                      metro_constant.fTimeStep)
        naWS = metro_util.interpolate(naTimeOrig, naWS, \
                                      metro_constant.fTimeStep)        
        # Round
        naTD = numarray.around(naTD)
        naAT = numarray.around(naAT)
        naSST = numarray.around(naSST)
        naWS = numarray.around(naWS)
        # Store
        observation_data.set_attribute('TD_VALID_INTERPOLATED', naTD)
        observation_data.set_attribute('AT_VALID_INTERPOLATED', naAT)
        observation_data.set_attribute('SST_VALID_INTERPOLATED', naSST)
        observation_data.set_attribute('WS_VALID_INTERPOLATED', naWS)
