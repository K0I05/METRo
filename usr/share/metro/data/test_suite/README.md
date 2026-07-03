# README test_suite 

The `test_suite.py` of METRo runs pre-selected case(s) automatically and output a
forecast file named `roadcast_test_suite_run.xml` for every pre-selected case.
It then compares the forecast file `roadcast_test_suite_run.xml` with the given
benchmark forecast file `roadcast_reference.xml` and displays the comparison
result.

## Location

`test_suite.py` is located in the directory `$METRoDIR/usr/share/metro/data/test_suite`
where "$METRoDIR" represents the home directory of the software METRo.

Each test case contains a subdirectory named "caseDDD", where "DDD" is a three
digits case number (ex: "case001" represents a case having case number 1, and
"case020" represents a case having case number 20).

## How to run test_suite.py?

1. Go to the directory "$METRoDIR/usr/share/metro/data/test_suite" where
   "$METRoDIR" represents the home directory of METRo.

2. Enter "python3 test_suite.py" to run all the cases inside the directory
   "test_suite" and displays the running results in a simplified version.


           OPTIONS
   
             "-v":
             runs all cases inside the directory "test_suite" and displays the
             detailed information of running processes and outputs the running
             results in a verbose version.

             "-c XX XX ..." where XX represents the case number:
             runs the case(s) whose number(s) is/are entered after "-c". You can
             enter as many case numbers as you would like to run, but you have to
             enter at least one case number in order to active "-c". Note: "-c" 
             and "-s" cannot be used simultaneously.

             "-s XX XX ..." where XX represents the case number:
             runs by skipping the case(s) whose number(s) is/are entered after
             "-s". You can enter as many case numbers as you would like to skip,
             but you have to enter at least one case number in order to active
             "-s". Note: "-c" and "-s" cannot be used simultaneously.

             "-e YY" where YY represents the error tolerance in floating points:
             runs all cases inside the directory "test_suite" and compares
             "roadcast_test_suite_run.xml" with "roadcast_reference.xml" and
             outputs comparison result(s) using YY instead of the default value
             of 0.01 as error of tolerance.

              "--clean":
              deletes all the files named "roadcast_test_suite_run.xml" within the
              directory "test_suite"."--clean" can only be used in combination 
              with "-v" which displays all the directory/directories where the
              "roadcast_test_suite_run.xml" is/are deleted.

              "--help":
              test_suite.py displays all the detailed information regarding above
              mentioned parameters.


## Files in the test directory

### config.json:
           Configuration file for the test. It includes three attributes:
           "description", "addition_to_command_line" and
           "expected_running_result".

           Expected value for "description" can be any strings that you
           would like to comment on the case.

           Expected value for "addition_to_command_line":
           --config filename
           --enable-sunshadow
           --fix-deep-soil-temperature temperature
           --generate-config filename
           --lang fr|en
           --log-file filename
           --output-subsurface-levels
           --roadcast-start-date date
           --silent
           --sunshadow-method method--use-anthropogenic-flux
           --use-infrared-forecast
           --use-sst-sensor-depth
           --use-solarflux-forecast
           --verbose-level level
           --version
           --help
           Please refer to:
           https://framagit.org/metroprojects/metro/wikis/Man_page_(METRo)
           for more details.

           Expected value for "expected_running_result" can only be
           either "SUCCESS" or "FAILURE".

           One extra attribute "error_tolerance" can be added and the value of
           this attribute has to be in decimal places (For example, having the
           value of "0.05" as the "error_tolerance", the comparison result
           between "roadcast_test_suite_run.xml" and "roadcast_reference.xml"
           lies outside the range of 0.05; in other words, any comparison
           differences within 0.05 are ignored).

           Note: If you would like to use the default error tolerance of
                 "0.01", there is no need to add this extra attribute in
                 "config.json".

### forecast.xml, observation.xml and station.xml:

          METRo standard input files and each case should have these three
           files in order for METRo to generate possible forecast.

### roadcast_reference.xml:
           Benchmark forecast file. Only exists for those cases whose attribute
           "expected_running_result" has value of "SUCCESS".


