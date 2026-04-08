from fastapi import FastAPI
from app.routers import contacts,todaydeals,products,orders,users,specialoccation
from fastapi.middleware.cors import CORSMiddleware


app= FastAPI(title="CozyEasy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router)
app.include_router(todaydeals.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(specialoccation.router)


