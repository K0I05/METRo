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
Name:		Metro_preprocess_combine
 Description: Combine the observation and the atmospheric forecast.
  Relaxation is done on the 6 first hours of forecast.
 Notes: TODO MT: Enlever le -3*3600/30 ou trouver une raison satisfaisante
  pour sa presence.
 Author: Miguel Tremblay
 Date: August 19th 2004
"""

import math
import numarray

from metro_preprocess import Metro_preprocess
from toolbox import metro_constant
from toolbox import metro_physics

class Metro_preprocess_combine(Metro_preprocess):


##
# Class attributes
##

    nDeltaIndice = 0 # The number of 30 seconds steps in the observation. 
    NTP = 0 # max(self.nDeltaIndice,0)
    NTP2 = 0 # min(self.nDeltaIndice,0)
    
#####################################################
    
    def start(self):
        Metro_preprocess.start(self)

        pForecast = self.get_infdata_reference('FORECAST')
        forecast_data = pForecast.get_data_collection()
        pObservation = self.get_infdata_reference('OBSERVATION')
        observation_data = pObservation.get_data_collection()
        
        self.__set_attribute(observation_data)
        self.__combine_AT(forecast_data.get_interpolated_data(),
                          observation_data.get_interpolated_data(),
                          observation_data)
        self.__combine_TD(forecast_data.get_interpolated_data(),
                          observation_data.get_interpolated_data(),
                          observation_data)
        self.__combine_WS(forecast_data.get_interpolated_data(),
                          observation_data.get_interpolated_data(),
                          observation_data)
        self.__combine_QP(forecast_data.get_interpolated_data(),
                          observation_data.get_interpolated_data())
        self.__create_AH(forecast_data.get_interpolated_data())

        pForecast.set_data_collection(forecast_data)
        pObservation.set_data_collection(observation_data)

####################################################        
# Name: __set_attribute
#
# Parameters:
#
# Returns: None
#
# Functions Called: max, min
#                   observation_data.get_attribute
#
# Description: Compute the number of 30 seconds step in the observation.
#   Uses self.observation_data.DELTA_T, i.e. the number of hours in the
#   observation to do so.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 20th 2004
#####################################################
    def __set_attribute(self, observation_data):
        fDeltaTMetroObservation = observation_data.get_attribute('DELTA_T')
        self.nDeltaIndice = int(fDeltaTMetroObservation*3600/30.)
        self.NTP = max(self.nDeltaIndice,0)
        self.NTP2 = min(self.nDeltaIndice,0)

####################################################        
# Name: __combine_AT
        #
# Parameters:[I] metro_data wf_interpolated_data : interpolated forecast data. 
#            [I] metro_data wf_interpolated_data :  interpolated observation data. 
# Returns: None
#
# Functions Called:wf_interpolated_data.get_matrix_col
#                  observation_data.get_attribute
#                  numarray.where
#
# Description: Combine the air temperature of forecast and observation.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 19th 2004
#####################################################
    def __combine_AT(self, wf_interpolated_data, \
                     ro_interpolated_data, observation_data):        

        naAT = wf_interpolated_data.get_matrix_col('AT')
        naATO = ro_interpolated_data.get_matrix_col('AT')

        nLenATO = len(naATO)
        nLenAT = len(naAT)-3*3600/30

        # Check if there is an error in the observation
        naSwo = observation_data.get_attribute('AT_VALID_INTERPOLATED')
        naSwo = naSwo[self.nDeltaIndice:nLenATO]
        naCheck = numarray.where(naSwo == 0, 1, 0)
        naBadIndices = (numarray.nonzero(naCheck))[0]
        if len(naBadIndices) == 0:
            for i in range(0, nLenATO-self.NTP):
                naAT[i-self.NTP2] = naATO[i+self.NTP-1]
            # Relaxation des observations vers la prevision.
            # Relaxation of observation to forecast.
            # Constante de 4 heures / 4 hour relaxation constant
            nFactor = nLenATO-self.NTP
            fTaCorr = naAT[nLenATO-self.NTP-self.NTP2]-naATO[nLenATO-1]
            if fTaCorr != 0:
                if self.NTP2 < 0:
                    nValueSup = nLenAT + self.NTP2
                else:
                    nValueSup = nLenAT
#                nValueSup = nLenATO-self.NTP + 460
                for i in range(nLenATO-self.NTP, nValueSup):
                    naAT[i-self.NTP2] = naAT[i-self.NTP2]-math.exp(-(i-nFactor)\
                                               *metro_constant.fTimeStep \
                                               *metro_constant.fConst)*fTaCorr


        wf_interpolated_data.set_matrix_col('AT', naAT)  

####################################################        
# Name: __combine_TD
        #
# Parameters:[I] metro_data wf_interpolated_data : interpolated forecast data. 
#            [I] metro_data wf_interpolated_data :  interpolated observation data. 
# Returns: None
#
# Functions Called: wf_interpolated_data.get_matrix_col
#                   numarray.where, nonzero
#
# Description: Combine the dew point of forecast and observation.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 23th 2004
#####################################################
    def __combine_TD(self, wf_interpolated_data, \
                     ro_interpolated_data, observation_data):        

        naTD = wf_interpolated_data.get_matrix_col('TD')
        naAT = wf_interpolated_data.get_matrix_col('AT')
        naTDO = ro_interpolated_data.get_matrix_col('TD')
        
        nLenTDO = len(naTDO)
        nLenTD = len(naTD)-3*3600/30

        # Check if there is an error in the observation
        naSwo = observation_data.get_attribute('TD_VALID_INTERPOLATED')
        naSwo = naSwo[self.nDeltaIndice:nLenTDO]
        naCheck = numarray.where(naSwo == 0, 1, 0)
        naBadIndices = (numarray.nonzero(naCheck))[0]
        # If there is no error in the dew point, use the observations, otherwise
        #  use the forecast for all the observation.
        if len(naBadIndices) == 0:
            for i in range(0, nLenTDO-self.NTP):
                naTD[i-self.NTP2] = naTDO[i+self.NTP-1]

            # Relaxation des observations vers la prevision.
            # Constante de 4 heures / 4 hour relaxation constant
            nFactor = nLenTDO-self.NTP
            fTdCorr = naTD[nLenTDO-self.NTP-self.NTP2]-naTDO[nLenTDO-1]
            if fTdCorr != 0:
                if self.NTP2 < 0:
                    nValueSup = nLenTD + self.NTP2
                else:
                    nValueSup = nLenTD
                for i in range(nLenTDO-self.NTP, nValueSup):
                    naTD[i-self.NTP2] = naTD[i-self.NTP2]-math.exp(-(i-nFactor)\
                                               *metro_constant.fTimeStep \
                                               *metro_constant.fConst)*fTdCorr
                    if  naTD[i-self.NTP2] >  naAT[i-self.NTP2]:
                         naTD[i-self.NTP2] =  naAT[i-self.NTP2]

        wf_interpolated_data.set_matrix_col('TD', naTD)
 
####################################################        
# Name: __combine_WS
        #
# Parameters:[I] metro_data wf_interpolated_data : interpolated forecast data. 
#            [I] metro_data wf_interpolated_data :  interpolated observation data. 
# Returns: None
#
# Functions Called: metro_data.get_matrix_col
#                   collection_data.get_attribute
#                   numarray.where, nonzero
#
# Description: Combine the wind speed of forecast and observation.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 23th 2004
#####################################################
    def __combine_WS(self, wf_interpolated_data, \
                     ro_interpolated_data, observation_data):        

        naWS = wf_interpolated_data.get_matrix_col('WS')
        
        naWSO = ro_interpolated_data.get_matrix_col('WS')
        nLenWSO = len(naWSO)
        nLenWS = len(naWS)-3*3600/30

        # Check if there is an error in the observation
        naSwo = observation_data.get_attribute('WS_VALID_INTERPOLATED')
        naSwo = naSwo[self.nDeltaIndice:nLenWSO]
        naCheck = numarray.where(naSwo == 0, 1, 0)
        naBadIndices = (numarray.nonzero(naCheck))[0]
        if len(naBadIndices) == 0:
            for i in range(0, nLenWSO-self.NTP):
                naWS[i-self.NTP2] = naWSO[i+self.NTP-1]

            # Relaxation of observation on the atmospheric forecast
            # 4 hour relaxation constant
            nTimeStepsInRelaxation = 4*3600/metro_constant.fTimeStep
            # Check if there is long enough atmospheric forecast
            if nLenWS <  nTimeStepsInRelaxation:
                nTimeStepsInRelaxation = nLenWS
            nValueSup = nLenWSO-self.NTP + nTimeStepsInRelaxation
            if self.NTP2 < 0:
                nValueSup = int(round(nValueSup + self.NTP2))
            else: # Cast anyway
                nValueSup = int(round(nValueSup))
            nFactor = nLenWSO-self.NTP
            fCurrentObs = naWSO[nLenWSO-1]
            fCurrentFor = naWS[nLenWSO-self.NTP-self.NTP2]
            if fCurrentObs < fCurrentFor:
                if fCurrentFor == 0:
                    fCurrentFor = 1.0
                if fCurrentObs == 0:
                    fCurrentObs = 1.0
                fTdCorr = fCurrentObs/fCurrentFor
                fSlope = (1-fTdCorr)*metro_constant.fConst*\
                         metro_constant.fTimeStep
                for i in range(int(round(nLenWSO-self.NTP)), nValueSup):
                    fFactor = fSlope*(i-nLenWSO+self.NTP)+fTdCorr
                    naWS[i-self.NTP2] = fFactor*naWS[i-self.NTP2]
                
            elif fCurrentFor < fCurrentObs:
                fTdCorr = fCurrentFor - fCurrentObs
                for i in range(int(round(nLenWSO-self.NTP)), nValueSup):  
                    naWS[i-self.NTP2] = naWS[i-self.NTP2]-math.exp(-(i-nFactor)\
                                           *metro_constant.fTimeStep \
                                           *metro_constant.fConst)*fTdCorr

        wf_interpolated_data.set_matrix_col('WS', naWS)
        
#####################################################
# Name: __combine_QP
#
# Parameters:[I] metro_data wf_interpolated_data : interpolated forecast data. 
#            [I] metro_data wf_interpolated_data :  interpolated observation data. 
# Returns: None
#
# Functions Called: metro_data.get_matrix_col
#                   collection_data.get_attribute
#
# Description: Set the precipitation rate with the accumulations.
#  Create the road condition.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 24th 2004
#####################################################
    def __combine_QP(self, wf_interpolated_data, \
                     ro_interpolated_data):        
        
        naQP = wf_interpolated_data.get_matrix_col('QP')

        # Create the road condition array. 0 is dry, 1 is wet
        # This is only use in the initialization of profile
        naSC = numarray.ones(len(naQP))

        # PI is equal to 1 when there is precipitation, 0 otherwise.
        naPI = ro_interpolated_data.get_matrix_col('PI')
        naSCO = ro_interpolated_data.get_matrix_col('SC')
        nLenPI = len(naPI)
        nLenQP = len(naQP)-3*3600/30

        for i in range(0, nLenPI-self.NTP):
            naQP[i-self.NTP2] = naPI[i+self.NTP-1]*\
                                (naQP[i+1-self.NTP2])
            naSC[i-self.NTP2] = naSCO[i+self.NTP-1]

        wf_interpolated_data.set_matrix_col('QP',naQP)
        wf_interpolated_data.append_matrix_col('SC',naSC)

#####################################################
# Name: __create_QA
#
# Parameters:[I] metro_data wf_interpolated_data : interpolated forecast data. 
#            [I] metro_data wf_interpolated_data :  interpolated observation data. 
# Returns: None
#
# Functions Called: metro_data.get_matrix_col
#                   numarray.zeros, astype
#                   metro_physics.foqst
#                    metro_data.append_matrix_col
#
# Description: Computation of the absolute humidity (g/kg)
#  see http://en.wikipedia.org/wiki/Absolute_humidity for a definition.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      August 24th 2004
#####################################################
    def __create_AH(self, wf_interpolated_data):
        
        # Get any of the interpolated forecast to retrieve the length
        naTD = wf_interpolated_data.get_matrix_col('TD')
        naAP = wf_interpolated_data.get_matrix_col('AP')

        naLenAH = len(naTD)

        # Create the array
        naAH = numarray.zeros(naLenAH)
        naAH = naAH.astype(numarray.Float)

        for i in range(0,naLenAH):
            naAH[i] = metro_physics.foqst(naTD[i]+metro_constant.fTcdk,\
                                           naAP[i])
            
        wf_interpolated_data.append_matrix_col('AH', naAH)
