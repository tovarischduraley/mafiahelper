import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from dependencies import container
from usecases import GetPlayersUseCase

app = FastAPI(title="MafiaAPI")
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/players", description="returns players for last game in draft")
async def get_players(request: Request) -> HTMLResponse:
    uc: GetPlayersUseCase = container.resolve(GetPlayersUseCase)
    players = await uc.get_players_for_stream()
    s = sorted(players, key=lambda p: p.number) if players else None
    return templates.TemplateResponse(request=request, name="main.html", context={"players": s})


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)

