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
    KIND = "expenses"
    PROJECT = "chase-expenses"

    def __init__(self):
        self.datastore = datastore.Client()

    def get_all(self):
        return self.query(kind=self.KIND, order=['-expense_date'])

    def get_by_key(self, name_or_id: str = ''):
        if name_or_id is None:
            raise KeyError(f"EntityKey ID not valid: {name_or_id}")

        if all(x.isdigit() for x in name_or_id):
            name_or_id = int(name_or_id)

        try:
            key = self.datastore.key(self.KIND, name_or_id)
            return self.datastore.get(key)
        except ValueError as err:
            logger.error(f"Fetch by key failed with error: {err}")
            raise ValueError(err)

    def query(self, kind, order):
        logger.info("querying...")
        return self.datastore.query(kind=kind, order=order).fetch()
