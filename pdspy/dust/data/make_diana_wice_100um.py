#!/usr/bin/env python3

from pdspy.dust import *
import numpy

water_ice = Dust()
water_ice.set_optical_constants_from_henn("optical_constants/water_ice.txt")
water_ice.set_density(0.92)

silicates = Dust()
silicates.set_optical_constants_from_draine("optical_constants/astronomical_silicates.txt")
silicates.set_density(3.3)
silicates.calculate_optical_constants_on_wavelength_grid(water_ice.lam)

amorphous_carbon = Dust()
amorphous_carbon.set_optical_constants_from_henn("optical_constants/amorphous_carbon_zubko1996_extrapolated.txt")
#amorphous_carbon.set_density(2.24)
amorphous_carbon.set_density(1.0)
amorphous_carbon.calculate_optical_constants_on_wavelength_grid(water_ice.lam)

species = [silicates,amorphous_carbon,water_ice]
abundances = numpy.array([0.8,0.2,0.5])
abundances = abundances / abundances.sum()
print(abundances)

dust = mix_dust(species, abundances, filling=0.75)

amin = 0.05e-4
amax = 1.000e-2
pl = 3.5

dust.calculate_size_distribution_opacity(amin, amax, pl, with_dhs=True, \
        coat_volume_fraction=0.0, nang=1)

dust.write('diana_wice_100um.hdf5')
