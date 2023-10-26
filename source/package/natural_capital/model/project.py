"""
Code related to the configuration of projects
"""
import json
import os
import sys


if sys.version_info[0] == 2:
    # Config parser API of Python 2 is slightly different to the API of
    # Python 3. Here we patch Python 2's API so we don't have to deal
    # with the differences in the rest of the code.
    import ConfigParser as configparser
    import StringIO

    configparser.ConfigParser.read_file = configparser.ConfigParser.readfp
    configparser.ConfigParser.read_string = (
        lambda self, string: configparser.ConfigParser.read_file(
            self, StringIO.StringIO(string)
        )
    )
else:
    import configparser


class Configuration:
    """
    Class for storing project configuration information
    """

    def __init__(self, parser):
        self.parser = parser
        self.expand_environment_variables()

        self.input_data_pathname = os.path.join(
            self.parser.get("input", "workspace"), self.parser.get("input", "directory")
        )
        self.output_data_pathname = os.path.join(
            self.parser.get("output", "workspace"),
            self.parser.get("output", "directory"),
        )
        self.raster_input_data_pathname = os.path.join(
            self.input_data_pathname, self.parser.get("input", "raster")
        )
        self.table_input_data_pathname = os.path.join(
            self.input_data_pathname, self.parser.get("input", "table")
        )
        self.raster_output_data_pathname = os.path.join(
            self.output_data_pathname, self.parser.get("output", "raster")
        )

    def string_value(self, section, option):
        """
        Return the option's value as a string
        """
        return self.parser.get(section, option).strip()

    def float_value(self, section, option):
        """
        Return the option's value as a floating point
        """
        return self.parser.getfloat(section, option)

    def input_raster_pathname(self, section, option):
        """
        Return an option's value as an input raster pathname
        """
        return os.path.join(
            self.raster_input_data_pathname, self.string_value(section, option) + ".map"
        )

    def output_raster_pathname(self, section, option):
        """
        Return an option's value as an output raster pathname
        """
        return os.path.join(
            self.raster_output_data_pathname,
            self.string_value(section, option) + ".map",
        )

    def input_table_pathname(self, section, option):
        """
        Return an option's value as an input table pathname
        """
        return os.path.join(
            self.table_input_data_pathname, self.string_value(section, option) + ".tab"
        )

    def parameters(self, section):
        """
        Return a dictionary containing the names of the model parameters
        of model named *section*
        """
        return json.loads(self.string_value(section, "parameters"))

    def input_raster_names(self, section):
        """
        Return the names of the input rasters
        """
        return self.parameters(section)["input"]["raster"]

    def input_table_names(self, section):
        """
        Return the names of the input tables
        """
        return self.parameters(section)["input"]["table"]

    def expand_environment_variables(self):
        """
        For all parameters that contain a pathname, replace environment
        variables by their values
        """

        def expand(section, options):
            if isinstance(options, list):
                for option in options:
                    expand(section, option)
            else:
                option = options
                self.parser.set(
                    section,
                    option,
                    os.path.expandvars(self.parser.get(section, option)),
                )

        def model_section_names():
            sections = set(self.parser.sections())
            std_sections = {"DEFAULT", "input", "output"}
            return sections - std_sections

        expand("DEFAULT", "workspace")
        expand("input", ["directory", "raster", "table"])
        expand("output", "directory")

        # In all model sections, replace environment variables in pathnames
        for model_section_name in model_section_names():
            expand(model_section_name, self.input_raster_names(model_section_name))
            expand(model_section_name, self.input_table_names(model_section_name))


