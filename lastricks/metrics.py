import sklearn

class Metrics:

    def __init__(self, ground_truth, prediction, labels=None):
        self.confusion_matrix = sklearn.metrics.confusion_matrix(ground_truth, prediction, labels=labels)
        self.number_of_labels = self.confusion_matrix.shape[0]
        
        if labels:
            assert len(labels) == self.number_of_labels
            self.range_to_labels = {i:l for i, l in enumerate(labels)} 
    
    def get_TP(self, c):
        """returns true positives for class c"""
        return self.confusion_matrix[c,c]

    def get_FP(self, c):
        """returns false positives for class c"""
        return np.sum(self.confusion_matrix[:,c]) - self.get_TP(c)

    def get_FN(self, c):
        """returns false negatives for class c"""
        return np.sum(self.confusion_matrix[c,:]) - self.get_TP(c)

    def get_TN(self, c):
        """returns true negatives for class c"""
        return np.trace(self.confusion_matrix) - self.get_TP(c)

    def get_precision(self):
        pass
    
    def recall(self):
        pass

    def get_F1_score(self):
        pass

    def get_intersection_over_union(self, c):
        pass

    def summary(self):
        """Provides a summary of every metrics on the given data. 

        Returns:
            pandas.DataFrame: each metric computed for each class.
        """
        df = pd.DataFrame(data=self.confusion_matrix)
        if dataset.map_range_to_names:
            df.rename(columns=self.range_to_labels, index=self.range_to_labels, inplace=True)
        metrics_table = pd.DataFrame(index=['precision', 'recall', 'F-score', 'IoU'], columns=dataset.range_to_labels.keys())
        
        for c in metrics_table.columns:
            if c in df.columns:
                pass # Compute Precision, Recall, F1-score, IoU 
        
        metrics_table.rename(columns=self.range_to_labels)

        return metrics_table