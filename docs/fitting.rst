===========================================
Fitting data with radiative transfer models
===========================================

This section is for setting up your data and running a fit of a disk radiative transfer model to it.

Preparing your data to be in the correct format
"""""""""""""""""""""""""""""""""""""""""""""""

Once CASA6 is released, there will be functionality to read data directly from CASA MS files, however until CASA6 is available, I put the data into my own HDF5 format. Here’s how:

1. Within CASA, use the exportuvfits to split every spectral window that you care about into a separate UV FITS file. Each MS file should go into a separate .vis file:
   ::

       filenameA.vis/  
       |---- filenameA.1.uv.fits  
       |---- filenameA.2.uv.fits  
       .  
       .  
       .  
       \---- filenameA.N.uv.fits  
       filenameB.vis/  
       |---- filenameB.1.uv.fits  
       |---- filenameB.2.uv.fits  
       .  
       .  
       .  
       \---- filenameB.N.uv.fits

   I’ll typically organize this by array configuration and band, so it may look like this:
   ::

       source_Band3_track1.vis  
       source_Band3_track2.vis  
       source_Band6_track1.vis  

2. Use the below code to turn the .vis files into HDF5 files. 
   ::

       import pdspy.interferometry as uv  
       import glob  

       files = glob.glob("*Band3*.vis")  

       data = []  
       for file in files:  
           data.append(uv.freqcorrect(uv.readvis(file)))  

       vis = uv.concatenate(data)  

       vis.write("Source_Band3.hdf5")

   It’ll grab all of the \*.vis files that match the wildcard at the beginning, so you can adjust that to decide which sets of files get grabbed. So in the above example you could run it once with \*Band3\*.vis to merge the Band 3 data into one file, and then \*Band5\*.vis to merge the Band 6 data into a single dataset.

Setting up a configuration file
"""""""""""""""""""""""""""""""

You can find a basic configuration file in the pdspy bin directory (`config_template.py <https://github.com/psheehan/pdspy/blob/master/bin/config_template.py>`_) as an example, and I think it should be close to what you’ll want for your application. The visibilities dictionary requests a bunch of information about the visibility data. The things in particular you’ll want to update are:

**file:** the HDF5 visibility files the were created above. Can list as many as you’d like, I just put in 2 as an example. (All of the entries in the visibilities dictionary should be lists with the same number of elements).

**freq/lam:** The frequency/wavelength of the observations. Freq should be a string, lam a number.

**x0/y0:** If the data is far off-center, these are initial corrections to approximately center the data. I believe positive x0 means west and positive y0 is south (i.e. perfectly backwards; a relic of not catching the problem until I was in too deep).

**image_file:** every HDF5 file should have a corresponding FITS image to show the best fit model over. All of the other image_* parameters correspond to values from the image: pixelsize, npix

Then at the bottom the **parameters** dictionary gives you a giant list of parameters that can be turned on or off. When a parameter has fixed:True, then it is fixed at a value of value. If fixed:False, then it’s a free parameter constrained by limits. For a full list of parameters, see `here <https://github.com/psheehan/pdspy/blob/master/pdspy/modeling/base_parameters.py>`_

The **flux_unc\*** parameters at the bottom add a flux uncertainty to the observations, with sigma:0.1 = 10% uncertainty (but that can be changed), and a Gaussian prior. You can add as many of these as you have visibility files, so you can tune the flux uncertainty separately for each dataset.

Running a model
"""""""""""""""

Make sure /path/to/pdspy/bin is in your PATH so that you can see the disk_model.py function. There are currently three well tested tools to run models:

+ **disk_model.py**: Used to fit ALMA continuum visibilities and broadband spectral energy distributions (SEDs) with full radiative transfer models.

+ **disk_model_powerlaw.py**: Used to fit ALMA continuum visibilities with protoplanetary disk models that include a vertically isothermal, power law temperature distribution. No radiative equilibrium calculation is done.

+ **flared_model.py**: Used to fit ALMA spectral line visibilities with protoplanetary disk models that include a vertically isothermal, power law temperature distribution. No radiative equilibrium calculation is done.

From there the most basic way to run any one of these models is in the directory with config.py and entering:
::

    disk_model.py --object <Object Name>

If you want to run with parallel RADMC-3D, to speed up the code, you can run:
::

    disk_model.py --object <Object Name> --ncpus N

Progress is saved, so if you want to resume a fit that stopped for some reason, you can add:
::

    disk_model.py --object <Object Name> --ncpus N --resume

You can also use MPI to run multiple single core models at once:
::

    mpirun -np N disk_model.py --object <Object Name> --ncpus 1

Or some combination of simultaneous models and parallel RADMC-3D:
::

    mpirun -np N disk_model.py --object <Object Name> --ncpus M

(where NxM should be <= the number of cores on your computer). The last two commands for running the code (using MPI) make it adaptable so that it can be run on supercomputers as well, for an even bigger boost. If you want to do this, let me know and I can provide some more details of how to efficiently run over multiple supercomputer nodes.
