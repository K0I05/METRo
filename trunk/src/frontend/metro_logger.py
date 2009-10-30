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

import time
import sys
import string

import metro_config
from toolbox import metro_date
from toolbox import metro_util

_ = metro_util.init_translation('metro_logger')

#===============================================================================
#
# Nom:         metro_logger
#
# Auteur:      Francois Fortin
#
# Date:        30/03/2004
#
# Description: Module permettant de centraliser l'ecriture des messages d'erreur
#              de METRo. Le logger a different niveau de verbositer:
#
# TODO:
#
#===============================================================================

# niveau de verbositer du logger
LOGGER_VERBOSE_LEVEL_NOLOG   = 9999 # setting special pour desactiver le logger
LOGGER_VERBOSE_LEVEL_MINIMAL = 20
LOGGER_VERBOSE_LEVEL_NORMAL  = 10
LOGGER_VERBOSE_LEVEL_FULL    = 5
LOGGER_VERBOSE_LEVEL_DEBUG   = 0

iLogger_verbose_level = LOGGER_VERBOSE_LEVEL_NOLOG 

# categorie du message
LOGGER_MSG_DEBUG         = 1   # afficher si verbositer = DEBUG
LOGGER_MSG_INFORMATIVE   = 6   # afficher si verbositer = FULL
LOGGER_MSG_EXECSECONDARY = 2   # afficher si verbositer = FULL
LOGGER_MSG_WARNING       = 11  # afficher si verbositer = ( FULL || NORMAL )
LOGGER_MSG_EXECPRIMARY   = 12  # afficher si verbositer = ( FULL || NORMAL )
LOGGER_MSG_CRITICAL      = 21  # toujours affiche
LOGGER_MSG_STOP          = 22  # toujours affiche

LOGGER_MSG_DEBUG_TXTID         = _("DEBUG      ")
LOGGER_MSG_INFORMATIVE_TXTID   = _("INFORMATIVE")
LOGGER_MSG_EXECSECONDARY_TXTID = _("EXECUTION  ")
LOGGER_MSG_WARNING_TXTID       = _("WARNING    ")
LOGGER_MSG_EXECPRIMARY_TXTID   = _("EXECUTION  ")
LOGGER_MSG_CRITICAL_TXTID      = _("CRITICAL   ")
LOGGER_MSG_STOP_TXTID          = _("STOP       ")
LOGGER_MSG_UNDEFINED_TXTID     = _("UNDEFINED  ")
LOGGER_MSG_EMPTY_TXTID         = "             "
# Condition pour qu'un message soit affiche:
# categorie du message > niveau de verbositer du logger

# Type de message pour les message imprimer avant la
# fin de l'initialisation de METRo
LOGGER_INIT_MESSAGE = 0
LOGGER_INIT_SUCCESS = 1
LOGGER_INIT_ERROR   = 2
LOGGER_INIT_BLANK   = 3



bIs_initialised = False

#-------------------------------------------------------------------------------
#
# Nom:          write_log_header
#
# Parametres:   I fLog_file  : fichier de log
#               I iVerbosity : niveau de verbosite
#
# Retourne:     aucun
#
# Descriptions: Ecriture d'un header pour une nouvelle session de log.
#               Le header comprend:
#               le numero de version de metro,
#               l'heure de demarrage,
#               l'instruction complete pour lancer metro,
#               niveau de verbosite du logger
#
#
#-------------------------------------------------------------------------------
def write_log_header( fLog_file, iVerbosity ):
    fLog_file.write("\n\n============================================\n")

    fLog_file.write(_("METRo version   : "))
    fLog_file.write(metro_config.get_metro_version())
    fLog_file.write("\n")

    line = _("METRo started   : %s %s") \
           % (time.asctime(time.localtime(time.time())),
              metro_date.get_system_tz())
    fLog_file.write(line)
    fLog_file.write("\n")

    fLog_file.write(_("command line    : "))
    fLog_file.write(string.join(sys.argv,' '))
    fLog_file.write("\n")

    fLog_file.write(_("logger verbosity: "))
    if iVerbosity == LOGGER_VERBOSE_LEVEL_NOLOG:
        fLog_file.write(_("No Log"))
    elif iVerbosity == LOGGER_VERBOSE_LEVEL_MINIMAL:
        fLog_file.write(_("Minimal"))
    elif iVerbosity == LOGGER_VERBOSE_LEVEL_NORMAL:
        fLog_file.write(_("Normal"))
    elif iVerbosity == LOGGER_VERBOSE_LEVEL_FULL:
        fLog_file.write(_("Full"))
    elif iVerbosity == LOGGER_VERBOSE_LEVEL_DEBUG:
        fLog_file.write(_("Debug"))
    else:
        fLog_file.write(_("Undefined"))
    fLog_file.write("\n")

    fLog_file.write("\n============================================\n")

