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

from metro_module import Metro_module

import sys

import metro_config
import metro_logger
from toolbox import metro_xml
from toolbox import metro_util
from data_module import metro_data
from data_module import metro_data_station
from data_module import metro_data_collection_input


_ = metro_util.init_translation('metro_dom2metro')


class Metro_dom2metro(Metro_module):

    ##
    # attributs de la classe
    ##
    domForecast    = None
    domObservation = None
    domStation     = None



    ##
    # Overwritten methodes
    ##
    def start(self):
        Metro_module.start(self)

        pForecast        = self.get_infdata_reference('FORECAST')
        pObservation     = self.get_infdata_reference('OBSERVATION')
        pStation         = self.get_infdata_reference('STATION')
        if self.infdata_exist('OBSERVATION_REF'):
            pObservation_ref = self.get_infdata_reference('OBSERVATION_REF')
        else:
            pObservation_ref = None
            
        
        self.domForecast        = pForecast.get_input_information()
        self.domObservation     = pObservation.get_input_information()
        if pObservation_ref != None:
            self.domObservation_ref = pObservation_ref.get_input_information()
        else:
            self.domObservation_ref = None
        self.domStation         = pStation.get_input_information()

        #
        # Forecast extraction
        #

        # validate version number
        sFilename = metro_config.get_value('FILE_FORECAST_IN_FILENAME')
        sFile_version = metro_xml.xpath(self.domForecast,"//version")

        sMin_version = metro_config.get_value('FILE_FORECAST_IN_MIN_VERSION')
        sMax_version = metro_config.get_value('FILE_FORECAST_IN_MAX_VERSION')
        self.validate_file_version_number(sFilename, sFile_version,
                                       sMin_version, sMax_version)
            
        try:
            # concatenation of all the keys of the header
            lHeader_keys = \
                metro_config.get_value('XML_FORECAST_HEADER_STANDARD_ITEMS') + \
                metro_config.get_value('XML_FORECAST_HEADER_EXTENDED_ITEMS')

            # xpath building
            sHeader_xpath = metro_config.get_value('XML_FORECAST_XPATH_HEADER')
            sData_xpath = \
                metro_config.get_value('XML_FORECAST_XPATH_PREDICTION')
            
            # concatenation of all forecast types
            lStandard_forecast = \
                metro_config.get_value('XML_FORECAST_PREDICTION_STANDARD_ITEMS')
            lExtended_forecast = \
                metro_config.get_value('XML_FORECAST_PREDICTION_EXTENDED_ITEMS')
            forecast_data = metro_data.Metro_data(lStandard_forecast,\
                                             lExtended_forecast)

            forecast_data = self.__extract_data_from_dom(forecast_data,
                                                         self.domForecast,
                                                         lHeader_keys,
                                                         sHeader_xpath,
                                                         lStandard_forecast,
                                                         lExtended_forecast,
                                                         sData_xpath)
        except "IOERROR":
            sXmlError = _("XML error in file '%s'.") % (sFilename)
            raise sXmlError

        # create forecast collection
        lForecast_standard_attribute = metro_config.get_value(
            'DATA_ATTRIBUTE_FORECAST_STANDARD')
        lForecast_extended_attribute = metro_config.get_value(
            'DATA_ATTRIBUTE_FORECAST_EXTENDED')
        lForecast_attribute = lForecast_standard_attribute \
                              + lForecast_extended_attribute
        forecast = metro_data_collection_input.Metro_data_collection_input(
            forecast_data, lForecast_attribute)

        #
        # Extraction des observations
        #
        
        # validate version number
        sFilename = metro_config.get_value('FILE_OBSERVATION_FILENAME')
        sFile_version = metro_xml.xpath(self.domObservation,"*/version/text()")
        sMin_version = metro_config.get_value('FILE_OBSERVATION_MIN_VERSION')
        sMax_version = metro_config.get_value('FILE_OBSERVATION_MAX_VERSION')
        self.validate_file_version_number(sFilename, sFile_version,
                                       sMin_version, sMax_version)

        try:
            # concatenation de toutes les cles du header
            lHeader_keys = \
                metro_config.get_value( 'XML_OBSERVATION_HEADER_STANDARD_ITEMS') + \
                metro_config.get_value('XML_OBSERVATION_HEADER_STANDARD_ITEMS')

            # construction du xpath
            sHeader_xpath = metro_config.get_value('XML_OBSERVATION_XPATH_HEADER')
            # construction du xpath
            sData_xpath = metro_config.get_value('XML_OBSERVATION_XPATH_MEASURE')
            
            # concatenation de tout les types d'observation
            lStandard_observation = metro_config.get_value( \
            'XML_OBSERVATION_MEASURE_STANDARD_ITEMS')
            lExtended_observation = metro_config.get_value( \
            'XML_OBSERVATION_MEASURE_EXTENDED_ITEMS')        

            obs_data = metro_data.Metro_data(lStandard_observation,lExtended_observation)

            observation_data = self.__extract_data_from_dom(obs_data,
                                                            self.domObservation,
                                                            lHeader_keys,
                                                            sHeader_xpath,
                                                            lStandard_observation,
                                                            lExtended_observation,
                                                            sData_xpath)
        except "METRoDateError", sError:
            sXmlError = _("XML error in file '%s'.\n") % (sFilename) +\
                        sError
            raise sXmlError
        except :
            sXmlError = _("XML error in file '%s'.") % (sFilename)
            raise sXmlError

        # create observation collection
        lObservation_standard_attribute = metro_config.get_value(
            'DATA_ATTRIBUTE_OBSERVATION_STANDARD')
        lObservation_extended_attribute = metro_config.get_value(
            'DATA_ATTRIBUTE_OBSERVATION_EXTENDED')
        lObservation_attribute = lObservation_standard_attribute \
                                 + lObservation_extended_attribute
        observation = metro_data_collection_input.Metro_data_collection_input(
            observation_data, lObservation_attribute)


        #
        # Extraction des observations_ref
        #
        
        if self.domObservation_ref != None:

            # validate version number
            sFilename = metro_config.get_value('FILE_OBSERVATION_REF_FILENAME')
            sFile_version = \
                metro_xml.xpath(self.domObservation_ref,"*/version/text()")
            sMin_version = \
                metro_config.get_value('FILE_OBSERVATION_MIN_VERSION')
            sMax_version = \
                metro_config.get_value('FILE_OBSERVATION_MAX_VERSION')
            self.validate_file_version_number(sFilename, sFile_version,
                                           sMin_version, sMax_version)
            
            try:
                # concatenation de toutes les cles du header
                lHeader_keys = \
                    metro_config.get_value('XML_OBSERVATION_HEADER_STANDARD_ITEMS') + \
                    metro_config.get_value('XML_OBSERVATION_HEADER_STANDARD_ITEMS')

                # construction du xpath
                sHeader_xpath = metro_config.get_value('XML_OBSERVATION_XPATH_HEADER')
            
                # construction du xpath
                sData_xpath = metro_config.get_value('XML_OBSERVATION_XPATH_MEASURE')
            
                # concatenation de tout les types d'observation
                lStandard_observation = metro_config.get_value( \
                    'XML_OBSERVATION_MEASURE_STANDARD_ITEMS')
                lExtended_observation = metro_config.get_value( \
                    'XML_OBSERVATION_MEASURE_EXTENDED_ITEMS')        

                obs_data = metro_data.Metro_data(lStandard_observation,lExtended_observation)

                observation_data = \
                    self.__extract_data_from_dom(obs_data,
                                                 self.domObservation_ref,
                                                 lHeader_keys,
                                                 sHeader_xpath,
                                                 lStandard_observation,
                                                 lExtended_observation,
                                                 sData_xpath)
            except:
                sXmlError = _("XML error in file '%s'.") % (sFilename)
                raise sXmlError

            # create observation collection
            lObservation_standard_attribute = metro_config.get_value(
                'DATA_ATTRIBUTE_OBSERVATION_STANDARD')
            lObservation_extended_attribute = metro_config.get_value(
                'DATA_ATTRIBUTE_OBSERVATION_EXTENDED')
            lObservation_attribute = lObservation_standard_attribute \
                                     + lObservation_extended_attribute
            observation_ref = \
                metro_data_collection_input.\
                Metro_data_collection_input(observation_data,
                                            lObservation_attribute)

            pObservation_ref.set_data_collection(observation_ref)

        #
        # Extraction des station
        #

        # validate version number
        sFilename = metro_config.get_value('FILE_STATION_FILENAME')
        sFile_version = metro_xml.xpath(self.domStation,"*/version/text()")
        sMin_version = metro_config.get_value('FILE_STATION_MIN_VERSION')
        sMax_version = metro_config.get_value('FILE_STATION_MAX_VERSION')
        self.validate_file_version_number(sFilename, sFile_version,
                                       sMin_version, sMax_version)

        try:
            # concatenation de toutes les cles du header
            lHeader_defs = \
                metro_config.get_value('XML_STATION_HEADER_STANDARD_ITEMS') + \
                metro_config.get_value('XML_STATION_HEADER_EXTENDED_ITEMS')

            # construction du xpath
            sHeader_xpath = metro_config.get_value('XML_STATION_XPATH_HEADER')

            # construction du xpath
            sData_xpath = metro_config.get_value('XML_STATION_XPATH_ROADLAYER')

            # concatenation de tout les section d'un roadlayer
            lStandard_roadlayer = metro_config.get_value( \
                'XML_STATION_ROADLAYER_STANDARD_ITEMS')
            lExtended_roadlayer = metro_config.get_value( \
                'XML_STATION_ROADLAYER_EXTENDED_ITEMS')        

            cs_data = metro_data_station.Metro_data_station(lStandard_roadlayer,lExtended_roadlayer )
            station_data = self.__extract_data_from_dom(cs_data,
                                                        self.domStation,
                                                        lHeader_defs,
                                                        sHeader_xpath,
                                                        lStandard_roadlayer,
                                                        lExtended_roadlayer,
                                                        sData_xpath)

        except:
            sXmlError = _("XML error in file '%s'.") % (sFilename)
            raise sXmlError


        pForecast.set_data_collection(forecast)
        pObservation.set_data_collection(observation)
        pStation.set_data(station_data)


    def stop(self):
        Metro_module.stop(self)
        # Liberation de la memoire utilise par les DOM
        metro_xml.free_dom(self.domForecast)
        metro_xml.free_dom(self.domObservation)
        if self.domObservation_ref != None:
            metro_xml.free_dom(self.domObservation_ref)
        metro_xml.free_dom(self.domStation)

    def get_receive_type(self):
        return Metro_module.DATATYPE_INPUT

    def get_send_type(self):
        return Metro_module.DATATYPE_DATA_IN


    def __extract_data_from_dom(self, metro_data, domDom,
                                ldHeader_keys, sHeader_xpath,
                                lStdData_keys, lExtData_keys,
                                sData_xpath):
        """
        Name: __extract_data_from_dom

        Arguments:  [I] metro_data: Object metro_data that will contain
                                    all the data.
                    [I] domDOM: DOM in which data has to be extracted.
                    [I] ldHeader_keys: List of dictionnaries containing the date
                                       definitions as defined in metro_config.py
                    [I] sHeader_xpath: xpath of the header
                    [I] lStdData_keys: like ldHeader_keys but for standard data
                    [I] lExtData_keys: like ldHeader_keys but for extended data
                    [I] sData_xpath : xpath for the data.

        Output: metro_data : object containing all the data extracted.

        Description: Given a list of tags defined in metro_config,
         this method extract all the values and put them in the object
         returned.
        """
        if ldHeader_keys != None and sHeader_xpath != None:
            
            # extraction des donnes contenue dans les nodes
            lHeader_data = metro_xml.extract_xpath(ldHeader_keys,\
                                                   domDom, sHeader_xpath)

            # ajout des elements dans le dictionnaire du header
            i = 0
            dHeader={}
            for i in range(0,len(ldHeader_keys)):
                dHeader_key = ldHeader_keys[i]
                dHeader[dHeader_key['NAME']] = lHeader_data[i]

            metro_data.set_header(dHeader)

        lData_keys = lStdData_keys + lExtData_keys

        if lData_keys != None and sData_xpath != None:
            # extraction de toute les nodes de mesure contenue dans le DOM
            lData_matrix = metro_xml.extract_xpath(lData_keys, domDom,\
                                                   sData_xpath, True)
            
            # transfert de la matrice dans objet Metro_data
            for lData_row in lData_matrix:
                metro_data.append_matrix_row(lData_row)

        return metro_data

    def validate_file_version_number( self, sFilename, sFile_version,
                                   sMin_version, sMax_version ):
        try:
            metro_util.validate_version_number(sFile_version,
                                            sMin_version,
                                            sMax_version)
        except "VersionErrorLow", sError:
            sMessage =_("An error occured when reading ") +\
                      _("file:\n'%s'.\nThe error is:\n'%s'.") \
                        % (sFilename,sError)
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                       sMessage)
        except "VersionErrorHigh", sError:
            sMessage =_("An error occured when reading ") +\
                      _("file:\n'%s'.\nThe error is:\n'%s'.\n") \
                      % (sFilename,sError) +\
                      _("METRo will try to read the file.") 

            metro_logger.print_message(metro_logger.LOGGER_MSG_CRITICAL,
                                       sMessage)
        except "VersionErrorUndetermined", sError:
            sMessage =_("An error occured when reading ") +\
                      _("file:\n'%s'.\nThe error is:\n'%s'.\n") \
                      % (sFilename,sError) + \
                      _("METRo will try to read the file.") \

            metro_logger.print_message(metro_logger.LOGGER_MSG_CRITICAL,
                                       sMessage) 
