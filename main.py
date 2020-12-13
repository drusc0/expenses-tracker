import logging
import random
import string
import time
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from bank_expenses.handlers import ExpenseHandler, ExpensesHandler, UpdateExpenseHandler, CreateFormHandler, CreateExpenseHandler


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# fastapi objects and dependencies
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    # logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    # logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

    return response


#######################################
# Only 3 endpoints will come in handy for this project.
# 1) GET all expenses (will include a start and end date, otherwise, all)
# 2) GET
# 3) POST update the category for each of the expenses
#######################################

@app.get("/expenses", response_class=HTMLResponse)
def expenses(req: Request):
    try:
        handler = ExpensesHandler(templates)
        return handler.handle(req)
    except Exception as err:
        logger.error(f"Unable to find expenses ({err})")
        return templates.TemplateResponse("error/404.html", {"request": req})


@app.get("/expense/{expense_id}", response_class=HTMLResponse)
async def expense(expense_id, req: Request):
    try:
        handler = ExpenseHandler(templates)
        return handler.handle(req)
    except Exception as err:
        logger.error(f"Unable to find expense id: {expense_id} ({err})")
        return templates.TemplateResponse("error/404.html", {"request": req})


@app.get("/create", response_class=HTMLResponse)
async def create(req: Request):
    try:
        handler = CreateFormHandler(templates)
        return handler.handle(req)
    except Exception as err:
        logger.error(f"Something went wrong while loading create form ({err})")
        return templates.TemplateResponse("error/404.html", {"request": req})


@app.post("/createExpense")
async def create_expense(req: Request):
    try:
        body = await req.form()
        params = {
            'amount': float(body['amount']),
            'expense_date': body['date'],
            'expense_location': body['location'],
            'category': body['category'],
            'hide': body['hide']
        }
        handler = CreateExpenseHandler()
        return handler.handle(req, params)
    except Exception as err:
        logger.error(f"Unable to create expense ({err})")
        return templates.TemplateResponse("error/404.html", {"request": req})


@app.post("/updateExpense")
async def update_expense(req: Request):
    try:
        body = await req.form()
        params = {
            'expense_id': body['id'],
            'category': body['category'],
            'hide': body['hide']
        }
        handler = UpdateExpenseHandler()
        return handler.handle(req, params)
    except Exception as err:
        logger.error(f"Unable to find expense id ({err})")
        return templates.TemplateResponse("error/404.html", {"request": req})


if __name__ == '__main__':
    uvicorn.run(app)
