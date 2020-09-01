"""This class contains the tools to connect, manipulate and save the data
associated with an experiment. The parametrization of the database is read
from the configuration file provided with the package.
The provided features are generic, by allowing to insert a document and create
an index on a document key.
"""

__copyright__ = """
Copyright (C) 2019 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import pymongo as pm


class ShamanDB:
    """This class contains different tools to connect and save the data associated with
    a little-shaman experiment.
    """

    def __init__(self, config):
        """Initializes the connection to the database.

        Args:
            config (dict): The information needed to reach the database.
        """
        self.db_connect = pm.MongoClient(
            host=config["host"], port=int(config["port"])
        )[config["database_name"]]

    def create_experiment_index(self):
        """Creates an index on a collection."""
        return self.db_connect["experiments"].create_index(
            [("experiment_id", pm.ASCENDING)], unique=True
        )

    def add_document(self, collection, document):
        """Adds a document to a collection.

        Args:
            collection (str): The name of the collection.
            document (dict): The data to add to the collection.
        """
        col = self.db_connect[collection]
        return col.insert_one(document)
