from fastapi import FastAPI
from storage.database import init_db
from storage.products.routers import api_router as product_router
from storage.orders.routers import api_router as order_router
from fastapi.responses import HTMLResponse
app = FastAPI()

init_db()

app.include_router(product_router)
app.include_router(order_router)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "Управление складом - Тестовое задание"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)