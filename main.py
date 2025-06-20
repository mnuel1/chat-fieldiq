from fastapi import FastAPI
from services import farmer_services

app = FastAPI(
    title="My FastAPI App",
    description="A basic FastAPI routing template",
    version="1.0.0"
)

# Include routes from services
app.include_router(farmer_services.router, prefix="/farmer", tags=["Farmer"])

# Root endpoint
@app.get("/")
async def helloworld():
    return {"message": "Hello World"}
