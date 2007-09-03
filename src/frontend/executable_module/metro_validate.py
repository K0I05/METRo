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

"""
Name:          metro_validate.py
Description:   Module that is used to validate the well-formatedness of the XML files.

Author:        Francois Fortin
Date:          2004
"""


from metro_module import Metro_module

import metro_logger
from toolbox import metro_xml
from toolbox import metro_util

_ = metro_util.init_translation('metro_validate')

ERROR_METRO_VALIDATE = "MetroValidateError"

class Metro_validate(Metro_module):

    def __init__(self):
        if self.__class__ is Metro_validate:
            sMessage = _("class %s is a virtual class") % \
                         str(self.__class__)
            raise NotImplementedError(sMessage)

    ##
    # Redefined method
    ##
    def get_receive_type( self ):
        return Metro_module.DATATYPE_INPUT

    def get_send_type( self ):
        return Metro_module.DATATYPE_INPUT

    ##
    # Protected method
    ##

    def _validate( self, sInfdata_tag ):
        if self.infdata_exist(sInfdata_tag):
            pInfdata = self.get_infdata_reference(sInfdata_tag)
            sXml_content = pInfdata.get_input_information()

            if sXml_content != "":
                try:            
                    self.__validate_xml_string(sXml_content)
                except ERROR_METRO_VALIDATE, sError:
                    sMessage = _("Fatal Error when validating %s ") \
                               %(sInfdata_tag) +\
                               _("XML string.\nThe error is:\n%s") \
                                 % (sError)
                    metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                               sMessage)
                else:
                    sMessage = _("%s XML string has been validated") \
                               % (sInfdata_tag)
                    metro_logger.print_message(metro_logger.LOGGER_MSG_INFORMATIVE,
                                               sMessage)
            else:
                sMessage = _("Fatal Error, %s XML string is empty") \
                           % (sInfdata_tag)
                metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                           sMessage)                        
        else:
            sMessage = _("Fatal Error, no %s XML string to validate.") \
                       % (sInfdata_tag)
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                       sMessage)        

    ##
    # Private method
    ##
    
    def __validate_xml_string( self, sXml_content):
        if sXml_content != None:
            try:
                return metro_xml.validate_string(sXml_content)
            except "metroValidationError", sError:
                metro_logger.print_message(metro_logger.LOGGER_MSG_DEBUG,
                                           _("Error when validating ") +\
                                           _("XML string."))
                raise ERROR_METRO_VALIDATE, sError
        else:
            sMessage = _("No XML string to validate")
            metro_logger.print_message(metro_logger.LOGGER_MSG_DEBUG,
                                       sMessage)
            raise ERROR_METRO_VALIDATE, sMessage
