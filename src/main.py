from fastapi import FastAPI
from menu.router import router as router_menu
from database import init_db

app = FastAPI(
    title='Menu App'
)

app.include_router(router_menu)

@app.on_event('startup')
async def startup_event():
    await init_db()