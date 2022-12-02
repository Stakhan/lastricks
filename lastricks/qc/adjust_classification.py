import numpy as np

def remove_virtual_points(classification):
    classification = np.array(classification)
    if 66 in classification:
        mask = classification != 66
        print(f"Removing {sum(~mask)} virtual points")
        return classification[ mask ]
    else:
        return classification