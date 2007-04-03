# -*- coding: iso-8859-15 -*-
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

####################################################
# Name:	 metro_util.py
# Description: Miscelleneous functions for METRo
# Notes: The language is set here because metro can be used
# as a library and metro_util is the module that every other module loads.
# Thus, the language setting that are used through metro is always set if
# this code is in the metro_util module.
####################################################

import os

# set environment variable LANGUAGE and LC_ALL
if 'LANGUAGE' not in os.environ and 'LC_ALL' not in os.environ:
    os.environ['LANGUAGE'] = 'en'
# If language is set, check if its "en" or "fr"
elif 'LANGUAGE' in os.environ:
    if os.environ['LANGUAGE'] != 'en' and os.environ['LANGUAGE'] != 'fr':
        os.environ['LANGUAGE'] = 'en'
elif 'LC_ALL' in os.environ:   
    if os.environ['LC_ALL'] != 'en' and os.environ['LC_ALL'] != 'fr':
        os.environ['LC_ALL'] = 'en'


import sys
import string
import math

from distutils.version import LooseVersion
from gettext import gettext as _
import gettext
import numarray
from numarray import array
from numarray import arange


import arrayfns

# return a module object import from module_path
def import_name( module_path, module_name ):
    try:
        module = __import__(module_path, globals(), locals(), [module_name])
    except ImportError:
        return None
    return vars(module)[module_name]

# Retourne le "path" de la racine du package METRo
def get_metro_root_path( ):
    lPath = string.split(sys.path[0],"/")
    if lPath[len(lPath)-1] == "frontend":
        sRoot_path = string.join(lPath[:-2],"/")
    elif lPath[len(lPath)-1] == "bin":
        sRoot_path = string.join(lPath[:-1],"/")
    elif lPath[len(lPath)-1] == "metro":
        sRoot_path = string.join(lPath[:-3],"/")
        
    else:
        sError = _("The executable 'metro.py' must be in one of the following directory:\n") +\
                 _("metro_directory/src/frontend' or 'metro_directory/usr/lib/metro'.\n") +\
                 _("The following path is not valid: '%s'.\n\n") % (sys.path[0]) +\
                 _("Aborting execution of METRo.\n")
        print sError
        sys.exit(1)
    
    return sRoot_path

def get_exec_root_path( ):
    return sys.path[0]

#########
# Passe pas belle pour pouvoir utiliser la fonction get_metro_root_path
# Ca permet de definir le underscore pour la traduction avec gettext.
#########
t = gettext.translation('metro_util', get_metro_root_path() +\
                        '/usr/share/locale')
_ = t.gettext
    

def test_import( sModule_name ):
    """
    Used to test check if a module is present.
    """
    try:
        sCode = "import " + sModule_name
        exec sCode
    except SyntaxError, sError:
        raise "MetroImportError", sError
    except ImportError, sError:
        raise "MetroImportError", sError
    except EOFError, sError:
        print 'sCode= [%s]' % (sCode)
        raise "MetroImportError", sError

# Utiliser pour tester la presence d'une fonction dans un module
def test_function_existence( sModule_name, sFunction_name ):
    try:
        sCode_import = "import " + sModule_name
        exec sCode_import
        sCode_function = "func_object = " + sModule_name + "." + sFunction_name
        exec sCode_function
        
    except SyntaxError, sError:
        raise "MetroImportError", sError
    except ImportError, sError:
        raise "MetroImportError", sError
    except AttributeError, sError:
        raise "MetroImportError", sError
    
def join_dictionaries(dDict1, dDict2):
    lKeys = dDict1.keys() + dDict2.keys()
    lValues = dDict1.values() + dDict2.values()

    i = 0
    dDict3 = {}
    while i < len(lKeys):
        dDict3[lKeys[i]] = lValues[i]
        i = i + 1

    return dDict3



def list2string( lList ):

    if len(lList) > 0:
        rslt =  str(lList[0])

        for element in lList[1:]:
            rslt = rslt + ", " + str(element)

    else:
        rslt = ""

    return rslt




