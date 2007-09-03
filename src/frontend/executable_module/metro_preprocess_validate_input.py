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
Name:	      metro_preprocess_validate_input
Description:  Validate input data to make sure they conform to certain rule. 
               1) Forecast and observation must overlap

Note:         Observation file cannot be too long because of the limitation of
               length in the fortran array.
TODO:         Remove length limitation once the fortran code is removed from METRo.
               
Author: Francois Fortin
        Miguel Tremblay
Date: 9 novembre 2004
"""

from metro_preprocess import Metro_preprocess

import metro_logger
import metro_config
from toolbox import metro_date
from toolbox import metro_util
from toolbox import metro_constant

import numarray

_ = metro_util.init_translation('metro_config')

class Metro_preprocess_validate_input(Metro_preprocess):

    def start(self):
        Metro_preprocess.start(self)

        pForecast = self.get_infdata_reference('FORECAST')
        forecast_data = pForecast.get_data_collection()
        pObservation = self.get_infdata_reference('OBSERVATION')
        observation_data = pObservation.get_data_collection()

        self.__validate_observation_length(observation_data.\
                                            get_controlled_data())
        self.__validate_forecast_length(forecast_data.get_controlled_data())


        self.__validate_last_observation_date(observation_data.\
                                            get_controlled_data())

        self.__validate_overlap(forecast_data.get_controlled_data(),
                                observation_data.get_controlled_data())


    def __validate_forecast_length(self, forecast_data):
        """
        Parameters: controlled forecast data
        
        Returns: None
        
        Functions Called: 

        Description: METRo needs more than one forecast date. If there is only one
         forecast, give an error message an exit.

        Notes: 

        Revision History:
        Author		Date		Reason
        Miguel Tremblay      March 20th 2007
        """
        
         # Check the length of forecast. Pick one element at random
        naFT = forecast_data.get_matrix_col('FORECAST_TIME')

        if len(naFT) < 2:
            sMessage = _("METRo needs more than one forecast date! Exiting")
            metro_logger.print_message(
                metro_logger.LOGGER_MSG_STOP, sMessage)

    def __validate_observation_length(self, observation_data):
        """
        Parameters: controlled observation data
        
        Returns: None
        
        Functions Called: 

        Description: Check if the observation is not too long. If so, truncate the
          beginning of the observation. This limitation is due to an array size
          hardcoded in the fortran code. 

        Notes: This method should be removed once the fortran code is removed
                from METRo.

        Revision History:
        Author		Date		Reason
        Miguel Tremblay      April 11th 2007
        """

        # Check the length of observation
        naOT = observation_data.get_matrix_col('OBSERVATION_TIME')
        fLast_observation_date = naOT[len(naOT)-1]
        fFirst_observation_date  = naOT[0]

        fLenght_observation_seconds = fLast_observation_date -\
                                      fFirst_observation_date
        nNbr_30_seconds_step_in_obs = fLenght_observation_seconds/30

        # Check if the length of observation is too high for the fortran code
        if nNbr_30_seconds_step_in_obs > metro_constant.nNL:
            nStepsToRemove = nNbr_30_seconds_step_in_obs -  metro_constant.nNL

            # Format the strings for warning message
            nNumberSecondsToRemove = nStepsToRemove*30
            fNumberHourToRemove = nNumberSecondsToRemove/3600.0
            fNewStartTime = fFirst_observation_date + nNumberSecondsToRemove
            sNewStartTime = metro_date.seconds2iso8601(fNewStartTime)
            # Retrieve the first time in observation that is after this date
            #  numarray trick. Put 0 where the time is under fNewStartTime
            naNumberOfItemToRemove = numarray.where(naOT <fNewStartTime, 1, 0)
            #  Get the indice of the last indice that is not zero
            tNonZero = numarray.nonzero(naNumberOfItemToRemove)
            nRemoveUntilIndice = tNonZero[0][-1]+1
            
            sOldStartTime = metro_date.seconds2iso8601(fFirst_observation_date)
            sMessage = _("Too many observation. Removing the %s seconds ") % \
                       (nNumberSecondsToRemove) + \
                       _("i.e. %s hour(s)\n")   % (fNumberHourToRemove) + \
                       _("Old start time is %s\n") % (sOldStartTime) + \
                       _("New start time is %s") % (sNewStartTime)
            metro_logger.print_message(
                metro_logger.LOGGER_MSG_WARNING, sMessage)

            # Warning is done, remove the data
            observation_data.del_matrix_row(range(nRemoveUntilIndice))


    def __validate_last_observation_date(self, observation_data):
        """
        Parameters: controlled observation data
        
        Returns: None
        
        Functions Called: 

        Description: Set the date of the last observation.

        Notes: 

        Revision History:
        Author		Date		Reason
        Miguel Tremblay      August 4th 2004
        """

        # Get the last observation
        naOT = observation_data.get_matrix_col('OBSERVATION_TIME')
        fLast_observation_date = naOT[len(naOT)-1]
        sStart_date = metro_date.seconds2iso8601(fLast_observation_date)
        metro_config.set_value('DATA_ATTRIBUTE_LAST_OBSERVATION', sStart_date)
        sMessage = _("Last observation date is: '%s'") % (sStart_date)
        metro_logger.print_message(metro_logger.LOGGER_MSG_INFORMATIVE,\
                                   sMessage)            
        

    def __validate_overlap( self, forecast_data, observation_data ):
        """        
        Parameters: forecast_data, observation_data

        Description: Make sure forecast and observation overlap, if it's
                     not the case abort METRo

        """

        fForecast_start = forecast_data.get_matrix_col('FORECAST_TIME')[0]
        naObservation = observation_data.get_matrix_col('OBSERVATION_TIME')
        fObservation_end = naObservation[len(naObservation)-1]

        if fForecast_start > fObservation_end:
            sForecast_start = metro_date.seconds2iso8601(fForecast_start)
            sObservation_end = metro_date.seconds2iso8601(fObservation_end)
            sError = _("Forecast and observation don't overlap. The date\n") +\
            _("of the first forecast must be before the last date of ") +\
            _("observation.\nFirst Forecast='%s'\nLast Observation='%s'") \
            %(sForecast_start,sObservation_end)

            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sError)
