"""
WHAT: Converts a data frame into discrete values via using clustering to identify value bins. See discretize() below for step-by-step logic.
WHY: Values in distinct bins can sometimes allow for easier modeling due to the removal of continuous values.
ASSUMES: Packages sklearn-som==1.1.0, numpy, pandas installed. Python 3.8 or greater.
         Data frame to be discretized can be clustered by clustering algorithm. Rows are instances/vectors, columns are features/variables.
FUTURE IMPROVEMENTS: Allow parameterization of clustering algorithm. This would allow flexibility in how clusters are generated compared to simply using SOM with defaults.
WHO: TZ 06/06/2023 Initial implementation.
"""
import numpy
import pandas
from sklearn_som.som import SOM
from typing import *
import logging
logger = logging.getLogger(__name__)


class ClusterDiscretizer:
    def __init__(self):
        """
        Initializes all attributes to be stored by the Cluster Discretizer. Call discretize() to generate discretized data.
        """
        # The clustering algorithm to run.
        self._clustering_algorithm: SOM = SOM()

        # The cluster labels for each instance. Generated once _cluster() is called.
        self._instance_clusters: numpy.array = numpy.array([])

        # List of all unique cluster values. Needed to quickly find ranges of each cluster via numpy.
        self._unique_clusters: numpy.array = []

    def _cluster(self, cluster_df: pandas.DataFrame):
        """
        Runs the clustering algorithm and generates a cluster label for each instance.
        :param cluster_df: Pandas Dataframe data set to cluster.
        """
        self._clustering_algorithm: SOM = SOM(dim=cluster_df.shape[1])
        logger.debug("SOM running...")
        self._clustering_algorithm.fit(cluster_df.values)
        logger.debug("SOM finished.")
        self._instance_clusters = self._clustering_algorithm.predict(cluster_df.values)
        self._unique_clusters = numpy.unique(self._instance_clusters).tolist()

    def discretize(self, data: pandas.DataFrame) -> pandas.DataFrame:
        """
        Run the clustering algorithm then create discretized features for each feature in cluster_df. Discretization steps for each feature is as follows:
        1) Get ranges (min, max) for all values in each cluster.
        2) Sort all value ranges as distinct values. Example: 3 clusters with ranges (2-7), (3-9), (1-4). Results are (1, 2, 3, 4, 7, 9).
        3) The sorted values from 2 are used as the bin edges to discretize the feature values.

        :param data: Pandas Dataframe to cluster on and to be discretized.
        :return: Pandas Dataframe of discretized data with same shape as cluster_df
        """
        self._cluster(data)

        discretized_df = pandas.DataFrame(columns=[f"Discretized {column}" for column in data.columns], index=data.index, dtype=int)

        logger.debug(f"Discretizing {len(data.columns)} columns.")
        for column in data.columns:
            column_values = data[column].values
            discretized_column = self._discretize_values(column_values)
            discretized_column_name = f"Discretized {column}"
            discretized_df[discretized_column_name] = discretized_column

        assert bool(discretized_df.isna().values.any()) is False, f"NaN present in discretized data {discretized_df}"
        logger.debug(f"Discretized {len(data.columns)} columns.")
        return discretized_df

    def _discretize_values(self, values: numpy.array) -> numpy.array:
        """
        Converts a list of values to discrete integer values according to their cluster labels. See discretize() for full details.
        :param values: Numpy array of values to be discretized.
        :return: A discretized Numpy array the same length as values.
        """
        assert len(self._instance_clusters) == len(values), "Cluster labels are not the same length as values to be discretized!"

        cluster_ranges = []
        for cluster_label in self._unique_clusters:
            # Get the values for this cluster and add to the ranges. Actually keeping track of each cluster's range is irrelevant, as we are just sorting all values.
            cluster_values = values[numpy.where(self._instance_clusters == cluster_label)]
            cluster_min = min(cluster_values)
            cluster_max = max(cluster_values)
            cluster_ranges.append(cluster_min)
            cluster_ranges.append(cluster_max)

        bins = sorted(cluster_ranges)
        discretized_values = numpy.digitize(x=values, bins=bins)

        return discretized_values


