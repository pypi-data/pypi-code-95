"""
Introduction
------------

ClusteringKey objects allow you to specify clustering of a collection on a 
subset of fields at creation time.

For more information on clustering, refer to `the official documentation 
<https://rockset.com/docs/>`_.

Example of basic clustering
---------------------------
::

    from rockset import Client

    rs = Client()

    clustering_key = [
        rs.ClusteringKey.clusteringField(
            field_name="country",
            cluster_type="AUTO"
        ),
        rs.ClusteringKey.clusteringField(
            field_name="occupation",
            cluster_type="AUTO"
        )
    ]

    # Create a collection clustered on (country, occupation)
    collection = rs.Collection.create(name="collection", clustering_key=clustering_key)

"""


class ClusteringKey(object):
    def __init__(self, field_name, cluster_type):
        self.field_name = field_name
        self.type = cluster_type

    def __str__(self):
        return str(vars(self))

    def __iter__(self):
        for k, v in vars(self).items():
            yield (k, v)

    @classmethod
    def clusteringField(cls, field_name, cluster_type):
        """Creates a new clustering field

        Args:
            field_name(str): Name of the field to cluster on
            cluster_type(str): The type of clustering scheme to apply to
              this field. Currently supported values: ['AUTO']
        """

        return cls(field_name, cluster_type)
