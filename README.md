# lastricks
A few LAS manipulations


## Installation
For now, to avoid trouble when installing `rasterio` and `gdal`, I recommend to use the provided conda environment (the one with laspy 2.x):
```
conda env create --file lastricks_v2_env.yml
```

## Run tests
 Since we are in the middle of the switch from laspy==1.7.x to laspy==2.0, make sure you have different virtual environments for each version of laspy.
 Only the test files with a `_v2` prefix will run with laspy==2.0:
```
pytest test/*_v2.py
```
 

## Dev stuff

### TODOS
+ [x] finish refactor to laspy==2.0
+ [x] update use_cases to reflect refactor
+ [x] build wheel
+ [ ] create documentation 



### Blueprint for `metrics`  and `analysis` 
We want a quick tool to generate all our usual metrics but on a specific region. Namely all ditches.
All ditches points are known thanks to the `ahn4clust-dec1-wc` dataset.

Params of new function:
+ gt_file: ground truth file
+ eval_file: the file to evaluate
+ filter_file: the file on which the filtering is being done
+ filter_class: an integer representing the class on which the filtering should be done.

