= Installation procedure =

METRO has been designed to run under GNU/Linux operating system on a x86 processor.

In case of trouble during the installation, please read see the online documentation at:
https://framagit.org/metroprojects/metro/wikis/home

== Needed package ==

To run METRo, you will need the following software packages:

    * python 3 
    * python :: numpy
    * python :: libxml2
    * gfortran
    * SWIG
    
    
== METRo software installation ==

   1. Decompress the METRo software.

      Ex: tar xjvf metro-x.x.x.tar.bz2

   2. Execute the script setup.sh with the destination directory as an argument.

      Ex: ./setup.sh /usr/local

   3. To verify your installation, in the directory

       path_to_metro/usr/bin

      do this command

      python ./metro --selftest 

      if the file

       path_to_metro/usr/share/metro/data/roadcast/roadcast.xml

      was created successfully and the differences with 
       path_to_metro/usr/share/metro/data/selftest/roadcast_reference.xml
     
      is only the element <production-date>.
      
      Ex:
diff path_to_metro/data/roadcast/roadcast_selftest*
5c5
<     <production-date>2020-01-09T07:22Z</production-date>
---
>     <production-date>2014-10-16T16:00Z</production-date>

Note: path_to_metro means the path to the top-level metro directory where metro 
has been installed, not the directory where the original tar file was unpacked.
The location where the METRo source is unpacked is in a directory called 
"metro-", e.g. metro-4.0.0, but the install directory will be named just "metro".

