from fastapi import FastAPI, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
import asyncio
import calendar
import json
from backend.db import invoice_collection

app = FastAPI()

# ─── CORS middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],     
)

# Constants
ORG_ID   = "<Org ID>"
USER_ID  = "<User ID>"
COOKIE   = f"<Hyperbots Token>"
COMMON_HDRS = {"accept": "application/json", "cookie": COOKIE}
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://p2p.hyperbots.com",
    "referer": "https://p2p.hyperbots.com/",
    "user-agent": "Mozilla/5.0",
}

def to_epoch_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def get_range(period: str) -> tuple[int, int]:
    period = period.lower()              # normalize
    today = datetime.today()

    if period == "monthly":
        first_day_last_month = today.replace(day=1) - timedelta(days=1)
        start = first_day_last_month.replace(day=1)
        end = first_day_last_month.replace(
            day=calendar.monthrange(first_day_last_month.year,
                                    first_day_last_month.month)[1]
        )
    elif period == "quarterly":
        current_quarter = (today.month - 1) // 3 + 1
        last_q_end = today.replace(month=(current_quarter - 1) * 3,
                                   day=1) - timedelta(days=1)
        last_q_start = last_q_end.replace(day=1).replace(month=last_q_end.month - 2)
        start, end = last_q_start, last_q_end
    elif period == "yearly":
        start = today.replace(year=today.year - 1, month=1, day=1)
        end   = today.replace(year=today.year - 1, month=12, day=31)
    else:
        raise ValueError("Invalid period")

    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    end = end.replace(hour=23, minute=59, second=59, microsecond=0)

    return to_epoch_ms(start), to_epoch_ms(end)


