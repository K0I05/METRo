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
Name:	       Metro_preprocess_interpol_forecast
Description: Interpolation of data in order to be at every 30 seconds.
  Solar flux is a special case.

 TODO MT: Do the update in order that the array are 0-based
 Auteur: Miguel Tremblay
 Date: August 2nd 2004
"""

from metro_preprocess import Metro_preprocess

import time
import numarray

from toolbox import metro_util
from toolbox import metro_date
from toolbox import metro_constant

##
# Class attributes
##
naTime = None # Array representing the time in seconds.


class Metro_preprocess_interpol_forecast(Metro_preprocess):

    def start(self):
        Metro_preprocess.start(self)

        pForecast = self.get_infdata_reference('FORECAST')
        forecast_data = pForecast.get_data_collection()

        self.__set_attribute(forecast_data.get_original_data(),\
                             forecast_data.get_controlled_data())
        self.__interpolate_FT(forecast_data.get_original_data(), \
                              forecast_data.get_controlled_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_AT(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_QP(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_WS(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_TD(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_AP(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_PI(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        self.__interpolate_CC(forecast_data.get_original_data(), \
                              forecast_data.get_interpolated_data() )
        

        pForecast.set_data_collection(forecast_data)


    def __set_attribute(self, wf_original_data, wf_controlled_data):
        """
        Name: __set_attribute

        Parameters: metro_data original_data : original forecast data

        Returns: None

        Functions Called: forecast_data.get_matrix_col
                          numarray.arange,                  
                          metro_date.get_hour
                          wf_controlled_data.append_matrix_col

        Description: Set the naTime array to span all the values
                     of the input matrix. The input must be at every hour.

        Notes: The initialization of the processed_data is made here.

        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 12th 2004
        """
        
        nbrHours = len(wf_original_data.get_matrix_col('AT'))

        self.naTime = numarray.arange(0,nbrHours)*3600        

        #  Used in fsint2.
        naTimeStart = \
            wf_original_data.get_matrix_col('FORECAST_TIME')
        nHourStart = int(metro_date.get_hour(naTimeStart[0]))
        naTimeAtHours = numarray.arange(0,nbrHours) + nHourStart

        wf_controlled_data.append_matrix_col('Hour', naTimeAtHours)


    def __interpolate_FT(self, wf_original_data, wf_controlled_data, \
                         wf_interpolated_data):
        """
        Name: __interpolate_FT

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_processed_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate,
                         metro_data.get_matrix_col
                         metro_data.append_matrix_col

         Description: Interpolate forcast time.
                      Copy self.naTime in wf_processed_data 'FORECAST_TIME'

         Revision History:
         Author		Date		Reason
         Miguel Tremblay      July 13th 2004
         """
        
        naFT = wf_original_data.get_matrix_col('FORECAST_TIME')
        naFT = metro_util.interpolate(self.naTime, naFT, \
                                      metro_constant.fTimeStep)
        wf_interpolated_data.append_matrix_col('FORECAST_TIME', naFT)
        
        nHourStart = int(metro_date.get_hour(naFT[0]))
        naTime = self.naTime
        wf_controlled_data.append_matrix_col('Time', naTime)
        naTime = metro_util.interpolate(self.naTime, naTime, \
                                      metro_constant.fTimeStep)
        naTime = (naTime+30)/3600+nHourStart
        wf_interpolated_data.append_matrix_col('Time', naTime)


    # Air temperature
    def __interpolate_AT(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_AT
        
        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_processed_data : container of the interpolated
                    data.

        Returns: None

        Functions Called: metro_util.interpolate,
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col

        Description: Does the interpolation of the air temperature


        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 12th 2004
        """
        
        naAT = wf_original_data.get_matrix_col('AT')
        naAT = metro_util.interpolate(self.naTime, naAT, \
                                      metro_constant.fTimeStep)
        wf_interpolated_data.append_matrix_col('AT', naAT)

        
    def __interpolate_QP(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_QP

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_interpolated_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate, shift_right
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col


        Description: Add the rain (in mm.) and the snow (in cm.) and store it
                      in RA. Since 1 cm. is, roughly, 1 mm. of water, the sum
                      is considerated in mm.


        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 12th 2004
        """
        naRA = wf_original_data.get_matrix_col('RA')
        naSN = wf_original_data.get_matrix_col('SN')
        naQP = naSN/10*metro_constant.nSnowWaterRatio \
               + naRA

        # Patch because of the -99 at the end of the forecast
        fMax = naQP.max()
        naQP = numarray.where(naQP < 0, fMax, naQP)

        naQP = naQP - metro_util.shift_right(naQP, 0)
        naSN = naSN - metro_util.shift_right(naSN, 0)
        naRA = naRA - metro_util.shift_right(naRA, 0)
        
        naQP = metro_util.interpolate(self.naTime, naQP, \
                                      metro_constant.fTimeStep)
        naSN = metro_util.interpolate(self.naTime, naSN, \
                                      metro_constant.fTimeStep)
        naRA = metro_util.interpolate(self.naTime, naRA, \
                                      metro_constant.fTimeStep)

        naQP = naQP *10e-4 # Set it in meter
        naQP = naQP / 3600.0 # Convert by second
        naQP = numarray.where(naQP < 0, 0, naQP)

        wf_interpolated_data.append_matrix_col('QP', naQP)
        wf_interpolated_data.append_matrix_col('SN', naSN)
        wf_interpolated_data.append_matrix_col('RA', naRA)
        

    # Wind velocity
    def __interpolate_WS(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_WS

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_interpolated_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate,
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col


        Description: Interpolate wind speed.  Wind is in km/h and is converted in
                     m/s by the product with 0.2777777


        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 12th 2004
        """
        naWS = wf_original_data.get_matrix_col('WS')*0.2777777
        naWS = metro_util.interpolate(self.naTime, naWS, \
                                      metro_constant.fTimeStep)
        wf_interpolated_data.append_matrix_col('WS', naWS)
        

    # Dew point
    def __interpolate_TD(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_TD

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_interpolated_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate,
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col


        Description: Interpolate the dew point.


        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 12th 2004
        """
        naTD = wf_original_data.get_matrix_col('TD')
        naTD = metro_util.interpolate(self.naTime, naTD, \
                                      metro_constant.fTimeStep)
        wf_interpolated_data.append_matrix_col('TD', naTD)

        
    # Pressure
    def __interpolate_AP(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_AP

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_interpolated_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate,
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col


         Description: Interpolate the surface pressure. Pressure in in hectopascal.


         Revision History:
         Author		Date		Reason
         Miguel Tremblay      July 12th 2004
         """
        naAP = wf_original_data.get_matrix_col('AP')
        
        # Replace invalid date by the normal pressure (1013.25 mb)
        naAP = numarray.where(naAP < metro_constant.nLowerPressure,\
                              metro_constant.fNormalPressure,  naAP)
        naAP = numarray.where(naAP > metro_constant.nUpperPressure,\
                              metro_constant.fNormalPressure,  naAP)
        
        # Convert it in pascals.
        naAP = naAP*100
        naAP = metro_util.interpolate(self.naTime, naAP, \
                                      metro_constant.fTimeStep)
        wf_interpolated_data.append_matrix_col('AP', naAP)


    # Type of precipitation
    def __interpolate_PI(self, wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_PI

        Parameters:[I] metro_data wf_original_data : original data.  Read-only
                   [I] metro_data wf_interpolated_data : container of the interpolated
                   data.

        Returns: None

        Functions Called: metro_util.interpolate,
                          metro_data.get_matrix_col
                          metro_data.append_matrix_col
                          numarray.where, around

        Description: Interpolate the type of precipitation.  The nearest neighbor is
                      is used.


        Revision History:
        Author		Date		Reason
        Miguel Tremblay      July 15th 2004
        """
        naRA = wf_original_data.get_matrix_col('RA')
        naSN = wf_original_data.get_matrix_col('SN')
        naAT = wf_original_data.get_matrix_col('AT')
        # Replace the last value if they are not good
        if naRA[len(naRA)-1] < 0:
            naRA[len(naRA)-1] = naRA.max()
        if naSN[len(naSN)-1] < 0:
            naSN[len(naSN)-1] = naSN.max()
        
        naDiffRA = naRA - metro_util.shift_right(naRA, 0)
        naDiffSN = naSN - metro_util.shift_right(naSN, 0)
        lPI = []

        for i in range(0, len(naDiffRA)):
            if naDiffRA[i] > 0:
                lPI.append(1)
            elif naDiffSN[i] > 0:
                lPI.append(2)
            elif naAT[i] > 0:
                lPI.append(1)
            else:
                lPI.append(2)

        naPI = numarray.array(lPI)
            
        # Interpolate
        naPI = metro_util.interpolate(self.naTime, naPI, \
                                      metro_constant.fTimeStep)
        # Round
        naPI = numarray.around(naPI)
        # Store
        wf_interpolated_data.append_matrix_col('PI', naPI)



    def __interpolate_CC(self,  wf_original_data, wf_interpolated_data):
        """
        Name: __interpolate_cloud_cover
        
        Parameters:
        [I] metro_data wf_controlled_data : controlled data.  Read-only
        [I] metro_data wf_interpolated_data : container of the interpolated

        Returns: None

        Description: Interpolate the cloud cover. Added in the roadcast file
         to be able to draw the the cloud cover.

        Notes: <other information, if any>
        Revision History:
        Author		Date		Reason
        Miguel Tremblay      June 20th 2005
        """
        lCC = wf_original_data.get_matrix_col('CC')

        naCC = numarray.array(lCC)
            
        # Interpolate
        naCC = metro_util.interpolate(self.naTime, naCC, \
                                      metro_constant.fTimeStep)

        # Round
        naCC = numarray.around(naCC)
        # Store
        wf_interpolated_data.append_matrix_col('CC', naCC)


