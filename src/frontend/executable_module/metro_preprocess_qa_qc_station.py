# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
# Code contributed by:
#  Miguel Tremblay - Canadian meteorological center
#  Francois Fortin - Canadian meteorological center
#
#  $LastChangedDate$
#  $LastChangedRevision$
################################################################################
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


"""
    Name:	       Metro_preprocess_qa_qc_station

    Description: QA and QC for the station file is made here.

    Notes:

    Auteur: Miguel Tremblay

    Date: September 30 2014
"""


from executable_module.metro_preprocess import Metro_preprocess
import metro_config
import metro_logger
import metro_error
import numpy
from toolbox import metro_util


_ = metro_util.init_translation('metro_preprocess_qa_qc_station')


class Metro_preprocess_qa_qc_station(Metro_preprocess):

    def start(self):
        Metro_preprocess.start(self)

        try:
            Metro_preprocess.start(self)
            pStation = self.get_infdata_reference('STATION')
            self.__check_custom_roadlayer(pStation)
            if self.infdata_exist('HORIZON'):
                self.__check_sunshadow(pStation)
        except metro_error.Metro_data_error as inst:
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, str(inst))

    # Capacity (J/m3/K) and conductivity (W/m/K) bounds for 'CUSTOM' road layers.
    # METRo's finite-difference ground grid (grille.f) is a fixed-size, unbounded-checked
    # array (nNGRILLEMAX) tuned for the 4 built-in materials (capacity ~2.0-2.1e6,
    # conductivity ~0.8-2.2). Values far outside that range make the grid numerically
    # unstable and crash the compiled physics core (segfault) instead of failing
    # gracefully. These bounds were determined empirically and comfortably contain the
    # built-in materials while allowing genuinely different ones (e.g. wood, brick).
    fCUSTOM_CAPACITY_MIN = 1.0e6
    fCUSTOM_CAPACITY_MAX = 1.0e7
    fCUSTOM_CONDUCTIVITY_MIN = 0.05
    fCUSTOM_CONDUCTIVITY_MAX = 3.5

    def __check_custom_roadlayer(self, pStation):
        """
            Description: A road layer of type 'CUSTOM' must have a valid
                         <capacity> and <conductivity> given in the station
                         configuration file, within a range that keeps METRo's
                         ground grid numerically stable (see the class-level
                         fCUSTOM_* bounds above for why).
                         See https://framagit.org/metroprojects/metro/wikis/Layer_type_(METRo)
        """
        cs_data = pStation.get_data()
        nCustom_type = metro_config.get_value('ROADLAYER_TYPE_CUSTOM')
        npType = cs_data.get_matrix_col('TYPE')
        npCapacity = cs_data.get_matrix_col('CAPACITY')
        npConductivity = cs_data.get_matrix_col('CONDUCTIVITY')

        for i in range(len(npType)):
            if npType[i] == nCustom_type:
                bMissing_capacity = numpy.isnan(npCapacity[i]) or npCapacity[i] <= 0
                bMissing_conductivity = numpy.isnan(npConductivity[i]) or npConductivity[i] <= 0
                if bMissing_capacity or bMissing_conductivity:
                    sMessage = _("Road layer #%d is of type 'CUSTOM' but is missing a valid ") % (i + 1) + \
                               _("(positive) <capacity> and/or <conductivity> value in the ") + \
                               _("station configuration file.")
                    metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)
                elif not (self.fCUSTOM_CAPACITY_MIN <= npCapacity[i] <= self.fCUSTOM_CAPACITY_MAX):
                    sMessage = _("Road layer #%d has a <capacity> of %s J/m3/K, outside the ") % \
                               (i + 1, str(npCapacity[i])) + \
                               _("supported range [%s, %s]. Values outside this range make ") % \
                               (str(self.fCUSTOM_CAPACITY_MIN), str(self.fCUSTOM_CAPACITY_MAX)) + \
                               _("METRo's ground grid numerically unstable.")
                    metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)
                elif not (self.fCUSTOM_CONDUCTIVITY_MIN <= npConductivity[i] <= self.fCUSTOM_CONDUCTIVITY_MAX):
                    sMessage = _("Road layer #%d has a <conductivity> of %s W/m/K, outside the ") % \
                               (i + 1, str(npConductivity[i])) + \
                               _("supported range [%s, %s]. Values outside this range make ") % \
                               (str(self.fCUSTOM_CONDUCTIVITY_MIN), str(self.fCUSTOM_CONDUCTIVITY_MAX)) + \
                               _("METRo's ground grid numerically unstable.")
                    metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)

        # Layers that are not 'CUSTOM' don't use these values; replace any
        # missing (NaN) value with 0.0 so downstream code only deals with floats.
        npCapacity = numpy.nan_to_num(npCapacity, nan=0.0)
        npConductivity = numpy.nan_to_num(npConductivity, nan=0.0)
        cs_data.set_matrix_col('CAPACITY', npCapacity)
        cs_data.set_matrix_col('CONDUCTIVITY', npConductivity)
        pStation.set_data(cs_data)

    def __check_sunshadow(self, station_data):
        """
            Check if all the condidations for the sun-shadow algorithm are met.
            1- Presence of the data in station config file;
            2- The last value of the azimuth is 360.
        """
        pHorizon = self.get_infdata_reference('HORIZON')
        horizon_data = pHorizon.get_data()

        # Is there the <azimuth> data in the station file?
        if horizon_data is None:
            sMessage = _("Option --enable-sunshadow is given but there is no ") + \
                       _("azimuth data in station configuration file.\n ") + \
                       _("Please correct this or remove the option --enable-sunshadow")
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage).Metro_util_error(sMessage)
        npAzim = horizon_data.get_matrix_col('AZIMUTH')
        npElev = horizon_data.get_matrix_col('ELEVATION')

        # Verification if the array has an monotone and regular incrementation steps
        if not metro_util.is_array_uniform(npAzim):
            sMessage = _("Azimuth data in station configuration file ") + \
                       _("is not ordered by equal growing azimuths.\n ") + \
                       _("Please correct this or remove the option --enable-sunshadow")
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage).Metro_util_error(sMessage)

        # Check if the first item is zero degree and the last 360
        if npAzim[0] != 0 and npAzim[-1] != 360:
            sMessage = _("Azimuth data does not have a value at 0 and/or 360 degrees. ") + \
                       _("Please add one of this value to have a complete horizon.\n ")
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage).Metro_util_error(sMessage)
        elif npAzim[0] == 0 and npAzim[-1] != 360:
            horizon_data.append_matrix_row([360.0, npElev[0]])
