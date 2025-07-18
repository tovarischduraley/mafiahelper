from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from dependencies import container
from usecases import GetGamesUseCase

app = FastAPI(title="MafiaAPI")
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")


@app.get("/players", description="returns last game in draft info")
async def get_players(request: Request) -> HTMLResponse:
    uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await uc.get_last_game_in_draft()
    return templates.TemplateResponse(request=request, name="main.html", context={"game": game})
