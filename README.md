# lastricks
A few LAS manipulations.

## Overview
The main strength of lastricks is the ability to abstract the action of running a process on a single LAS/LAZ file or a folder of LAS/LAZ files.

The user can therefore concentrate on the actual processing with the [laspy library](https://laspy.readthedocs.io/en/latest/) by directly manipulating [`laspy.LasData`](https://laspy.readthedocs.io/en/latest/api/laspy.lasdata.html?highlight=LasData#lasdata) representations.

It can also handle sets of input LAS/LAZ files; in that case, it is implied that these sets are isomorph (i.e. for each file in one set there is a corresponding file in all other sets).

## Table of Contents

- [Status](#status)
- [Installation](#installation)
- [Usage](#usage)
- [Run tests](#run_tests)
- [Development/Documentation](#dev_doc)

## Status <a name = "status"></a>

| Development                      | Status      | Feature                                                                |
| -------------------------------- | ----------- | ---------------------------------------------------------------------- |
| [`core`](lastricks/core)         | finished    | <ul><li>[x] LASProcessor</li><li>[x] LASProcess</li></ul> |
| [`cleaning`](lastricks/cleaning) | finished    | <ul><li>[x] New Class From GeoPackage</li><li>[x] Reclassify Above</li></ul> |
| [`qc`](lastricks/qc)             | finished    | <ul><li>[x] Error Cloud</li></ul> |
| [`las2las`](lastricks/las2las)   | finished    | <ul><li>[x] CopyField </li></ul> |
| [`analysis`](lastricks/analysis) | in progress | <ul><li>[ ] Classification/Segmentation Metrics Summary</li></ul> |

## Installation <a name = "installation"></a>
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
## Usage <a name = "usage"></a>
Depending on the kind of processing you want to perform, two paradigms are available.
If your processing requires:
1. a single set of LAS/LAZ files as input → use a pipeline paradigm
2. two or more sets of LAS/LAZ files as input → use a kernel function paradigm

### Pipeline paradigm
In this paradigm, you can simply create a list of `lastricks.core.LASProcess` to apply:
```python
from pathlib import Path
from lastricks.cleaning import ReclassifyAbove
from lastricks.cleaning import new_class_from_gpkg

pipeline = [
    NewClassFromGpkg(
    Path("/path/to/vector_data.gpkg"),
    9,
    1,
    gpkg_as_mask=False
    ),
    ReclassifyAbove(
        Path("/path/to/DTM_20m.tif"),
        9,
        1,
        10
    )
]
```
Specify your set of input LAS/LAZ files and a location for your output:
```python
input_path = Path.cwd() / 'input'
output_path = Path.cwd() / 'output'
output_path.mkdir(exist_ok=True)
```
Create a LASProcessor object (responsible for abstracting the handling of sets of LAS/LAZ files):
```python
processor = LASProcessor(
    input_path,
    pipeline=cleaning_pipeline,
    output_folder=output_path,
    output_suffix='_processed'
)
```
Run the process:
```python
processor.run()
```
See [`here`](use_cases/cleaning_pipeline.py) for a complete example.

### Kernel function paradigm
In this paradigm you have to write a so-called "kernel function" that will be applied on each combination of `laspy.LasData` representation.

Let's take the example of the creation of an error cloud from a given classification and an awaited ground truth. Two sets of LAS/LAZ files are needed:
+ one set containing the classification
+ the other set containing the ground truth

Inside lastricks, these sets are handled by a `lastricks.core.InputManager`:
```python
from pathlib import Path
from lastricks.core import InputManager

input_path = Path('/path/to/input')
gt_input_path = Path('/Path/to/gt')

main_input = InputManager( input_path ) # classification
gt_input = InputManager( gt_input_path ) # ground truth
```
It is easy to iterate over them and get matching `laspy.LasData` representations:
```python
for path in main_input:
    classif = main_input.query_las(path)
    ground_truth = gt_input.query_las(path)
    # Do something with the representation...
```
Knowing this, let's write a kernel function that will apply the `qc.ErrorCloud` LASProcess:
```python
error_cloud = ErrorCloud(
    error_label = 1,
    correct_label = 0
)
def ec_kernel_func(path, main_input, *other_inputs):
    las = main_input.query_las(path)
    gt_las = other_inputs[0].query_las(path)
    return error_cloud(las, gt_las)
```
> NB: The kernel function has to match the following signature: ``kernel_func(path: Path, main_input: InputManager, *other_inputs: InputManager) -> LasData``.

And provide this kernel function to a LASProcessor object:
```python
output_path = Path('/path/to/output')
processor = LASProcessor(
    input_path,
    gt_input_path,
    kernel_func=ec_kernel_func,
    output_folder = output_path,
)
processor.run()
```
See [`here`](use_cases/qc_subcontractor_error_cloud_with_lasprocessor.py) for the complete example.

## Run tests <a name = "run_tests"></a>

```
pytest test
```
*NB: Some older tests have been developed with laspy==1.7.x and haven't been rewritten yet. They are suffixed with `_v1.7` and prefixed with a `_` to avoid execution when launching `pytest test`*

## Development/Documentation  <a name = "dev_doc"></a>
### General TODOS
+ [x] minimal usage section
+ [x] in use_cases:
    + simple example with kernel_func
    + simple example with pipeline
+ [ ] merge back to main (check older useful stuff is not ommitted in the process)
+ [ ] adding CLI version of each utility that one might call with `python -m lastricks.qc.error_cloud /path/to/input /path/to/output`
+ [ ] take care of `lastricks/cleaning/new_class_from_gpkg`
+ [ ] extensive documentation 
+ [ ] build wheel


### Blueprint for `metrics`  and `analysis` 
We want a quick tool to generate all our usual metrics but on a specific region. Namely all ditches.
All ditches points are known thanks to the `ahn4clust-dec1-wc` dataset.

Params of new function:
+ gt_file: ground truth file
+ eval_file: the file to evaluate
+ filter_file: the file on which the filtering is being done
+ filter_class: an integer representing the class on which the filtering should be done.

