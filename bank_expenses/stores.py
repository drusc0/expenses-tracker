import logging

from google.cloud import datastore


logger = logging.getLogger(__name__)
# google data store, storage of preference
datastore_client = datastore.Client()


# DatastoreDB
# wrapper around datastore object
# this will be used to make the needed calls to datastores
# get - all and single entities
# update - update entity (remove visibility, update category, etc)
class DatastoreDB:
    def __init__(self):
        self.datastore = datastore.Client()

    def get_all(self):
        return self.query(kind="expenses", order=['-expense_date'])

    def query(self, kind, order):
        return self.datastore.query(kind=kind, order=order).fetch()