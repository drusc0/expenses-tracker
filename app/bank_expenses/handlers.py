import logging

from datetime import datetime, timedelta
from pytz import timezone
from optional import Optional
from typing import Dict

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
        filters = self._extract_properties_to_filter(request.query_params)
        expenses = []
        resp = [x for x in self.db.get_all(filters)]
        total_amt = sum(list(map(lambda x: float(x['amount']), resp)))

        skip = 3
        for i in range(0, len(resp), skip):
            expenses.append(resp[i:i + skip])

        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "expenses": expenses, "total_amt": total_amt}
        )

    def _extract_properties_to_filter(self, params: Dict):
        filters = []

        hide = params.get('hide', 'false')
        start_dt = params.get('start_dt', None)
        end_dt = params.get('end_dt', datetime.now().strftime('%Y-%m-%d'))
        end = datetime.strptime(end_dt, '%Y-%m-%d')

        start = end - timedelta( days = 30 )
        if start_dt:
            start = datetime.strptime(start_dt, '%Y-%m-%d')

        filters.append(('hide', '=', hide))
        filters.append(('expense_date', '<=', end.astimezone(timezone('US/Pacific'))))
        filters.append(('expense_date', '>=', start.astimezone(timezone('US/Pacific'))))

        return filters


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


class UpdateExpenseHandler(Handler):
    def __init__(self):
        super().__init__()

    def handle(self, request: Request, params: Dict):
        if not request:
            raise RuntimeError("Missing request")

        logger.info(f"Updating expense {params['expense_id']}")
        expense_id = Optional.of(params['expense_id'])
        category = Optional.of(params['category'])
        hide = Optional.of(params['hide'])

        if expense_id.is_empty():
            raise RuntimeError("Expense id should not be empty")

        try:
            self.db.update_by_key(expense_id.get(), category=category, hide=hide)
            return """
            <html>
                <head>
                    <title>Some HTML in here</title>
                </head>
                <body>
                    <h1>Successful </h1>
                </body>
            </html>
            """
        except Exception as err:
            logger.error(f"Unable to update expense id: {expense_id} - {err}")
            raise RuntimeError("Update failed")


class CreateFormHandler(Handler):
    def __init__(self, templates):
        super().__init__()
        self.templates = templates

    def handle(self, request: Request):
        return self.templates.TemplateResponse("create.html", {"request": request})

class CreateExpenseHandler(Handler):
    def __init__(self):
        super().__init__()

    def handle(self, request: Request, params: Dict):
        if not request:
            raise RuntimeError("Missing request")

        if any(x is None or x == '' for x in params.values()):
            raise RuntimeError("All fields in form need to be filled")
        params['expense_date'] = datetime.strptime(params['expense_date'], '%Y-%m-%d')\
            .astimezone(timezone('US/Pacific'))

        logger.info(f"Creating expense {params.values()}")
        try:
            key = self.db.create(**params)
            return """
            <html>
                <head>
                    <title>Some HTML in here</title>
                </head>
                <body>
                    <h1>Successful</h1>
                </body>
            </html>
            """
        except Exception as err:
            logger.error(f"Unable to create expense - {err}")
            raise RuntimeError("Update failed")