# Per model some information for us, not for the user.
# parameters: A JSON formatted value containing information that is used
#     by the Configuration class. In case the JSON parser complains, then
#     the value is not formatted correctly.
# - Scalar input parameters are not yet listed here. No need for it yet.
PRIVATE_DEFAULT_CONFIGURATION = """
[mortality_reduction]
parameters = {
        "input": {
            "raster": [
                "population",
                "ndvi",
                "mort"
                ],
         "table": [
            ]
        },
        "output": {
            "raster": [
             "mortality_reduction",
             "mortality_reduction_total",
             "mortality_reduction_per_100k"
            ]
        }
    }

[heat_stress]
parameters = {
        "input": {
            "raster": [
                "root4",
                "svf_bag",
                "trees",
                "shrubs",
                "grass",
                "bgt",
                "ndvi"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "uhi_max",
                "uhi_max_lim",
                "cooling",
                "cooling_lim"
            ]
        }
    }

[pm_retention]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "pm_10",
                "pm_25",
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
                "deposition_lut",
                "deposition_tree_lut",
                "resuspension_fractionpm10_lut",
                "resuspension_fractionpm25_lut"
            ]
        },
        "output": {
            "raster": [
                "capture_pm10",
                "capture_pm25",
                "map_total_pm10",
                "map_total_pm25",
                "perc_conc_change_pm10",
                "perc_conc_change_pm25"
            ]
        }
    }

[physical_activity]
parameters = {
        "input": {
            "raster": [
                "population",
                "ndvi"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [

                "added_activity"

            ]
        }
    }

[obesity_and_green_space]
parameters = {
        "input": {
            "raster": [
                "population",
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "ProbObesity",
                "PopProb",
                "AverageProbObesity"
            ]
        }
    }

[green_and_mental_health]
parameters = {
        "input": {
            "raster": [
                "population",
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "ProbPsycho",
                "PopPsycho",
                "AverageProbPsycho",
                "ProbAnxi",
                "PopAnxi",
                "AverageProbAnxi",
                "ProbHypno",
                "PopHypno",
                "AverageProbHypno",
                "ProbAntidep",
                "PopAntidep",
                "AverageProbAntidep"
            ]
        }
    }

[water_storage]
parameters = {
        "input": {
            "raster": [
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "Water_storage",
                "Water_storage_monetary"
            ]
        }
    }

[environmental_health_risks]
parameters = {
        "input": {
            "raster": [
                "pm_10",
                "NO2"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "MGR_pm_10",
                "MGR_NO2"
            ]
        }
    }


[wind_map]
parameters = {
        "input": {
            "raster": [
                "Buildings",
                "Buildings_frontNS",
                "Height_buildings",
                "Trees",
                "Trees_frontNS"
            ],
            "table": [
            ]
        },
        "output": {
            "raster": [
                "Southwind_buildings",
                "Southwind_trees",
                "Southfront_buildings",
                "Southfront_trees"
            ]
        }
    }

[cooling_in_urban_areas]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "wind_speed",
                "population",
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
                "roughness_length",
                "wind_class",
                "built_up",
                "uhi_reduction_lut"
            ]
        },
        "output": {
            "raster": [
                "maximum_uhi_effect",
                "potential_uhi_effect",
                "in_situ_cooling_effect",
                "actual_uhi_effect",
                "cooling_effect"
            ]
        }
    }

[green_space_and_health_lgn]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "mask",
                "crops",
                "LGN",
                "population"
            ],
            "table": [
                "agriculture_lut"
            ]
        },
        "output": {
            "raster": [
                "amount_of_green_space_with_agriculture",
                "amount_of_green_space_without_agriculture",
                "reduced_number_of_patients_with_agriculture",
                "reduced_number_of_patients_without_agriculture",
                "health_effects_with_agriculture",
                "health_effects_without_agriculture",
                "reduced_health_labor_costs_with_agriculture",
                "reduced_health_labor_costs_without_agriculture",
                "reduced_health_costs_with_agriculture",
                "reduced_health_costs_without_agriculture"
            ]
        }
    }

[house_value]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "population",
                "property_value",
                "lakes_and_seas",
                "trees",
                "shrubs",
                "grass"
            ],
            "table": [
                "property_value_increase_fraction_lut",
                "water_lut"
            ]
        },
        "output": {
            "raster": [

                "increase_property_value"
            ]
        }
    }

[wood_production_vegetation]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "Trees",
                "crop_parcels",
                "soil_physics_units",
                "groundwater_level",
                "high_groundwater_level",
                "low_groundwater_level",
                "area_percentage_natural_forest",
                "area_percentage_production_forest"
            ],
            "table": [
                "soil_texture_type",
                "soil_texture_group",
                "high_groundwater_level_class",
                "low_groundwater_level_class",
                "soil_drainage_class",
                "gxg_drainage_class",
                "drainage_group",
                "agricultural_areas",
                "soil_suitability_for_forest_a",
                "soil_suitability_for_forest_b",
                "forest_types",
                "forest_mask",
                "harvest_factora",
                "harvest_factorb",
                "increment_a",
                "increment_b",
                "wood_prices",
                "gxg_unit"
            ]
        },
        "output": {
            "raster": [
                "physical_suitability_wood_production",
                "potential_wood_production",
                "actual_wood_production",
                "monetary_value_actual_wood_production"
            ]
        }
    }

[Biocontrol]
parameters = {
        "input": {
            "raster": [
                "Flowerrich_annual",
                "Flowerrich_perennial",
                "Flowerpoor_perennial",
                "Bushes",
                "Treeline",
                "Crops"
            ],
            "table": [
                "Pest_habitat_lut"
            ]
        },
        "output": {
            "raster": [
                "Pest_habitat",
                "Crawling_predator_habitat",
                "Flying_predator_habitat",
                "Parasitoids_habitat",
                "Overall_predator_habitat",
                "Effective_pestcontrol"
            ]
        }
    }

[carbon_sequestration_vegetation]
parameters = {
        "input": {
            "raster": [
                "land_cover",
                "Trees",
                "area_percentage_natural_forest",
                "area_percentage_production_forest"
            ],
            "table": [
                "biomass_expansion_factors",
                "wood_density_factors",
                "forest_types",
                "storage_change_natforest_factors",
                "storage_change_prodforest_factors"
            ]
        },
        "output": {
            "raster": [
                "potential_c_sequestration_biomass_forest",
                "actual_c_sequestration_biomass_forest"
            ]
        }
    }


"""