####################################################
# Name: interpolate
#
# Parameters: [[I] Numeric.Array lXArray : The value of x to
#                   interpolate.  Must be of constant distance between
#                   two consecutives X.]
#              [[I] Numeric.Array lYArray: The value of y to
#                   interpolate.]
#              [[I] int iIncrement: The increment to use
#                    between two X consecutes values to get the new X
#
# Returns: list The interpolate Y value. Throw an exception in case
#  of error.
#
# Functions Called: [interp() see http://wikid.cmc.ec.gc.ca/tiki-index.php?page=Fonction+interp+dans+python]
# #
# Description: This function do the interpolation of a one dimension
#  function.  The x and the corresponding y value are given
#  (i.e. y[n] correspond to x[n]) The value of x must be
#  evenly spaced.
#  The third argument (iIncrement) tells how to
#  increment the value between two consecutive x.
#
# Notes: This function needs the NumArray package. We assume that
#  the values do no need to be sorted (i.e. they are in order).
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay      June 30th 2004   To replace the linear
#                                        interpolation of fortran code
#####################################################

def interpolate(xArray, yArray, iIncrement):
    
    # Check if the size of the array is ok.
    iLenXArray = len(xArray)
    iLenYArray = len(yArray)
    if( iLenXArray != iLenYArray):
        sMetroUtilWarning = _("In interpolate, the arrays does not") +\
                            _("have the same length. %d != %d\n") %\
                              (iLenXArray, iLenYArray )
        print sMetroUtilWarning
        if iLenYArray < iLenXArray:
            sMetroUtilWarning = _("Padding Y array with average at the end.")
            naPadd = numarray.zeros(iLenXArray - iLenYArray)+yArray.mean()
            yArray = numarray.concatenate((yArray,naPadd))
        else:
            raise "METRoUtilError", sMetroUtilWarning
        
    elif(iLenXArray < 2):
        sMetroUtilError = _("In interpolate, the arrays have only one value (1)")
        raise "METRoUtilError", sMetroUtilError
    elif(xArray[1]-xArray[0] < iIncrement):
        sMetroUtilError = _("In interpolate, iIncrement is too big. \n")+\
                          _("Space between two values in xArray:")+\
                          "xArray[0]: %f xArray[1]:%f \n Increment=%f" \
                          % (xArray[0], xArray[1], iIncrement)
        raise "METRoUtilError", sMetroUtilError

    # Build the new x
    xArrayInt = arange(xArray[0],xArray[iLenXArray-1],iIncrement)
    yArrayInt = arrayfns.interp(yArray,xArray, xArrayInt)

    return array(yArrayInt)

####################################################
# Name: shift_left
#
# Parameters: [[I] numarray naInput : The array that the value will be
#              be shifted left]
#             [[I] double fValueAdded=0 : The value to be added at left
#
# Returns: numarray naOutput: The array with the value shifted
#
# Functions Called:  numarray.take
#                    numarray.concatenate
#
# Description: This method shift the value of the array at left, i.e.
#  naInput[n] becomes naInput[n] for all n in [1..len(naInput)-1].  The
#  value fValueAdded is added at the end, i.e. naInput[len(naInput)-1]=fValueAdded
#
# Notes: naInput must be one dimension.
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       July 2nd         Tanne de toujours faire la meme chose
#####################################################
def shift_left(naInput, fValueAdded=0):
    # Check the dimension
    if(naInput.getshape() <= 0):
        sMetroUtilError = _("In shift_left, naInput is not of size (1,).\n")+\
                          "len(naInput.getshape())=%s"\
                          % (len(naInput.getshape()))
        raise "METRoUtilError", sMetroUtilError

    # Cut the first value
    naOutput  = numarray.take(naInput,\
                              numarray.arange(1, len(naInput)))
    naToBeCat = array([fValueAdded])
    naOutput = numarray.concatenate((naOutput, naToBeCat))

    return naOutput


####################################################
# Name: shift_right
#
# Parameters: [[I] numarray naInput : The array that the value will be
#              be shifted right]
#             [[I] double fValueAdded=0 : The value to be added at the
#                beginning of the array
#
# Returns: numarray naOutput: The array with the value shifted
#
# Functions Called:  numarray.take
#                    numarray.concatenate
#
# Description: This method shift the value of the array at right, i.e.
#  naInput[n] becomes naInput[n+1] for all n in [0..len(naInput)-2].  The
#  value fValueAdded is added at the begining, i.e. naInput[0]=fValueAdded
#
# Notes: naInput must be one dimension.
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       July 2nd         Tanne de toujours faire la meme chose
#####################################################
def shift_right(naInput, fValueAdded=0):
    # Check the dimension
    if(naInput.getshape() <= 0):
        sMetroUtilError = _("In shift_right, naInput is not of size (1,).\n")+\
                          "len(naInput.getshape())=%s"\
                          % (len(naInput.getshape()))
        raise "METRoUtilError", sMetroUtilError
    naToBeCat = array([fValueAdded])
    # Cut the trailing value
    naOutput  = numarray.take(naInput,\
                              numarray.arange(0, len(naInput)-1))
    naOutput = numarray.concatenate((naToBeCat, naOutput))

    return naOutput

