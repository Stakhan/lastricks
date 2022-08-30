# lastricks
A few LAS manipulations.

## Installation
1. Clone the repository:
```
git clone https://github.com/Stakhan/lastricks
```
2. Install complicated dependencies:
```
 conda install -c conda-forge geopandas 
```
3. Install the rest of the dependencies from `pyproject.toml`:
```
cd lastricks
pip install -e .
```

## Run tests
 
```
pytest test
```
*NB: Some older tests have been developed with laspy==1.7.x and haven't been rewritten yet. They are suffixed with `_v1.7` and prefixed with a `_` to avoid execution when launching pytest.*

## Development
### General TODOS
+ [ ] finish refactor to laspy==2.0
+ [ ] update use_cases to reflect refactor
+ [ ] create documentation 
+ [ ] build wheel


### Blueprint for `metrics`  and `analysis` 
We want a quick tool to generate all our usual metrics but on a specific region. Namely all ditches.
All ditches points are known thanks to the `ahn4clust-dec1-wc` dataset.

Params of new function:
+ gt_file: ground truth file
+ eval_file: the file to evaluate
+ filter_file: the file on which the filtering is being done
+ filter_class: an integer representing the class on which the filtering should be done.

