# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
# Code contributed by:
#  Francois Fortin - Canadian meteorological center
#  Sasa Zhang - Canadian meteorological center
#
#  $LastChangedDate$
#  $LastChangedRevision$
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
    This test_suit.py file runs the test suite that comes with the METRo program
"""

import argparse
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

num_of_success = 0
num_of_failure = 0
list_of_failure_cases = []
list_of_missing_file_cases = []
dict_error = {}
list_of_errors = []
error_difference = 0
forecast_exists = False
station_exists = False
observation_exists = False
json_exists = False
reference_exists = False


# -------------------------------------Class definition: XmlTree--------------------------------------------------------
class XmlTree:
    sum_of_error_outside_tolerance = 0
    sum_of_error_within_tolerance = 0
    list_of_diff_case = []
    display_info = True

    def __init__(self, error_value=0.01):
        self._error = error_value

    def get_error(self):
        return self._error

    def set_error(self, error_value):
        self._error = error_value

    @staticmethod
    def convert_string_to_tree(xml_file):
        """
            Convert an XML file into a tree
            :param xml_file: the name of the file that is going to be converted
            :return: the tree which is converted from the 'xml_file'
        """
        return (ET.parse(xml_file)).getroot()

    def text_compare(self, text1, text2):
        """
            Compare two text strings
            :param text1: text one
            :param text2: text two
            :return: True if these two text strings are a match
        """
        if not text1 and not text2:
            return True
        if text1 == '*' or text2 == '*':
            return True
        return (text1 or '').strip() == (text2 or '').strip()

    def xml_compare(self, xml_file1, xml_file2, excludes=None, display_info=True):
        """
            Compare two xml trees
            :param display_info: boolean variable to indicate if the program display all the different value of tags
            :param xml_file1: the first tree from xml_file1
            :param xml_file2: the second tree from xml_file2
            :param excludes: list of attributes to exclude from comparison
            :return: True if both files match with each other
        """
        global dict_error
        global list_of_errors
        global error_difference

        if excludes is None:
            excludes = []

        if xml_file1.tag != xml_file2.tag:
            if display_info:
                print('Tags do not match: {} and {}.'.format(xml_file1.tag, xml_file2.tag))
            return False

        for name, value in xml_file1.attrib.items():
            if name not in excludes:
                if xml_file2.attrib.get(name) != value:
                    if display_info:
                        print('Attributes do not match: {}={} and {}={}.'.format(name, value, name,
                                                                                 xml_file2.attrib.get(name)))
                    return False

        for name in xml_file2.attrib.keys():
            if name not in excludes:
                if name not in xml_file1.attrib:
                    if display_info:
                        print('xml_file2 has an attribute xml_file1 is missing: {}.'.format(name))
                    return False

        if not self.text_compare(xml_file1.text, xml_file2.text):
            if abs(float(xml_file1.text) - float(xml_file2.text)) - self.get_error() <= 0.00000001:
                XmlTree.sum_of_error_within_tolerance += 1

            elif abs(float(xml_file1.text) - float(xml_file2.text)) - self.get_error() > 0.00000001:
                XmlTree.sum_of_error_outside_tolerance += 1
                if display_info:
                    if XmlTree.sum_of_error_outside_tolerance == 1:
                        print("\nroadcast_reference.xml            roadcast_test_suite_run.xml"
                              "\n----------------------            ---------------------------")
                    tag_reference = '<' + xml_file1.tag + '>' + xml_file1.text + '<' + xml_file1.tag + '>'
                    tag_test_suite_run = '<' + xml_file2.tag + '>' + xml_file2.text + '<' + xml_file2.tag + '>'
                    print("{}{}{}".format(tag_reference.ljust(24), '!='.ljust(10), tag_test_suite_run))

                    abs_error_difference = abs(float(xml_file1.text) - float(xml_file2.text))

                    if xml_file1.tag not in dict_error.keys():
                        if abs(abs_error_difference - error_difference) <= 0.00000001:
                            dict_error[xml_file1.tag] = []
                            dict_error[xml_file1.tag].append([float(xml_file1.text), float(xml_file2.text)])
                        elif abs_error_difference - error_difference > 0.00000001:
                            dict_error.clear()
                            dict_error[xml_file1.tag] = []
                            dict_error[xml_file1.tag].append([float(xml_file1.text), float(xml_file2.text)])
                            error_difference = abs_error_difference

                    elif xml_file1.tag in dict_error.keys():
                        if abs(abs_error_difference - error_difference) <= 0.00000001:
                            list_of_errors = [float(xml_file1.text), float(xml_file2.text)]
                            dict_error[xml_file1.tag].append(list_of_errors)
                        elif abs_error_difference - error_difference > 0.00000001:
                            dict_error.clear()
                            dict_error[xml_file1.tag] = []
                            dict_error[xml_file1.tag].append([float(xml_file1.text), float(xml_file2.text)])
                            error_difference = abs_error_difference
            return False

        if not self.text_compare(xml_file1.tail, xml_file2.tail):
            if display_info:
                print('tail: {} != {}.'.format(xml_file1.tail, xml_file2.tail))
            return False

        child1 = list(xml_file1)
        child2 = list(xml_file2)
        if len(child1) != len(child2):
            if display_info:
                print('children length differs, {} != {}.'.format(len(child1), len(child2)))
            return False

        for c1, c2 in zip(child1, child2):
            if c1.tag not in excludes:
                if not self.xml_compare(c1, c2, excludes, display_info):
                    pass
        return True


# -----------------------------------------Method definition------------------------------------------------------------
def process_case_name(case_string, case_list=None):
    """
        Process the case name(s) that is/are passed by the command line.
        :param case_string: case number entered by the user through command line
        :param case_list: a case list including all case number entered by the user
        :return: a validated case list for further process
    """
    if case_list is None:
        case_list = []
    for case in case_string:
        if case.startswith('case'):
            case = case[4:]
        case = case.zfill(3)
        case = 'case' + case
        if case not in case_list:
            case_list.append(case)
    return case_list


def process_test_result(case_folder, test_code, expected_value_json, verbosity=False):
    """
        Processes the running result(s) of the test suite
        :param verbosity: indicate the willingness of the user having the info displayed in detail
        :param case_folder: case name which is being tested
        :param test_code: code returned by the program after done running the case
        :param expected_value_json: predefined value inside 'config.jason' file
        :return: case running result
    """
    global num_of_success, num_of_failure, list_of_failure_cases
    global forecast_exists, station_exists, observation_exists, json_exists, reference_exists

    if (test_code == 0 and expected_value_json == 'SUCCESS' and XmlTree.sum_of_error_outside_tolerance == 0) \
            or (test_code != 0 and expected_value_json == 'FAILURE'):
        num_of_success += 1
        print(case_folder, ' SUCCESS!')
        if (not reference_exists or not json_exists) and verbosity:
            print()
            if not reference_exists:
                print("Note: 'roadcast_reference' file does not exist for {}".format(case_folder))
            if not json_exists:
                print("Note: 'config.json' file does not exist for {}".format(case_folder))

    elif (test_code != 0 and expected_value_json == 'SUCCESS') or \
            (test_code == 0 and expected_value_json == 'FAILURE') or \
            (test_code == 0 and (expected_value_json == 'SUCCESS' or expected_value_json == '')
             and XmlTree.sum_of_error_outside_tolerance > 0) or \
            ((not forecast_exists or not station_exists or not observation_exists) and not json_exists):
        num_of_failure += 1
        list_of_failure_cases.append(case_folder)
        if verbosity:
            print('The exit code of METRo is: {}\n'.format(test_code))
        print(case_folder, ' FAILURE! ***')

        if (not reference_exists or not json_exists) and verbosity:
            print()
            if not reference_exists:
                print("Note: 'roadcast_reference' file does not exist for {}".format(case_folder))
            if not json_exists:
                print("Note: 'config.json' file does not exist for {}".format(case_folder))
    else:
        print('Something went wrong with this test run, please try to restart it again!')


def process_xml_file(current_case_path, case_folder, error_value, verbosity=False):
    """
        Compares the output XML file with the given benchmark XML file
        :param current_case_path: directory of the current case that is going to be compared
        :param case_folder: case number that is being compared
        :param error_value: defined error tolerance for the running case
        :param verbosity: boolean variable to indicate the willingness of display the comparison result in detail
        :return: comparison result
    """
    global dict_error
    global list_of_errors
    global error_difference
    global reference_exists

    os.chdir(current_case_path)
    XmlTree.sum_of_error_within_tolerance = 0
    XmlTree.sum_of_error_outside_tolerance = 0
    comparator = XmlTree(error_value)
    if verbosity:
        XmlTree.display_info = True
    elif not verbosity:
        XmlTree.display_info = False

    try:
        tree1 = XmlTree.convert_string_to_tree('roadcast_reference.xml')
        tree2 = XmlTree.convert_string_to_tree('roadcast_test_suite_run.xml')

        dict_error = {}
        list_of_errors = []
        error_difference = 0.0

        if comparator.xml_compare(tree1, tree2, ['production-date'],
                                  XmlTree.display_info) and XmlTree.sum_of_error_outside_tolerance == 0:
            if reference_exists and verbosity:
                print('\nXML FILES COMPARISON RESULT: \t', end='')
                print('  {} differences within the predefined error tolerance.\n'.
                      format(XmlTree.sum_of_error_within_tolerance))
        elif XmlTree.sum_of_error_outside_tolerance != 0:
            XmlTree.list_of_diff_case.append(case_folder)
            if reference_exists and verbosity:
                print('\nXML FILES COMPARISON RESULT: ', end='')
                print('\t  {} differences within the predefined error tolerance.'
                      .format(str(XmlTree.sum_of_error_within_tolerance).rjust(4)))
                print('                             \t  {} differences outside the predefined error tolerance.\n'
                      .format(str(XmlTree.sum_of_error_outside_tolerance).rjust(4)))
                print('The largest error difference is:              {}\n'.format(round(error_difference, 2)))
                print('The largest error difference exists in:       ', end='')
                print('roadcast_reference.xml'
                      '         roadcast_test_suite.xml')
                print('                                              ----------------------'
                      '         -----------------------')
                for key, values in dict_error.items():
                    for value in values:
                        error_reference = '<' + key + '>' + str(value[0]) + '<' + key + '>'
                        error_test_suite_run = '<' + key + '>' + str(value[1]) + '<' + key + '>'
                        print('\t\t\t\t\t\t{}\t\t{}'.format(error_reference.ljust(20), error_test_suite_run.ljust(20)))
    except IOError:
        pass


# ---------------------------------------Method: main()-----------------------------------------------------------------
def main():
    # ----------------------------------------Process user's input from command line------------------------------------
    case_name = ''
    default_error_tolerance = 0.01

    parser = argparse.ArgumentParser(description='run the test suite')
    parser.add_argument('-c', '--case', nargs='+', default=[], metavar='', help='add case number(s) to a case list')
    parser.add_argument('-s', '--skip', nargs='+', default=[], metavar='',
                        help='add case number(s) to a do-not-run case list')
    parser.add_argument('-v', '--verbose', action='store_true', help='display the process in a complete detailed way')
    parser.add_argument('-e', '--error', type=float, help='specified value of error tolerance')
    parser.add_argument('--clean', action='store_true', help="clean up output XML file 'roadcast_test_suite_run.xml'")
    args = parser.parse_args()

    if args.verbose:
        verbosity = True
    else:
        verbosity = False

    if args.case or args.skip:
        if args.case and args.skip:
            print("'-c' and '-s' cannot be used at the same time. The METRo program will exit with code 2.")
            sys.exit(2)
        run_all_cases = False
    else:
        case_name = 'case'
        run_all_cases = True

    if args.error:
        error_value = args.error
    else:
        error_value = default_error_tolerance

    num_of_folders = 0
    list_of_folders = []
    list_of_wrong_folders = []
    test_suite_path = os.getcwd()
    num_of_clean_up = 0
    # -------------------------------------------Clean up the output XML file-------------------------------------------
    if args.clean:
        if args.case or args.skip or args.error:
            print("'--clean' can only be used with '-v'.")
            sys.exit(0)

        for folder in sorted(os.listdir(test_suite_path)):
            if folder.startswith('case'):
                try:
                    os.remove(test_suite_path + '/' + folder + '/roadcast_test_suite_run.xml')
                    num_of_clean_up += 1
                    if  verbosity:
                        if num_of_clean_up == 1:
                            print('File(s) that are successfully removed:')
                        print(test_suite_path + '/' + folder + '/roadcast_test_suite_run.xml')
                except IOError as e:
                    continue
        if num_of_clean_up == 0:
            print('There is nothing needs to be cleaned up.')
        else:
            if not verbosity:
                print("All 'roadcast_test_suite_run.xml' files are cleaned up.")
        sys.exit(0)

    # --------------------------------------------List of validated test cases------------------------------------------
    if verbosity:
        print('\n\n================================================================================')
        print('\n', '                         ', 'VALIDATED LIST OF TEST CASES: ')
        print('\n================================================================================')

    if args.case:
        case_list = process_case_name(args.case, case_list=None)
    else:
        case_list = []

    if args.skip:
        do_not_run_case_list = process_case_name(args.skip, case_list=None)
    else:
        do_not_run_case_list = []

    if do_not_run_case_list and not case_list:
        list_of_folders = []
        case_name = 'case'
        for folder in sorted(os.listdir(test_suite_path)):
            if folder.startswith(case_name):
                list_of_folders.append(folder)
        list_of_folders = list_of_folders

        for case in do_not_run_case_list:
            if list_of_folders:
                for folder in list_of_folders:
                    if case not in list_of_folders and case not in list_of_wrong_folders:
                        list_of_wrong_folders.append(case)
            else:
                if case not in list_of_wrong_folders:
                    list_of_wrong_folders.append(case)

        if list_of_wrong_folders:
            print('\nWarning: No case named by: {}. The program exits with code 0.\n'.
                  format(', '.join(list_of_wrong_folders)))
            sys.exit(0)

        case_list = sorted(list(set([folder for folder in sorted(os.listdir(test_suite_path))
                                     if folder.startswith(case_name)]) - set(do_not_run_case_list)))

    if run_all_cases:
        list_of_folders = []
        for folder in sorted(os.listdir(test_suite_path)):
            try:
                if folder.startswith(case_name):
                    list_of_folders.append(folder)
                    num_of_folders += 1
                    if verbosity:
                        print(folder)
            except TypeError:
                break

    if not run_all_cases:
        list_of_folders = []
        for case in case_list:
            for folder in os.listdir(test_suite_path):
                if case == folder:
                    list_of_folders.append(case)
                    num_of_folders += 1
                    if verbosity:
                        print(case)

    if (sorted(list_of_folders) != sorted(case_list)) and not run_all_cases and not do_not_run_case_list:
        for case in case_list:
            if list_of_folders:
                for folder in list_of_folders:
                    if case not in list_of_folders and case not in list_of_wrong_folders:
                        list_of_wrong_folders.append(case)
            else:
                if case not in list_of_wrong_folders:
                    list_of_wrong_folders.append(case)

        print('\nWarning: No case named by: {}. The program exits with code 0.\n'.
              format(', '.join(list_of_wrong_folders)))
        sys.exit(0)

    # -------------------------------------------------Test running process--------------------------------------------
    global forecast_exists, station_exists, observation_exists, json_exists, reference_exists
    global num_of_failure, list_of_failure_cases, list_of_missing_file_cases
    file_forecast_path = ''
    file_station_path = ''
    file_observation_path = ''
    extra_parameter = ''
    expected_value = 'SUCCESS'
    arrow_line = '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    ripple_line = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

    if verbosity:
        print('\n\n\n================================================================================')
        print('\n', '                            ', 'TESTING PROCESS: ')
        print('\n================================================================================')
    for folder in list_of_folders:
        current_case_path = './' + str(folder)
        for (dir_path, dir_names, file_names) in os.walk(current_case_path):  # Walk into each case.
            forecast_exists = False
            station_exists = False
            observation_exists = False
            json_exists = False
            reference_exists = False
            for file_name in file_names:
                extra_parameter = ''  # Set a default value for extra_parameter as not all cases need it.
                forecast_exists = os.path.isfile(current_case_path + '/forecast.xml')
                station_exists = os.path.isfile(current_case_path + '/station.xml')
                observation_exists = os.path.isfile(current_case_path + '/observation.xml')
                json_exists = os.path.isfile(current_case_path + '/config.json')
                reference_exists = os.path.isfile(current_case_path + '/roadcast_reference.xml')

            if forecast_exists:
                file_forecast_path = os.path.join(test_suite_path + dir_path[1:], 'forecast.xml')
            if station_exists:
                file_station_path = os.path.join(test_suite_path + dir_path[1:], 'station.xml')
            if observation_exists:
                file_observation_path = os.path.join(test_suite_path + dir_path[1:], 'observation.xml')
            if json_exists:
                os.chdir(current_case_path)  # Change the current path to the current case directory.
                with open('config.json') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key == 'addition_to_command_line':
                            if value is not None:
                                extra_parameter = value
                        if key == 'expected_running_result':
                            if value == 'FAILURE':
                                expected_value = 'FAILURE'
                            elif value == 'SUCCESS':
                                expected_value = 'SUCCESS'
                            else:
                                print('Please verify the format/syntax of the config.json file.')
                        if key == 'error_tolerance':
                            error_value = value
                        if key == 'description':
                            case_description = value

            if forecast_exists and station_exists and observation_exists:
                file_output_path = os.path.join(test_suite_path + dir_path[1:], 'roadcast_test_suite_run.xml')
                os.chdir(test_suite_path)  # Change back the path so as to make the function call.

                command_to_run = 'python3 ../../../../bin/metro {} --input-forecast {} --input-station {} ' \
                                 '--input-observation {} --output-roadcast {}'.format(extra_parameter,
                                                                                      file_forecast_path,
                                                                                      file_station_path,
                                                                                      file_observation_path,
                                                                                      file_output_path)

                if verbosity:
                    try:
                        print('\n>>>>>>>>>>>>>>>>>>>>>>>> {} starts to run...... <<<<<<<<<<<<<<<<<<<<<<<<<<'
                              '<'.format(folder))
                        print('\n{}\n'.format(case_description))
                        if expected_value == 'FAILURE':
                            print('>>>>>>>>>>>>>>>>>>>>>>>> {} is expected to FAIL...... <<<<<<<<<<<<<<<<<<'
                                  '<<<'.format(folder))
                        if expected_value == 'SUCCESS':
                            print('>>>>>>>>>>>>>>>>>>>>>>>> {} is expected to SUCCEED...... <<<<<<<<<<<<<<<<<<'
                                  '<<<'.format(folder))

                        print('\nSyntax to run {}:'.format(folder))
                        print('--------------------------------------------------------------------------------')
                        print(
                            'python3 ../../../../bin/metro {0} --input-forecast ../test_suite'
                            '/{1}/forecast.xml --input-station ../test_suite/{1}/station.xml --input'
                            '-observation ../test_suite/{1}/observation.xml --output-roadcast '
                            '../test_suite/{1}/roadcast_test_suite_run.xml\n'.format(extra_parameter, folder))
                        print('--------------------------------------------------------------------------------')

                        print('\n\n')
                        test_run = subprocess.run(command_to_run, shell=True, check=True)
                        print('\n\n{}'.format(arrow_line))
                        if reference_exists:
                            print('\nError Tolerance:                  {}'.format(error_value))
                        process_xml_file(current_case_path, folder, error_value, verbosity=True)
                        if not reference_exists:
                            print('No reference XML file to do the comparison.\n')
                        process_test_result(folder, test_run.returncode, expected_value, verbosity=True)
                    except subprocess.CalledProcessError:
                        print('\n\n{}'.format(arrow_line))
                        if not reference_exists:
                            print('No reference XML file to do the comparison.')
                        print('No generated XML file to do the comparison.\n')
                        process_test_result(folder, 1, expected_value, verbosity=True)
                        print('\n{}\n\n'.format(arrow_line))
                        continue
                    os.chdir(test_suite_path)
                    print('\n{}\n\n'.format(arrow_line))

                elif not verbosity:
                    test_run = subprocess.run(command_to_run, shell=True, stdout=subprocess.DEVNULL,
                                              stderr=subprocess.STDOUT)
                    process_xml_file(current_case_path, folder, error_value, verbosity=False)
                    process_test_result(folder, test_run.returncode, expected_value, verbosity=False)
                    os.chdir(test_suite_path)

            elif not forecast_exists or not station_exists or not observation_exists:
                if verbosity:
                    print('\n>>>>>>>>>>>>>>>>>>>>>>>> {} cannot be started...... <<<<<<<<<<<<<<<<<<<<<<'.format(folder))
                    print('\n{} has missing input file(s): '.format(folder))
                    if not forecast_exists:
                        print("\t\t\t\t\t'forecast.xml'")
                    if not station_exists:
                        print("\t\t\t\t\t'station.xml'")
                    if not observation_exists:
                        print("\t\t\t\t\t'observation.xml'")
                num_of_failure += 1
                list_of_missing_file_cases.append(folder)
                print(folder, ' FAILURE! ***')
                if verbosity:
                    print('\n{}\n\n'.format(arrow_line))
                os.chdir(test_suite_path)

    # ----------------------------------------------Summary after test running------------------------------------------
    print('\n\n\n================================================================================')
    print('\n', '                                  ', 'SUMMARY: ')
    print('\n================================================================================')
    print('Total number of test cases ran:\t\t\t\t', str(num_of_folders), '\nNumber of cases ran with SUCCESS:\t\t\t',
          str(num_of_success), '\nNumber of cases  ran with FAILURE: \t\t\t', str(num_of_failure))

    if len(list_of_missing_file_cases) != 0:
        print('Case(s) missing proper input file(s):\t\t\t', end=' ')
        print(*list_of_missing_file_cases, sep=' ')

    if len(list_of_failure_cases) != 0:
        print('Case(s) does/do not produce expected result(s):\t\t', end=' ')
        print(*list_of_failure_cases, sep=' ')
    print('\n\n\n')

    if (len(list_of_failure_cases) != 0) and verbosity:
        print('\n\n\n================================================================================')
        print('\n', '                           ', 'FAILED RUNNING CASE(S): ')
        print('\n================================================================================')
        for case in list_of_failure_cases:
            print(case)
            print(ripple_line)
            print('Syntax to run this individual case with more details:')
            print('-----------------------------------------------------')
            print('python3 ../../../../bin/metro {0} --verbose-level 4 --input-forecast ../test_suite'
                  '/{1}/forecast.xml --input-station ../test_suite/{1}/station.xml --input'
                  '-observation ../test_suite/{1}/observation.xml --output-roadcast '
                  '../test_suite/{1}/roadcast_test_suite_run.xml\n'.format(extra_parameter, case))


if __name__ == '__main__':
    main()
    sys.exit(num_of_failure)
