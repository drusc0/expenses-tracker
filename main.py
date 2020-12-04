from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from google.cloud import datastore

# fastapi objects and dependencies
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# google data store, storage of preference
datastore_client = datastore.Client()


@app.get("/")
async def root():
    return {"message": "Hello World"}


#######################################
# Only 3 endpoints will come in handy for this project.
# 1) GET all expenses (will include a start and end date, otherwise, all)
# 2) GET
# 3) POST update the category for each of the expenses
#######################################

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(req: Request):
    entities = []
    query = datastore_client.query(kind='expenses')

    for e in query.fetch():
        entities.append(e)

    expenses = []
    skip = 3
    for i in range(0, len(entities), skip):
        expenses.append(entities[i:i+skip])

    return templates.TemplateResponse("index.html", {
        "request": req,
        "expenses": expenses
    })

@app.get("/expense/{entity_id}")
async def expense(entity_id):
    return {'entity_id': entity_id}

@app.post("/update_category/{entity_id}")
async def update_category(entity_id):
    pass