#-------------------------------------------------------------------------------
#
# Nom:          init
#
# Parametres:   aucun
#
# Retourne:     aucun
#
# Descriptions: Initialisation du niveau de verbosite du logger
#
#-------------------------------------------------------------------------------
def init( ):
    global iLogger_verbose_level
    global bLogger_shell_display
    global sLogger_filename
    global fLogger_file
    global bIs_initialised

    #pre initialisation pour que l'initialisation du log ne soit pas logge
    iLogger_verbose_level     = LOGGER_VERBOSE_LEVEL_NOLOG
    bLogger_shell_display     = False

    sMessage = _("Starting METRo logger")
    print_init_message(LOGGER_INIT_MESSAGE,sMessage)

    #recuperer les valeurs de configuration
    sTmp_logger_filename      = metro_config.get_value("FILE_LOGGER_FILENAME")
    iTmp_logger_verbose_level = \
        metro_config.get_value("INIT_LOGGER_VERBOSE_LEVEL")
    bTmp_logger_shell_display = \
        metro_config.get_value("INIT_LOGGER_SHELL_DISPLAY")

    #initialisation
    sLogger_filename      = sTmp_logger_filename
    iLogger_verbose_level = iTmp_logger_verbose_level
    bLogger_shell_display = bTmp_logger_shell_display

    #ouverture du fichier log
    try:
        fLogger_file = open(sLogger_filename,'a')
    except IOError:
        fLogger_file = None
        sError_message = _("can't open/create logger file:'%s'") \
                         % (sLogger_filename)
        print_init_message(LOGGER_INIT_ERROR,
                           sError_message)
    else:
        #ecrire le header du log
        write_log_header(fLogger_file, iLogger_verbose_level)
        
        sSuccess_message = _("METRo logger started, log file:'%s'") \
                           % (sLogger_filename)
        print_init_message(LOGGER_INIT_SUCCESS,
                           sSuccess_message)

    bIs_initialised = True

        



#-------------------------------------------------------------------------------
#
# Nom:          stop
#
# Parametres:   aucun
#
# Retourne:     aucun
#
# Descriptions: Fermeture du loggger
#
#-------------------------------------------------------------------------------
def stop():
    if fLogger_file:
        fLogger_file.close()

#-------------------------------------------------------------------------------
#
# Nom:          print_message
#
# Parametres:   I iMessage_category : categorie du message
#               I sMessage          : message
#
# Retourne:     aucun
#
# Descriptions: sauvegarde d'un message dans le fichier log. Un message est
#               sauvegarde seulement si sont niveau de gravite est superieur
#               au niveau de verbosite du logger. De facon optionnel, le message
#               peut etre aussi affiche dans le shell.
#
#-------------------------------------------------------------------------------
def print_message( iMessage_category, sMessage ):

    # determiner l'identifiant texte de la categorie de message
    if iMessage_category == LOGGER_MSG_DEBUG:
        sMessage_category_string = LOGGER_MSG_DEBUG_TXTID
    elif iMessage_category == LOGGER_MSG_INFORMATIVE:
        sMessage_category_string = LOGGER_MSG_INFORMATIVE_TXTID
    elif iMessage_category == LOGGER_MSG_EXECSECONDARY:
        sMessage_category_string = LOGGER_MSG_EXECSECONDARY_TXTID
    elif iMessage_category == LOGGER_MSG_WARNING:
        sMessage_category_string = LOGGER_MSG_WARNING_TXTID
    elif iMessage_category == LOGGER_MSG_EXECPRIMARY:
        sMessage_category_string = LOGGER_MSG_EXECPRIMARY_TXTID
    elif iMessage_category == LOGGER_MSG_CRITICAL:
        sMessage_category_string = LOGGER_MSG_CRITICAL_TXTID
    elif iMessage_category == LOGGER_MSG_STOP:
        sMessage_category_string = LOGGER_MSG_STOP_TXTID
    else:
        sMessage_category_string = LOGGER_MSG_UNDEFINED_TXTID


    # controle si le message doit etre "logge"
    if iMessage_category > iLogger_verbose_level:

        #Ajustement des newline pour que le texte dans le fichier soit
        #aligne correctement
        sMessage = string.replace(sMessage,
                                  "\n",
                                  "\n" + LOGGER_MSG_EMPTY_TXTID)

        if fLogger_file:
            try:
                fLogger_file.write(sMessage_category_string + ": "+ sMessage + '\n')
            except:
                sLine = _("%s unexpected error, can't write message in the log file: %s") \
                        % (LOGGER_MSG_CRITICAL_TXTID,sLogger_filename)
                print sLine

        # controle si le message doit etre afficher dans le shell
        if bLogger_shell_display == True:
            print (sMessage_category_string + ": " + sMessage).encode('ISO-8859-1')

    # si une erreur necessitant l'arret du programme se produit,
    # il faut avertir l'usager
    if iMessage_category == LOGGER_MSG_STOP:
        print "\n\n------------------------------------------------------------------------"
        print _("An unrecoverable error has occured, see details in the log file: ")
        print sLogger_filename.encode('ISO-8859-1')

        if iLogger_verbose_level != LOGGER_VERBOSE_LEVEL_FULL:
            print "\n"
            print _("Lauching METRo with full logging capability may help you trace the error.")

        print "-------------------------------------------------------------------------"
        sys.exit(1)

def print_blank_line(iMessage_category):
     # controle si le message doit etre "logge"
    if iMessage_category > iLogger_verbose_level:
        if fLogger_file:
            fLogger_file.write("\n")

        # controle si le message doit etre afficher dans le shell
        if bLogger_shell_display == True:
            print ""

# Cette fonction imprime le message seulemement a l'ecran
def print_init_message( iType, sMessage="" ):

    if iType == LOGGER_INIT_ERROR:
        sMessage_leading_id = "[!!] "
    elif iType == LOGGER_INIT_SUCCESS:
        sMessage_leading_id = "[ok] "
    elif iType == LOGGER_INIT_MESSAGE:
        sMessage_leading_id = "* "
    elif iType == LOGGER_INIT_BLANK:
        sMessage_leading_id = ""
    else:
        sMessage_leading_id = ""
        
    sMessage = string.replace(sMessage,
                              "\n",
                              "\n" + "     ")

    print (sMessage_leading_id + sMessage)


def is_initialised( ):
    return bIs_initialised

