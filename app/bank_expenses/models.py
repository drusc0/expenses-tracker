import logging
import optional

from dataclasses import dataclass
from fastapi import Request
from typing import Optional, List


logger = logging.getLogger(__name__)


@dataclass
class ExpensesRequest:
    # Those will all be optional paramereters for the request
    # we will use them to validate, and form the queries
    categories: Optional[List[str]]
    start_dt: Optional[str]
    end_dt: Optional[str]

    @staticmethod
    def from_req(req: Request):
        if not req:
            raise AttributeError("Request and/or Query Params not available")

        categories = optional.Optional.of(req.query_params.get('categories'))
        start_dt = optional.Optional.of(req.query_params.get('start_dt'))
        end_dt = optional.Optional.of(req.query_params.get('end_dt'))

        expenses_req = ExpensesRequest(categories, start_dt, end_dt)
        logger.info(f"Generating ExpenseRequest from FastAPI Request: {expenses_req}")

        return expenses_req