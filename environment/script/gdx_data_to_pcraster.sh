#!/usr/bin/env bash
set -e


# Tuples of (basename,input_extension,value_scale)
rasters="
    $NCM_WORKSPACE/20171103/Inputmaps,bomenkaart,tif,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,boomhoogte,tif,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,conc_pm10_2016,tif,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,Gewas,tif,VS_NOMINAL
    $NCM_WORKSPACE/20171103/Inputmaps,graskaart,tif,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,Inwoners,asc,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,LCEU_ini,tif,VS_NOMINAL
    $NCM_WORKSPACE/20171103/Inputmaps,Mask,tif,VS_BOOLEAN
    $NCM_WORKSPACE/20171103/Inputmaps,Meer_plas_zee,tif,VS_BOOLEAN
    $NCM_WORKSPACE/20171103/Inputmaps,struikenkaart,tif,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,windkaart,asc,VS_NOMINAL
    $NCM_WORKSPACE/20171103/Inputmaps,WOZ_buurt,asc,VS_SCALAR
    $NCM_WORKSPACE/20171103/Inputmaps,bofek2012,tif,VS_NOMINAL
"
# $NCM_WORKSPACE/20160223,Eerste_gwt,tif,VS_NOMINAL
# $NCM_WORKSPACE/20160223,GHG,tif,VS_SCALAR
# $NCM_WORKSPACE/20160223,GLG,tif,VS_SCALAR

areas="
    amsterdam
    arnhem
    nederland
    vondelpark
"


# Convert the original GDX input data to PCRaster format
# No conversion takes place if the output raster already exists
function gdx_data_to_pcraster()
{
    workspace=$NCM_WORKSPACE
    # input_directory=$workspace/20171103/Inputmaps
    output_directory=$workspace/input/raster/nederland_geconverteerd

    for tuple in $rasters; do
        IFS=',' read input_directory basename extension value_scale <<< "${tuple}"

        case $value_scale in
            "VS_BOOLEAN")
                value_type="Byte"
                ;;
            "VS_NOMINAL")
                value_type="Int32"
                ;;
            "VS_ORDINAL")
                value_type="Int32"
                ;;
            "VS_SCALAR")
                value_type="Float32"
                ;;
            *)
                echo "Unknown value scale: $value_scale"
                exit 1
                ;;
        esac

        input_raster=$input_directory/$basename.$extension
        output_raster=$output_directory/$basename.map

        if [ ! -f $output_raster ]; then
            echo "converting $basename..."
            gdal_translate \
                -of PCRaster \
                -ot $value_type \
                -mo "PCRASTER_VALUESCALE=$value_scale" \
                $input_raster $output_raster
        fi

    done;
}


# Cookie-cut an area from the Netherlands rasters
# No cookie-cutting takes place if the output raster already exists
function cookie_cut_area()
{
    x_min=$1
    y_min=$2
    x_max=$3
    y_max=$4
    output_directory=$5

    workspace=$NCM_WORKSPACE
    input_directory=$workspace/input/raster/nederland_geconverteerd
    output_directory=$workspace/input/raster/$output_directory

    mkdir -p $output_directory

    for tuple in $rasters; do
        IFS=',' read meh basename extension value_scale <<< "${tuple}"

        raster=$basename.map
        input_raster=$input_directory/$raster
        output_raster=$output_directory/$raster

        if [ ! -f $output_raster ]; then
            echo "cutting $basename..."
            cookie_cut.py $input_raster \
                $x_min $y_max $x_max $y_min \
                $output_raster
        fi
    done
}


# Cookie-cut some areas from the Netherlands rasters
function cookie_cut_areas()
{
    # Arnhem
    x_min=182745; y_min=429840; x_max=208346; y_max=448762;
    output_directory=arnhem
    cookie_cut_area $x_min $y_min $x_max $y_max $output_directory

    # Amsterdam
    # lon, lat (WGS84, epsg:4326) -> x, y (RD New, epsg:28992)
    # 4.6665, 52.2746 -> 105811.821671, 476532.094816
    # 5.127, 52.4743 -> 137320.608361, 498539.046838
    x_min=105811.821671; y_min=476532.094816
    x_max=137320.608361; y_max=498539.046838
    output_directory=amsterdam
    cookie_cut_area $x_min $y_min $x_max $y_max $output_directory

    # Vondelpark
    x_min=110483; y_min=480716; x_max=129397; y_max=490927
    output_directory=vondelpark
    cookie_cut_area $x_min $y_min $x_max $y_max $output_directory

    # Nederland, geharmoniseerd naar extent landgebruik
    x_min=10000; y_min=300000; x_max=280000; y_max=625000
    output_directory=nederland
    cookie_cut_area $x_min $y_min $x_max $y_max $output_directory
}


# Post-process rasters that need it
function post_process_rasters()
{
    workspace=$NCM_WORKSPACE

    for area in $areas; do
        output_directory=$workspace/input/raster/$area
        cd $output_directory
        pcrcalc \
            "LCEU_ini.map=if(LCEU_ini.map != 0 and LCEU_ini.map != 999, LCEU_ini.map)"
        cd -
    done
}


gdx_data_to_pcraster
cookie_cut_areas
# post_process_rasters