####################################################
# Name: get_indice_of
#
# Parameters: [[I] numarray naInput : The array to search in.
#             [[I] double fValue : The value to "insert" in the array
#
# Returns: int nIndice : The indice of the array where fValue belongs.
#
# Functions Called:  
#
# Description: The numarray must be ordered.  Returns the indices where
#  naInput[nIndice-1] <= fValue <= naInput[nIndice]
#
# Notes: naInput must be one dimension.
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       July 2nd         Tanne de toujours faire la meme chose
#####################################################
def get_indice_of(naInput, fValue=0):
    if type (naInput) != type(numarray.array([])):
        naInput = numarray.array(naInput)
    if fValue < naInput.min():
        return 0
    elif fValue > naInput.max():
        return len(naInput)
    for i in range(1, len(naInput)):
        if naInput[i-1] <= fValue and fValue <= naInput[i]:
            return i

    sMetroUtilError = _("No indice with this value: %d") %(fValue)
    raise "METRoUtilError", sMetroUtilError

####################################################
# Name: get_difference_array
#
# Parameters: [[I] numarray naInput :
#
# Returns: numarray naOutput : An array storing the difference.
#          bool bPrevious : If True , get the difference
#                            between the indice i and the indice i-1.
#                           If False (default), get the difference between
#                            the indice i and indice i+1.
#          
#
# Functions Called:  
#
# Description: This method compute the difference between consecutive value
#  in a numarrray.
#           naOutput[0] = naInput[1]-naInput[0]
#           naOutput[i] = naInput[1+1]-naInput[i]
#           naOutput[len(naOutput)-1] = naInput[0]-naInput[len(naInput)-1]
#
# Notes: naInput must be one dimension.
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       August 4th 2004     Compute time in observation
#####################################################
def get_difference_array(naInput, bPrevious=False):
    if bPrevious:
        naShiftRight = shift_right(naInput,naInput[len(naInput)-1])
        naOutput = naShiftRight - naInput
        return naOutput
    else:
        naShiftLeft = shift_left(naInput,naInput[0])
        naOutput = naShiftLeft - naInput
        return naOutput

####################################################
# Name: sign
#
# Parameters:   [I double  dResult : 
#               [I double  dSign : 
#
# Returns:  - abs(dResult) if dSign < 0
#           abs(dResult) if dSign > 0
#           
#
# Functions Called:  abs
#
# Description:  See "Returns"
#
# Notes: This is the equivalent of SIGN in fortran.  And no,
#  there is no built-in function that does that.
#  See http://makeashorterlink.com/?D27123029
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       August 24th 2004     
#####################################################
def sign(dResult, dSign):
    # If dSign is == 0, raise an error
    if dSign == 0:
        sMetroUtilError = _("Cannot determine the sign of zero")
        raise sMetroUtilError
    elif dSign > 0:
        return abs(dResult)
    else:
        return -abs(dResult)
    

####################################################
# Name: print_numarray
#
# Parameters:   numarray naToPrint : array to print
#
# Returns:  nothing
#
# Functions Called: 
#
# Description:  Used for debugging purpose.  Prints all the value of a numarray.
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       September 17th 2004     
#####################################################
def print_numarray(naToPrint):
    for i in range(0, len(naToPrint)):
        print "printing", i, naToPrint[i]

####################################################
# Name: subsample
#
# Parameters:   numarray naInput : array to subsample
#               integer nSubsamplingIndice : if == 2, only take one element
#  out of two.
#
# Returns:  numarray naOutput : subsampled array
#
# Functions Called: 
#
# Description:  
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       September 20th 2004     
#####################################################
def subsample(naInput, nSubsamplingIndice):
    # Check if there is an error
    if len(naInput) < nSubsamplingIndice:
        sMetroUtilError = _("In metro_util.subsample, subsampling rate")+\
                          _("is higher than array size: %d > %d") %\
                          (nSubsamplingIndice, len(naInput ))
        raise "METRoUtilError", sMetroUtilError

    # Perform the subsampling
    naSub = numarray.arange(0, len(naInput), nSubsamplingIndice)
    naOutput = numarray.take(naInput, naSub)

    return naOutput

