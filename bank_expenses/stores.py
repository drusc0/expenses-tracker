import logging

from typing import List, Tuple
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

    def get_all(self, filters: List[Tuple]):
        return self.query(self.KIND, filters)

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

    def create(self, **kwargs):
        key = self.datastore.key(self.KIND)
        entity = datastore.Entity(key)
        entity.update(**kwargs)

        try:
            self.datastore.put(entity)
            return entity.key
        except Exception as err:
            logger.error(f"Unable to create new entity: {entity} ({err})")
            raise RuntimeError("Unable to create expense")

    def update_by_key(self, name_or_id: str = '', **kwargs):
        if name_or_id is None:
            raise KeyError(f"EntityKey ID not valid: {name_or_id}")

        try:
            entity = self.get_by_key(name_or_id)
            for k, v in kwargs.items():
                if not v.is_empty():
                    entity[k] = v.get()

            self.datastore.put(entity)
        except ValueError as err:
            logger.error(f"Unable to update entity ({err}")
            raise RuntimeError("Unable to update key")
        except Exception as err:
            logger.error(f"Something else went wrong while updating ({err})")
            raise RuntimeError("Unable to update key")

    def query(self, kind: str, filters: List[str]):
        logger.info("Querying...")
        q = self.datastore.query(kind=kind)
        for f in filters:
            q.add_filter(f[0], f[1], f[2])
        return q.fetch()
