from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from exceptions.global_exception import GlobalException
from services import farmer_services, salesrep_services, view_models_services, admin_services

app = FastAPI(
    title="My FastAPI App",
    description="A basic FastAPI routing template",
    version="1.0.0"
)


@app.exception_handler(GlobalException)
async def app_exception_handler(request: Request, exc: GlobalException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

origins = [
    "http://localhost:3000",  # React/Vite/Next.js frontend
    "http://127.0.0.1:3000",  # Alternate local frontend URL
    # Add your actual deployed frontend URL here in production
    "https://www.fieldiq.ph",
    "https://fieldiq.ph",
    "https://field-iq-three.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    # Or use ["*"] to allow all origins (not recommended for prod)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],                # Allows all HTTP methods
    allow_headers=["*"],                # Allows all headers
)

# Include routes from services
app.include_router(farmer_services.router, prefix="/farmer", tags=["Farmer"])
app.include_router(salesrep_services.router,
                   prefix="/salesrep", tags=["Sales Rep"])
app.include_router(view_models_services.router,
                   prefix="/ViewModels", tags=["View Models"])
app.include_router(admin_services.router,
                   prefix="/admin", tags=["Admin"])

# Root endpoint
@app.get("/")
async def helloworld():
    return {"message": "Hello World"}
