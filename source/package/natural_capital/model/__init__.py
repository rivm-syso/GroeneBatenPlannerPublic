"""
Collection of natural capital models

Each model is available as a function accepting input variables and
returning output variables. I/O must be handled elsewhere. If you
need higher level function, also performing I/O, have a look at the
:py:mod:`.hl` module.

High-level usage:

.. code-block:: python

   from natural_capital.model.hl import cooling_in_urban_areas

   project_file_pathname = "my_project.ini"
   cooling_in_urban_areas(project_file_pathname)


Low-level usage:

.. code-block:: python

   from natural_capital.model import cooling_in_urban_areas

   # Create/read input variables
   land_cover = ...
   residential_areas = ...
   cooling_effect_factor = ...
   cooling_vegetation = ...

   # Call function to determine output variables
   fraction_cooling_vegetation, decrease_uhi, cooling_effect = \\
       cooling_in_urban_areas(
           land_cover, residential_areas, cooling_effect_factor,
           cooling_vegetation)

   # Use result variables

   from natural_capital.model import wood_production
   # TODO
   # Create/read input variables

   # Call function to determine output variables

   # Use result variables
   in carbon_sequestration

   from natural_capital.model import carbon_sequestration
   # TODO
   # Create/read input variables

   # Call function to determine output variables

   # Use result variables
   in biomass energy
   ...

The high-level API can be used when writing shell scripts for running
individual models. See for example the implementation of the scripts
in the `script` directory. The low-level API can be used when a model
must be integrated in other software. The low-level API is, of course,
used in the implementation of the high-level API.
"""
from .cooling_in_urban_areas import function as cooling_in_urban_areas
from .pollination import function as pollination
