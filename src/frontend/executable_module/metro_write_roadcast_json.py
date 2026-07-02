# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
##################################################################################
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
    Name: Metro_write_roadcast_json

    Description: Optional JSON roadcast writer, alongside the XML one. Only
                 writes a file if --output-roadcast-json=<file> was given.
                 Reads straight from the roadcast's Metro_data (the same
                 subsampled/rounded data metro_metro2dom.py turns into XML),
                 independently of the XML DOM, so this cannot affect the
                 existing XML output path.
"""

from executable_module.metro_write import Metro_write
import metro_config
import metro_logger
from toolbox import metro_json
from toolbox import metro_util


_ = metro_util.init_translation('metro_write_roadcast_json')


class Metro_write_roadcast_json(Metro_write):

    def start(self):
        Metro_write.start(self)
        sFilename = metro_config.get_value('FILE_ROADCAST_JSON_FILENAME')
        if sFilename == "":
            return

        pRoadcast = self.get_infdata_reference('ROADCAST')
        roadcast_data = pRoadcast.get_data_collection()
        if roadcast_data is None:
            metro_logger.print_message(metro_logger.LOGGER_MSG_WARNING, _("no roadcast, nothing to write in JSON"))
            return

        lHeader_items = metro_config.get_value('XML_ROADCAST_HEADER_STANDARD_ITEMS') + \
                        metro_config.get_value('XML_ROADCAST_HEADER_EXTENDED_ITEMS')
        lPrediction_items = metro_config.get_value('XML_ROADCAST_PREDICTION_STANDARD_ITEMS') + \
                            metro_config.get_value('XML_ROADCAST_PREDICTION_EXTENDED_ITEMS')

        dRoadcast = metro_json.metro_data_to_dict(roadcast_data.get_subsampled_data(), lHeader_items,
                                                  lPrediction_items)
        try:
            sMessage = _("start writing file:'%s'") % sFilename
            metro_logger.print_message(metro_logger.LOGGER_MSG_DEBUG, sMessage)
            metro_json.write_to_file(sFilename, dRoadcast)
        except IOError as inst:
            sMessage = _("An error occured when writing JSON file: '%s'\n%s") % (sFilename, str(inst))
            metro_logger.print_message(metro_logger.LOGGER_MSG_CRITICAL, sMessage)
        else:
            sMessage = _("JSON file: '%s' written with success") % sFilename
            metro_logger.print_message(metro_logger.LOGGER_MSG_INFORMATIVE, sMessage)

    def stop(self):
        Metro_write.stop(self)