async def fetch_po_count(client: httpx.AsyncClient, start: int, end: int):
    try:
        print("Calling PO API with:", start, end)

        payload = {
  "my_prs": {
    "andFilters": [
      [
        {
          "field": "info_meta_data.created_on",
          "operation": "RANGE",
          "values": [start, end],
          "type": "DATE",
          "clause": "FILTER"
        },
        {
          "field": "type",
          "operation": "IN",
          "values": ["PURCHASE_REQUISITION"],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.created_by",
          "operation": "IN",
          "values": ["87f50a59-b24c-4550-bd67-7c5eaec9755d"],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.status",
          "operation": "NOT_IN",
          "values": ["DELETED"],
          "type": "TEXT",
          "clause": "MUST_NOT"
        }
      ]
    ],
    "indexName": "mongodb.document-hub-db.documents-a0010681-b5cf-427f-9451-ede87ef19a1e",
    "metricField": "document.entities.gross_amount.value.display_val"
  },
  "for_my_review": {
    "andFilters": [
      [
        {
          "field": "info_meta_data.created_on",
          "operation": "RANGE",
          "values": [start, end],
          "type": "DATE",
          "clause": "FILTER"
        },
        {
          "field": "type",
          "operation": "IN",
          "values": ["PURCHASE_REQUISITION"],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.status",
          "operation": "IN",
          "values": [
            "PENDING_APPROVAL",
            "CHANGES_REQUESTED",
            "REVIEW_REQUIRED"
          ],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.delegated_to",
          "operation": "IN",
          "values": ["87f50a59-b24c-4550-bd67-7c5eaec9755d"],
          "type": "TEXT",
          "clause": "SHOULD"
        },
        {
          "field": "info_meta_data.assigned_to",
          "operation": "IN",
          "values": ["87f50a59-b24c-4550-bd67-7c5eaec9755d"],
          "type": "TEXT",
          "clause": "SHOULD"
        }
      ]
    ],
    "orFilters": [[]],
    "filterQuery": "",
    "indexName": "mongodb.document-hub-db.documents-a0010681-b5cf-427f-9451-ede87ef19a1e",
    "metricField": "document.entities.gross_amount.value.display_val"
  },
  "pending_on_others": {
    "andFilters": [
      [
        {
          "field": "info_meta_data.created_on",
          "operation": "RANGE",
          "values": [start, end],
          "type": "DATE",
          "clause": "FILTER"
        },
        {
          "field": "type",
          "operation": "IN",
          "values": ["PURCHASE_REQUISITION"],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.status",
          "operation": "IN",
          "values": [
            "PENDING_APPROVAL",
            "CHANGES_REQUESTED",
            "REVIEW_REQUIRED"
          ],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.assigned_to",
          "operation": "NOT_IN",
          "values": ["87f50a59-b24c-4550-bd67-7c5eaec9755d"],
          "type": "TEXT",
          "clause": "MUST_NOT"
        },
        {
          "field": "info_meta_data.delegated_to",
          "operation": "NOT_IN",
          "values": ["87f50a59-b24c-4550-bd67-7c5eaec9755d"],
          "type": "TEXT",
          "clause": "MUST_NOT"
        }
      ]
    ],
    "orFilters": [[]],
    "filterQuery": "",
    "indexName": "mongodb.document-hub-db.documents-a0010681-b5cf-427f-9451-ede87ef19a1e",
    "metricField": "document.entities.gross_amount.value.display_val"
  },
  "processed_prs": {
    "andFilters": [
      [
        {
          "field": "info_meta_data.created_on",
          "operation": "RANGE",
          "values": [start, end],
          "type": "DATE",
          "clause": "FILTER"
        },
        {
          "field": "type",
          "operation": "IN",
          "values": ["PURCHASE_REQUISITION"],
          "type": "TEXT",
          "clause": "FILTER"
        },
        {
          "field": "info_meta_data.status",
          "operation": "IN",
          "values": ["APPROVED", "INACTIVE", "AUTO_APPROVED"],
          "type": "TEXT",
          "clause": "FILTER"
        }
      ]
    ],
    "orFilters": [[]],
    "filterQuery": "",
    "indexName": "mongodb.document-hub-db.documents-a0010681-b5cf-427f-9451-ede87ef19a1e",
    "metricField": "document.entities.gross_amount.value.display_val"
  },
  "purchase_orders": {
    "andFilters": [
      [
        {
          "field": "created_at",
          "operation": "RANGE",
          "values": [start, end],
          "type": "DATE",
          "clause": "FILTER"
        },
        {
          "field": "source",
          "operation": "IN",
          "values": ["HYPRBOTS"],
          "type": "TEXT",
          "clause": "FILTER"
        }
      ]
    ],
    "orFilters": [[]],
    "filterQuery": "",
    "indexName": "datahubdb.public.purchase_order_detail_json-a0010681-b5cf-427f-9451-ede87ef19a1e",
    "metricField": "gross_amount"
  }
}


        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "cookie": "<HYPRBOTS_TOKEN>"
        }

        url = "https://api.hyperbots.com/workitems/search/v2/a0010681-b5cf-427f-9451-ede87ef19a1e/summary/pr"

        res = await client.post(url, json=payload, headers=headers)
        res.raise_for_status()

        data = res.json()
        print("PO API Response:", data)
        return data.get("count")

    except httpx.HTTPStatusError as e:
        print(f"PO API failed: {e}")
        print("Response text:", e.response.text)
        return None
    except Exception as e:
        print(f"Unhandled PO API error: {e}")
        return None




async def fetch_invoice_count(client: httpx.AsyncClient, start: int, end: int) -> Optional[int]:
    try:
        filters = [
            {
                "field": "created_at",
                "operation": "RANGE",
                "values": [start, end],
                "type": "DATE"
            },
            {
                "field": "invoice_status",
                "operation": "NOT_IN",
                "values": ["INACTIVE"],
                "type": "TEXT"
            }
        ]
        params = {
            "filter": json.dumps(filters, separators=(",", ":")),  # compact JSON
            "indexName": f"datahubdb.public.purchase_invoice_json-{ORG_ID}",
            "groupBy": "invoice_status",
            "includeField": "gross_amount"
        }

        url = f"https://api.hyperbots.com/workitems/search/v1/{ORG_ID}/summary"
        res = await client.get(url, headers=COMMON_HDRS, params=params, timeout=10)
        res.raise_for_status()

        data = res.json()
        print("Invoice API Response:", data)
        return data.get("total_count")
    except Exception as e:
        print(f"Invoice API failed: {e}")
        if isinstance(e, httpx.HTTPStatusError):
            print("Response text:", e.response.text)
        return None


