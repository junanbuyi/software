from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    chart_data,
    dataset_records,
    datasets,
    files,
    market,
    models,
    prediction_details,
    predictions,
    weather,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(datasets.router)
api_router.include_router(dataset_records.router)
api_router.include_router(files.router)
api_router.include_router(models.router)
api_router.include_router(predictions.router)
api_router.include_router(prediction_details.router)
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(chart_data.router, prefix="/chart", tags=["chart"])
api_router.include_router(market.router, prefix="/market", tags=["market"])