####################################################
# Name: concat_array
#
# Parameters:   numarray naArray1 : array to put in the first column
#               numarray naArray2 : array to put in the second column
#
# Returns:  numarray naConcat : 
#
# Functions Called: numarray.concatenate numarray.setshape
#
# Description: Take two arrays, transform then in column and then form
#  a couple of number in each position.  Usefull to create graphics.
#
#   x = [x1, x2, ..., xn]
#   y = [y1, y2, ..., yn]
#   concat_array(x,y) return [[x1,y1],
#                             [x2,y2],
#                             ...,
#                             [xn,yn]],
#                             
#
# Notes: 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       September 20th 2004     
#####################################################
def concat_array(naArray1, naArray2):
    nLen1 = len(naArray1)
    nLen2 = len(naArray2)
    if nLen2 < nLen1:
        sMetroUtilWarning = _("Array are not of the same size") +\
                            _("cutting the first one")
        print sMetroUtilWarning
        naPadd = numarray.zeros(nLen1 - nLen2)+naArray2.mean()
        naArray2 = numarray.concatenate((naArray2,naPadd))
        nLen2 = nLen1
    elif nLen1 < nLen2:
        sMetroUtilError = _("In metro_util.concat_array, array must be") +\
                          _(" of the same dimension: %d != %d") % \
                          ((nLen1, nLen2))
        raise "METRoUtilError", sMetroUtilError

    # First, rotate the axis
    naArray1.setshape(nLen1,1)
    naArray2.setshape(nLen2,1)

    # Then concatenate
    naConcat = numarray.concatenate((naArray1,naArray2),1)

    return naConcat

####################################################
# Name: cut_indices
#
# Parameters:   numarray naArray : array to be cut
#               float x0 : The minimum from with the left will
#  be cut.
#               float  xn:  The maximum from with the right will
#  be cut.
#
# Returns:  [indiceLeft, indiceRight]
#
# Functions Called: 
#
# Description:  Reduce an array to the value between x0 and xn
#
#
# Notes: Array should be monotone 
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       September 20th 2004     
#####################################################
def cut_indices(naArray, x0, xn):
    nFirstValidIndice = get_indice_of(naArray, x0)
    nLastValidIndice = get_indice_of(naArray, xn)

    lRes = [nFirstValidIndice,nLastValidIndice]
    return lRes

    
def cut(naArray, x0, xn):
    [left,right] = cut_indices(naArray, x0, xn)

    naRes = naArray[left:right]
    return naRes

####################################################
# Name: sum_array
#
# Parameters:   numarray naInput : array to be sum
#
# Returns:   numarray naOutput 
#
# Functions Called: 
#
# Description:  Put the sum of naInput[0:i].sum() in naOuput[i]
#
#
# Notes: Array should be 1-dimension
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       January 18th 2005
#####################################################
def sum_array(naInput):

    naOutput = numarray.array([])

    for i in range(0,len(naInput)):
        naOutput = numarray.concatenate((naOutput, \
                           numarray.array([naInput[0:i].sum()])),1)

    return naOutput


def validate_version_number(sVersion, sMin_version, sMax_version ):

    min_version = LooseVersion(sMin_version)
    max_version = LooseVersion(sMax_version)

    
    if sVersion != None:
        version = LooseVersion(sVersion)
        
        if version < min_version:
            sMessage = _("Version number:'%s' is too old. Version from '%s' ")\
                       % (version, min_version) +\
                       _("to '%s' inclusively are supported") \
                       % (max_version)
            raise "VersionErrorLow", sMessage
                
        elif version > max_version:
            sMessage = _("Version number:'%s' is not yet supported. Version ")\
                       % (version) +\
                       _("from '%s' to '%s' inclusively are supported") \
                       % (min_version,max_version)
            raise "VersionErrorHigh", sMessage
    else:
        sMessage = _("Can't find version number. Version from '%s' ") \
                   % (min_version) +\
                   _("to '%s' inclusively are supported") \
                   % (max_version)
        raise "VersionErrorUndetermined", sMessage

####################################################
# Name: init_translation
#
# Parameters:   string sFilename :
#
#
# Returns:  _
#
# Functions Called: gettext.translation
#
# Description:  Indication which file should be use for translation.
#
#
# Notes:
#
# Revision History:
#  Author		Date		Reason
# Miguel Tremblay       November 8th 2004     
#####################################################
def init_translation(sFilename):
    t = gettext.translation(sFilename, get_metro_root_path() +\
                            '/usr/share/locale')
    _t_ = t.gettext

    return _t_


