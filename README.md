 A few LAS manipulations

## Run tests
 Since we are in the middle of the switch from laspy==1.7.x to laspy==2.0, make sure you have different virtual environments for each version of laspy.
 Only the test files with a `_v2` prefix will run with laspy==2.0:
```
pytest test/*_v2.py
```
 

## TODOS
+ [ ] finish refactor to laspy==2.0
+ [ ] update use_cases to reflect refactor
+ [ ] build wheel
+ [ ] create documentation 



## Blueprint for `metrics`  and `analysis` 
We want a quick tool to generate all our usual metrics but on a specific region. Namely all ditches.
All ditches points are known thanks to the `ahn4clust-dec1-wc` dataset.

Params of new function:
+ gt_file: ground truth file
+ eval_file: the file to evaluate
+ filter_file: the file on which the filtering is being done
+ filter_class: an integer representing the class on which the filtering should be done.