DEFAULT_CONFIGURATION = """\
# - Names of datasets (raster, tables) don't need an extension
# - Pathnames of files and directories can be relative or absolute. In case
#   of relative pathnames, they are joined to upper level pathnames. Otherwise
#   they are used unchanged. For example, the pathname of an input land
#   cover raster dataset is determined by joining the configuration values of
#   <DEFAULT:workspace>/<input:directory>/<input:raster>/
#       <pm_retention:land_cover>


[DEFAULT]
# Default pathname of workspace directory. It is often convenient to put all
# data in subdirectories below the workspace directory.
workspace = workspace


[input]
# Pathname of directory containing input files. Unless this directory
# is an absolute path, it will be joined to the workspace directory
# pathname.
directory = input

# Pathname to directory containing input raster datasets. Unless this
# directory is an absolute path, it will be joined to the input directory.
raster = raster

# Pathname to directory containing input table datasets. Unless this
# directory is an absolute path, it will be joined to the input directory.
table = table


[output]
# Pathname of directory containing output files. This directory will be
# joined to the workspace directory pathname.
directory = output
raster =

[mortality_reduction]
# Inputs
ndvi = ndvi_2020
mort = mort_2022
population = inwonerkaart

# Outputs
mortality_reduction = mortality_reduction
mortality_reduction_total = mortality_reduction_total
mortality_reduction_per_100k = mortality_reduction_per_100k

[heat_stress]
# Inputs
root4 = root4_10m
svf_bag = svf_bag_10m
trees = bomenkaart
shrubs = struikenkaart
grass = graskaart
bgt = bgt
ndvi = ndvi_2020

# Outputs
uhi_max = uhi_max
uhi_max_lim = uhi_max_lim
cooling = cooling
cooling_lim = cooling_lim

[pm_retention]
# Inputs
land_cover = land_cover
pm_10 = pm_10
pm_25 = pm_25
trees = trees
shrubs = shrubs
grass = grass
resuspension_fractionpm10 = 0.5
resuspension_fractionpm25 = 0.76
deposition_lut = deposition
deposition_tree_lut = deposition_tree

# Outputs
capture_pm10 = capture_pm10
capture_pm25 = capture_pm25
map_total_pm10 = map_total_pm10
map_total_pm25 = map_total_pm25
perc_conc_change_pm10 = perc_conc_change_pm10
perc_conc_change_pm25 = perc_conc_change_pm25

[physical_activity]
# Inputs
population = population
ndvi = ndvi

# Outputs
added_activity = added_activity


[obesity_and_green_space]
# Inputs
population = population
trees = trees
shrubs = shrubs
grass = grass

# Outputs
ProbObesity = ProbObesity
PopProb = PopProb
AverageProbObesity = AverageProbObesity

[green_and_mental_health]
# Inputs
population = population
trees = trees
shrubs = shrubs
grass = grass

# Outputs
ProbPsycho = ProbPsycho
PopPsycho = PopPsycho
AverageProbPsycho = AverageProbPsycho
ProbAnxi = ProbAnxi
PopAnxi = PopAnxi
AverageProbAnxi = AverageProbAnxi
ProbHypno = ProbHypno
PopHypno = PopHypno
AverageProbHypno = AverageProbHypno
ProbAntidep = ProbAntidep
PopAntidep = PopAntidep
AverageProbAntidep = AverageProbAntidep

[water_storage]
# Inputs
trees = trees
shrubs = shrubs
grass = grass

# Outputs
Water_storage = Water_storage
Water_storage_monetary = Water_storage_monetary

[environmental_health_risks]
# Inputs
pm_10 = pm_10
NO2 = NO2

# Outputs
MGR_pm_10 = MGR_pm_10
MGR_NO2 = MGR_NO2

[wind_map]
#Inputs
Buildings = Buildings
Buildings_frontNS = Buildings_frontNS
Height_buildings = Height_buildings
Trees_frontNS = Trees_frontNS
Trees = Trees

#Outputs
Southwind_buildings = Southwind_buildings
Southwind_trees = Southwind_trees
Southfront_buildings = Southfront_buildings
Southfront_trees = Southfront_trees

[cooling_in_urban_areas]
# Inputs
land_cover = land_cover
roughness_length = roughness_length
wind_speed = wind_speed
wind_class = wind_class
population = population
built_up = built_up
uhi_reduction_lut = uhi_reduction
trees = trees
shrubs = shrubs
grass = grass

# Outputs
maximum_uhi_effect = maximum_uhi_effect
potential_uhi_effect = potential_uhi_effect
in_situ_cooling_effect = in_situ_cooling_effect
actual_uhi_effect = actual_uhi_effect
cooling_effect = cooling_effect


[house_value]
# Inputs
land_cover = land_cover
population = population
property_value = property_value
property_value_increase_fraction_lut = property_value_increase_fraction
lakes_and_seas = lakes_and_seas
water_lut = water
trees = trees
shrubs = shrubs
grass = grass

# Outputs
increase_property_value = increase_property_value

[wood_production_vegetation]
#Inputs
land_cover = land_cover
Trees = Trees
crop_parcels = crop_parcels
soil_physics_units = soil_physics_units
groundwater_level = groundwater_level
high_groundwater_level = high_groundwater_level
low_groundwater_level = low_groundwater_level
area_percentage_natural_forest = area_percentage_natural_forest
area_percentage_production_forest = area_percentage_production_forest
soil_texture_type = soil_texture_type
soil_texture_group = soil_texture_group
high_groundwater_level_class = high_groundwater_level_class
low_groundwater_level_class = low_groundwater_level_class
soil_drainage_class = soil_drainage_class
gxg_drainage_class = gxg_drainage_class
drainage_group = drainage_group
agricultural_areas = agricultural_areas
soil_suitability_for_forest_a = soil_suitability_for_forest_a
soil_suitability_for_forest_b = soil_suitability_for_forest_b
forest_types = forest_types
forest_mask = forest_mask
harvest_factora = harvest_factora
harvest_factorb = harvest_factorb
Increment_a = Increment_a
Increment_b = Increment_b
wood_prices = wood_prices
gxg_unit = gxg_unit

# Outputs
physical_suitability_wood_production = physical_suitability_wood_production
potential_wood_production = potential_wood_production
actual_wood_production = actual_wood_production
monetary_value_actual_wood_production = monetary_value_actual_wood_production

[Biocontrol]
# Inputs
Flowerrich_annual = Flowerrich_annual
Flowerrich_perennial = Flowerrich_perennial
Flowerpoor_perennial = Flowerpoor_perennial
Bushes = Bushes
Treeline = Treeline
Crops = Crops
Pest_habitat_lut = Pest_habitat_lut
# Outputs
Pest_habitat = Pest_habitat
Crawling_predator_habitat = Crawling_predator_habitat
Flying_predator_habitat = Flying_predator_habitat
Parasitoids_habitat = Parasitoids_habitat
Overall_predator_habitat = Overall_predator_habitat
Effective_pestcontrol = Effective_pestcontrol

[carbon_sequestration_vegetation]

potential_wood_production = potentiele_houtproductie
actual_wood_produdction = actuele_houtproductie
land_cover = bgt
Trees = bomenkaart
area_percentage_natural_forest = bt_natbos_oppfract
area_percentage_production_forest = bt_prodbos_oppfract
biomass_expansion_factors = BEF_aangepast
wood_density_factors = C_dichtheid
forest_types = BGTBostype
storage_change_natforest_factors = Voorraadveranderingsfactoren_natuurlijk_bos
storage_change_prodforest_factors = Voorraadveranderingsfactoren_productie_bos
c_to_co2 = C_CO2
classExtraTrees = 143
Carbon_price1 = 40
Carbon_price2 = 160
Carbon_price3 = 200


# Outputs
potential_c_sequestration_biomass_forest = potentiele_koolstofopslag_biomassa
actual_c_sequestration_biomass_forest = actuele_koolstofopslag_biomassa
Carbon_monetary1 = Monetary_benefit_carbon_sequestration1
Carbon_monetary2 = Monetary_benefit_carbon_sequestration2
Carbon_monetary3 = Monetary_benefit_carbon_sequestration3

"""


