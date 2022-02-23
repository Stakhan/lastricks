


def metrics_subcloud(
    gt_file,
    eval_file,
    filter_file,
    filter_class
):
    """Compute metrics on a subset of points based on the class of an extra file.

    Args:
        gt_file (pathlib.Path): ground truth file
        eval_file (pathlib.Path): file to evaluate
        filter_file (pathlib.Path): file on which the filtering will be based
        filter_class (int): class used for filtering within `filter_file`
    
    Returns:
        pandas.DataFrame
    """
