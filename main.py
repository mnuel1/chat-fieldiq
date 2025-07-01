from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import farmer_services

app = FastAPI(
    title="My FastAPI App",
    description="A basic FastAPI routing template",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",  # React/Vite/Next.js frontend
    "http://127.0.0.1:3000",  # Alternate local frontend URL
    # Add your actual deployed frontend URL here in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Or use ["*"] to allow all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],                # Allows all HTTP methods
    allow_headers=["*"],                # Allows all headers
)

# Include routes from services
app.include_router(farmer_services.router, prefix="/farmer", tags=["Farmer"])

# Root endpoint
@app.get("/")
async def helloworld():
    return {"message": "Hello World"}
