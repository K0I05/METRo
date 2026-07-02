                      METRo Developer README file

You are currently reading the Developer README file. For general information
about METRo please read the "README" file.


========================================
== Setting up development environment ==
========================================

init_devel.sh
-------------
You need to run the 'init_devel.sh' script to prepare your working directory. 
If the script complain about the environment variable "PYTHON_INCLUDE": 
you need to set it to a valid value. Usually, it will be something like:
'export PYTHON_INCLUDE=/usr/include/pythonX.X' where the X's are the 
version numbers. You only need to run the 'init_devel.sh' script one time.

* From now on, we assume the 'init_devel.sh' script has been run.


==========================
== New optional features ==
==========================

Freezing point of water in the forecast
----------------------------------------
The atmospheric forecast file can optionally give METRo the freezing point of
water (in Celsius) for each forecast timestep, instead of always assuming the
physical freezing point of pure water (0 C). This is useful for roads treated
with de-icing chemicals, where water on the surface does not actually freeze
at 0 C.

1) Add a <tfz> element (Celsius) to every <prediction> in the forecast file:

    <prediction>
        <forecast-time>2018-03-27T15:00Z</forecast-time>
        <at>-5.0</at>
        ...
        <tfz>-3.0</tfz>
    </prediction>

2) Run METRo with the option --use-freezing-point-forecast :

    metro --use-freezing-point-forecast --input-forecast forecast.xml \
          --input-observation observation.xml --input-station station.xml \
          --output-roadcast roadcast.xml

If the option is not used, or a given prediction has no <tfz>, METRo falls
back to the physical freezing point of pure water (0 C), i.e. the previous
behaviour is unchanged.

Custom road layer type
-----------------------
The station configuration file's road layers were previously restricted to
4 built-in materials (asphalt, crushed rock, cement, sand). A 5th type,
'custom', lets you supply the thermal capacity (J/m3/K) and conductivity
(W/m/K) of the layer directly, for materials METRo doesn't know about.

1) In the station file, set <type>custom</type> and add <capacity> and
   <conductivity> to that roadlayer:

    <roadlayer>
        <position>1</position>
        <type>custom</type>
        <thickness>0.15</thickness>
        <capacity>1.8e6</capacity>
        <conductivity>1.2</conductivity>
    </roadlayer>

2) Run METRo normally; no command line option is needed, the layer type in
   the station file is enough.

Both <capacity> and <conductivity> are mandatory for a 'custom' layer, and
must fall within a validated range:
    capacity:     1.0e6 to 1.0e7  J/m3/K
    conductivity: 0.05  to 3.5   W/m/K
Values outside this range are rejected at startup with a clear error message.
This is not an arbitrary restriction: METRo's ground grid (src/model/grille.f)
is a fixed-size, unbounded-checked array tuned for the 4 built-in materials.
Values far outside the validated range make it numerically unstable and crash
the compiled physics core (segfault) instead of failing gracefully, so keep
new materials within (or close to) this range.

Non-'custom' layers ignore <capacity>/<conductivity> if present.


=======================
== Compiling "model" ==
=======================

Fortran model
-------------
To compile the Fortran model you will need to perform the following action:
1) cd src/model/
2) ../../scripts/do_macadam


======================
== Building package ==
======================

1) Change the METRo version number in the following files:
    scripts/do_macadam
    src/frontend/metro_config.py

2) Change release date in the following files:
    README
    src/frontend/metro_config.py

3) Commit every change
    svn commit

4) Compile model:
    compile the Fortran model (see == Compiling "model" ==)

5) Update package list
    grep -E "^src/frontend/.*\.py" scripts/make_package.py | sort > /tmp/packaged_modules
    find src/frontend -name *.py | sort > /tmp/actual_modules
    diff -y -W 200 /tmp/packaged_modules /tmp/actual_modules
    vi scripts/make_package.py

6) Build Package
    cd scripts/ 
    ./make_package.py
    * You need a valid gpg key to be able to sign your package

=============
== Release ==
=============

1) Make a tag in SVN for the release of that version.
   You will need an access to the metro project on GNA to do that.
   The following is an example of the user Francois Fortin making a tags
   for the 3.2.4 version

   svn copy svn+ssh://francois_fortin@svn.gna.org/svn/metro/metro/trunk \
            svn+ssh://francois_fortin@svn.gna.org/svn/metro/metro/tags/metro-3.2.4
    
2) Upload package to the GNA web site (http://download.gna.org/metro/)
   scp metro-3.2.4.tar.bz2  metro-3.2.4.tar.bz2.sig
   francois_fortin@download.gna.org:/upload/metro/

3) Create a new LATEST_RELEASE file with the new version number.
   The content of the file is:

   ------------------------------------- cut here --------------------------------
   Please note:

   - The latest stable version of the METRo package is:
     metro-3.2.4
   ------------------------------------- cut here --------------------------------

4) Upload the LATEST_RELEASE file to the GNA web site
   (http://download.gna.org/metro/)
   scp LATEST_RELEASE francois_fortin@download.gna.org:/upload/metro/

