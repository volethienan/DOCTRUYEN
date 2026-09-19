import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="Web Đọc Truyện - Xà Tiên")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def on_startup():
    database.init_db()

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    novel = database.get_novel_info()
    chapters = database.get_chapters_list(limit=1000)
    stats = database.get_stats()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "novel": novel,
            "chapters": chapters,
            "stats": stats
        }
    )

@app.get("/chapter/{chapter_num}", response_class=HTMLResponse)
async def read_chapter(request: Request, chapter_num: int):
    chapter = database.get_chapter(chapter_num)
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chương {chapter_num} chưa có trong dữ liệu.")
        
    prev_chap, next_chap = database.get_prev_next_chapter(chapter_num)
    
    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            "chapter": chapter,
            "prev_chap": prev_chap,
            "next_chap": next_chap
        }
    )

@app.get("/api/stats")
async def api_stats():
    return database.get_stats()

@app.get("/api/chapters")
async def api_chapters(limit: int = 100, offset: int = 0):
    return database.get_chapters_list(limit=limit, offset=offset)

def run():
    port = int(os.environ.get("PORT", 8088))
    print(f"Khởi động Web Đọc Truyện tại http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    run()
