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

# # -*- coding:iso-8859-1  -*-

"""
Name:		metro_xml_pyxml
Description:  Wrapper for pyxml library
 
Notes: All these methods should also be implemented in
  metro_xml_libxml2.py

Author: François Fortin
Date: Somewhere in the summer 2004
"""

import sys
import xml.xpath
from xml.dom.ext.reader.Sax import FromXmlFile
from xml.dom.ext.reader.Sax import FromXml
from xml.dom.ext import PrettyPrint
from xml.dom import implementation
from xml.parsers.xmlproc import xmlval
from xml.parsers.xmlproc.xmlapp import ErrorHandler

import metro_logger
from toolbox import metro_util

_ = metro_util.init_translation('metro_xml_pyxml')

# DTD Error handler
class BadOrderErrorHandler(ErrorHandler):
    def warning(self,msg):
        sMessage = _("XML Warning!: %s") % (msg)
        if metro_logger.is_initialised():            
            metro_logger.print_message(metro_logger.LOGGER_MSG_WARNING,
                                       sMessage)
        else:
            metro_logger.print_init_message(metro_logger.LOGGER_INIT_ERROR,
                                            sMessage)

    def error(self,msg):
        sMessage = _("XML Error!: %s") % (msg)
        if metro_logger.is_initialised():            
            metro_logger.print_message(metro_logger.LOGGER_MSG_CRITICAL,
                                       sMessage)
        else:
            metro_logger.print_init_message(metro_logger.LOGGER_INIT_ERROR,
                                            sMessage)

    def fatal(self,msg):
        sMessage = _("XML Fatal Error!: %s") % (msg)
        if metro_logger.is_initialised():            
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP,
                                       sMessage)
        else:
            metro_logger.print_init_message(metro_logger.LOGGER_INIT_ERROR,
                                            sMessage)




class Metro_xml_pyxml:
    
    def start( self ):
        pass
    
    def stop( self ):
        pass

    def get_name( self ):
        return str(self.__class__.__name__)
        
    #------------------
    # lecture d'un DOM
    #------------------
    
    def read_dom( self, sFilename ):
        return  FromXmlFile(sFilename)
    
    def dom_from_string( self, sXml ):
        return FromXml(sXml)
    
    def xpath( self, nodeBranch, sTag ):
        return xml.xpath.Evaluate(sTag,nodeBranch)
    
    def get_node_value( self, node ):
        return node.nodeValue
    
    #------------
    # validation 
    #------------

    def validate_xml_string( self, sXml_content ):
        xv = xmlval.XMLValidator()
        bh = BadOrderErrorHandler(xv.app.locator)
    
        xv.set_error_handler(bh)
        xv.feed(sXml_content)
        
    #------------------
    # creation d'un DOM
    #------------------
    
    def create_dom( self, sDoc_name ):
        doctype = implementation.createDocumentType(sDoc_name, None, None)
        return implementation.createDocument(None, sDoc_name, doctype)
    
    def create_text_node( self, domDoc, sNode_name, sNode_value ):
        nodeTmp = domDoc.createElement(sNode_name)
        nodeTmp.appendChild(domDoc.createTextNode(sNode_value))
        return nodeTmp
    
    def create_node( self, domDoc, sNode_name ):
        return domDoc.createElement(sNode_name)

    def set_attribute( self, node, sAttributeName, sAttributeValue ):
        pass
        # FFTODO code that operation for pyxml
        #node.setProp(sAttributeName,  sAttributeValue)
    
    def append_child( self, nodeParent, nodeChild ):
        nodeParent.appendChild(nodeChild)
    
    def write_xml_file( self, domDoc, sFilename ):
            file = open(sFilename, "w")
            PrettyPrint(domDoc, file)
            file.close()
    
    #------------------
    # autre
    #------------------
    
    def get_dom_root( self, domDoc ):
        return domDoc.documentElement
    
    def free_dom( self, domDoc ):
        pass
    
    #################################
    # Returns all the node of the xpath in a list
    ##########################################
    def get_nodes_in_list(self, dom, sXPath):
        lNode = []
        nodes = self.xpath(dom, sXPath)
        for node in nodes:
            lNode.append(self.get_node_value(node))
        return lNode


