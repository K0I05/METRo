# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
###################################################################################
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
    Name: metro_json

    Description: Serializes a Metro_data object (a roadcast, forecast, etc.)
                 to a plain dict suitable for json.dump(), reusing the same
                 NAME/XML_TAG/DATA_TYPE item definitions from metro_config.py
                 that drive the XML reader/writer, so JSON and XML use the
                 same field names and values.

                 By the time this runs, REAL values are already rounded to
                 their final precision by metro_postprocess_round_roadcast.py,
                 so no rounding is applied here.

                 Limitation: multi-column fields (e.g. TL / subsurface levels,
                 enabled with --output-subsurface-levels) are not supported
                 and are skipped with a warning; everything else standard or
                 extended (RA, SN, RC, ST, GRIP, ...) is supported.
"""

import json
import metro_logger
from toolbox import metro_date
from toolbox import metro_util


_ = metro_util.init_translation('metro_json')


def _convert_value(sData_type, value):
    if sData_type == 'DATE':
        return metro_date.seconds2iso8601(value)
    if sData_type == 'INTEGER':
        return int(value)
    if sData_type == 'REAL':
        return float(value)
    return value


def _header_to_dict(metro_data, lHeader_items):
    dHeader = metro_data.get_header()
    dResult = {}
    for dItem in lHeader_items:
        sName = dItem['NAME']
        if sName not in dHeader:
            continue
        sData_type = dItem['DATA_TYPE']
        # Simple types (STRING/DATE/INTEGER/REAL) get converted; anything else
        # (e.g. VERTICAL_LEVELS, already a plain list) is passed through as-is.
        dResult[dItem['XML_TAG']] = _convert_value(sData_type, dHeader[sName])
    return dResult


def _predictions_to_list(metro_data, lPrediction_items):
    lSingle_items = []
    for dItem in lPrediction_items:
        sName = dItem['NAME']
        if sName not in metro_data.get_matrix_col_list():
            continue
        if metro_data.is_multi_col(sName):
            sMessage = _("metro_json: prediction field '%s' is a multi-value field, ") % dItem['XML_TAG'] + \
                       _("not supported yet, skipping it.")
            metro_logger.print_message(metro_logger.LOGGER_MSG_WARNING, sMessage)
            continue
        lSingle_items.append(dItem)

    dColumns = {dItem['NAME']: metro_data.get_matrix_col(dItem['NAME']) for dItem in lSingle_items}
    nNbr_row = len(next(iter(dColumns.values()))) if dColumns else 0

    lPredictions = []
    for i in range(nNbr_row):
        dRow = {}
        for dItem in lSingle_items:
            dRow[dItem['XML_TAG']] = _convert_value(dItem['DATA_TYPE'], dColumns[dItem['NAME']][i])
        lPredictions.append(dRow)
    return lPredictions


def metro_data_to_dict(metro_data, lHeader_items, lPrediction_items):
    """
        Name: metro_data_to_dict

        Parameters: [I] metro_data : the Metro_data object to serialize (e.g. a roadcast's subsampled data)
                    [I] lHeader_items : list of item definitions (NAME/XML_TAG/DATA_TYPE) for the header
                    [I] lPrediction_items : list of item definitions for each prediction row

        Returns: a plain dict, ready for json.dump()
    """
    return {
        'header': _header_to_dict(metro_data, lHeader_items),
        'prediction-list': _predictions_to_list(metro_data, lPrediction_items)
    }


def write_to_file(sFilename, dData):
    with open(sFilename, 'w') as pFile:
        json.dump(dData, pFile, indent=2)