async def fetch_accrual_count(client: httpx.AsyncClient, start: int, end: int) -> Optional[int]:
    try:
        or_filters = [
            [   # block‑1 (all accrual except deleted / draft)
                {"field":"info_meta_data.created_on","operation":"RANGE","values":[start,end],"type":"DATE","clause":"FILTER"},
                {"field":"type","operation":"IN","values":["ACCRUAL"],"type":"TEXT","clause":"FILTER"},
                {"field":"info_meta_data.status","operation":"NOT_IN","values":["DELETED","DRAFT"],"type":"TEXT","clause":"MUST_NOT"}
            ],
            [   # block‑2 (drafts created by me)
                {"field":"info_meta_data.created_on","operation":"RANGE","values":[start,end],"type":"DATE","clause":"FILTER"},
                {"field":"type","operation":"IN","values":["ACCRUAL"],"type":"TEXT","clause":"FILTER"},
                {"field":"info_meta_data.status","operation":"IN","values":["DRAFT"],"type":"TEXT","clause":"FILTER"},
                {"field":"info_meta_data.created_by","operation":"IN","values":[USER_ID],"type":"TEXT","clause":"FILTER"}
            ]
        ]
        params = {
            "orFilters": json.dumps(or_filters, separators=(",", ":")),
            "indexName": f"mongodb.document-hub-db.documents-{ORG_ID}",
            "aggregateField": "info_meta_data.status",
            "metricField": "document.entities.gross_amount.value.display_val"
        }

        url = f"https://api.hyperbots.com/workitems/search/v2/{ORG_ID}/summary"
        res = await client.get(url, headers=COMMON_HDRS, params=params, timeout=10)
        res.raise_for_status()

        data = res.json()
        print("Accrual API Response:", data)
        return data.get("total_count")
    except Exception as e:
        print(f"Accrual API failed: {e}")
        if isinstance(e, httpx.HTTPStatusError):
            print("Response text:", e.response.text)
        return None


async def get_counts(start: int, end: int):
    async with httpx.AsyncClient() as client:
        po, invoice, accrual = await asyncio.gather(
            fetch_po_count(client, start, end),
            fetch_invoice_count(client, start, end),
            fetch_accrual_count(client, start, end),
        )
        return {
            "po_count": po,
            "invoice_count": invoice,
            "accrual_count": accrual
        }

from fastapi import Response

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/{period}")
async def get_period_summary(period: str):
    try:
        print(f"Received request for: {period}")
        start, end = get_range(period)
        print(f"Time range: {start} to {end}")
        result = await get_counts(start, end)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)} 

class InvoiceModel(BaseModel):
    id: str = Field(...)
    customerName: str
    createdAt: str
    billingPeriod: str
    documentCounts: Dict[str, int]
    pricing: Dict[str, float]
    totalAmount: float
    status: str

@app.post("/invoices/", response_model=InvoiceModel)
async def create_invoice(invoice: InvoiceModel):
    invoice_dict = invoice.dict()
    await invoice_collection.insert_one(invoice_dict)
    return invoice

@app.get("/invoices/", response_model=List[InvoiceModel])
async def get_invoices():
    invoices = []
    async for invoice in invoice_collection.find():
        invoice["_id"] = str(invoice["_id"])  # Convert ObjectId to string if needed
        invoices.append(InvoiceModel(**invoice))
    return invoices 

@app.patch("/invoices/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, status: str = Body(...)):
    result = await invoice_collection.update_one(
        {"id": invoice_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 1:
        return {"message": "Status updated"}
    else:
        return {"message": "Invoice not found or status unchanged"} 