def default_configuration():
    """
    Fill and return a default configuration

    :rtype: configparser.ConfigParser

    Default configurations contain settings that will be used when the user
    does not overwrite them using a project configuration. First, a bare
    configuration is set, with the following settings:

    .. code-block:: ini

        {}

    These settings are probably not what you want to use...

    If the environment variable named `NCM_CONFIGURATION` is set,
    its value is used to update the configuration settings. It *must*
    point to a readable configuration file.

    Environment variables in pathnames will be expanded.
    """
    parser = configparser.ConfigParser()
    # interpolation=configparser.ExtendedInterpolation())  # Python 3 only...

    # Before populating the sections with the stuff the user can work with,
    # we add some information that is relevant for ourselves. These are
    # details which the user ideally should never see and change.
    # We need it because the ini file is nice for the user, but bad for
    # us. For example, given a section with options, we cannot figure
    # out which are the input parameters.
    # Therefore, we add some information, in json format for easy parsing.
    parser.read_string(PRIVATE_DEFAULT_CONFIGURATION)

    # Bare defaults, just to have all required fields populated
    configuration_string = DEFAULT_CONFIGURATION
    parser.read_string(configuration_string)

    # Site defaults
    variable_name = "NCM_CONFIGURATION"

    if variable_name in os.environ:
        configuration_file_pathname = os.environ[variable_name]
        with open(configuration_file_pathname, encoding="utf-8") as configuration_file:
            parser.read_file(configuration_file, configuration_file_pathname)

    return parser


# Insert the default configuration in the docstring. This way updates to
# the default configuration end up in the documentation automatically.
default_configuration.__doc__ = default_configuration.__doc__.format(  # type:ignore
    f"{8 * ' '}".join([f"{line}\n" for line in DEFAULT_CONFIGURATION.split("\n")])
)


def configuration(pathname):
    """
    Fill and return a configuration

    :param str pathname: Pathname to file containing configuration settings
    :rtype: Configuration

    The configuration returned is populated using the folowing procedure:

    - Load the :py:func:`default configuration <default_configuration>`
    - If `pathname` exists, update the default configuration using the
      settings found in `pathname`
    - Expand environment variables in pathnames

    It makes sense to put the important configuration settings in your
    own configuration file. These will overrule the default settings
    and can be used later to lookup the used settings and/or to rerun
    models.
    """

    parser = default_configuration()

    # It is not an error if pathname doesn't point to an existing file. See
    # ConfigParser's docs for more info.
    if not os.path.isfile(pathname):
        raise RuntimeError(f"Configuration file {pathname} does not exist")
    parser.read(pathname)

    return Configuration(parser)
