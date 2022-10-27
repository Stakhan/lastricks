# ``compare_deliveries`` README

## Preparing reference vector data
Using the FME workbench in this directory, convert your DGN file to a GPKG file:
```
fme dgnv8_to_gpkg.fmw --SourceDataset_DGNV8 <input_dgn_file> --DestDataset_OGCGEOPACKAGE <output_gpkg_file>
```

## Run the tool (Work In Progress)
Inside this directory:
```
python compare_deliveries.py \
            -d1 <path_to_delivery_1> \
            -d2 <path_to_delivery_2> \
            -e <path_to_errors_in_delivery_1>
```