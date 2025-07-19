from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "<MongoDB Connection String>"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.invoice_dashboard  
invoice_collection = database.get_collection("invoices") 