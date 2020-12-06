import logging

from fastapi.templating import Jinja2Templates
from fastapi import Request

from .stores import DatastoreDB


logger = logging.getLogger(__name__)


# Handler
# base class to handle requests...
# only one field necessasry, the db, but may need to inject other dependencies
class Handler:
    def __init__(self):
        self.db = DatastoreDB()

    def handle(self):
        raise NotImplementedError("Child class should implement its handler")

    def validate(self):
        raise NotImplementedError("Child class should implement its validator")


# ExpensesHandler
# will take care of the validation of the request, make the call to datastore,
# and build the response
class ExpensesHandler(Handler):
    def __init__(self, templates: Jinja2Templates):
        super().__init__()
        self.templates = templates

    def handle(self, request: Request):
        logger.info(f"Handling expenses with request: {request}")
        expenses = []
        resp = [x for x in self.db.get_all()]

        skip = 3
        for i in range(0, len(resp), skip):
            expenses.append(resp[i:i + skip])

        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "expenses": expenses}
        )
