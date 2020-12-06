import logging

from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

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

    def handle(self, request: Request) -> HTMLResponse:
        logger.info(f"Handling expenses with request: {request}")
        expenses = []
        resp = [x for x in self.db.get_all()]
        total_amt = sum(list(map(lambda x: float(x['amount']), resp)))

        skip = 3
        for i in range(0, len(resp), skip):
            expenses.append(resp[i:i + skip])
        logger.info(f"got my request. building response {total_amt}, {expenses}")

        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "expenses": expenses, "total_amt": total_amt}
        )


class ExpenseHandler(Handler):
    def __init__(self, templates: Jinja2Templates):
        super().__init__()
        self.templates = templates

    def handle(self, request: Request) -> HTMLResponse:
        entity_key = request.path_params['expense_id']
        logger.info(f"Handling expense id: {entity_key} with request: {request}")

        try:
            expense = self.db.get_by_key(entity_key)
        except ValueError as err:
            logger.error(f"Unable to find expense id: {entity_key} - {err}")
            raise RuntimeError("Expense not found.")

        return self.templates.TemplateResponse(
            "expenseid.html",
            {"request": request, "expense": expense, "total_amt": float(expense['amount'])}
        )
