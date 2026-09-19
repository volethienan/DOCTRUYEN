import os
import sys
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import hashlib
from collections import OrderedDict
import edge_tts

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

# ==========================================================================
# EDGE TTS STUDIO NEURAL VOICES API
# ==========================================================================
TTS_CACHE = OrderedDict()
MAX_TTS_CACHE = 200

SUPPORTED_EDGE_VOICES = {
    "vi-VN-HoaiMyNeural": {
        "id": "vi-VN-HoaiMyNeural",
        "name": "Hoài My (Nữ AI Studio)",
        "gender": "Female",
        "desc": "Truyền cảm, dịu dàng, phát âm tự nhiên chuẩn MC"
    },
    "vi-VN-NamMinhNeural": {
        "id": "vi-VN-NamMinhNeural",
        "name": "Nam Minh (Nam AI Studio)",
        "gender": "Male",
        "desc": "Trầm ấm, hào sảng, cực hợp truyện Tiên hiệp / Kiếm hiệp"
    }
}

@app.get("/api/tts/voices")
async def api_tts_voices():
    return list(SUPPORTED_EDGE_VOICES.values())

@app.get("/api/tts/audio")
async def api_tts_audio(text: str, voice: str = "vi-VN-HoaiMyNeural", speed: float = 1.0):
    text_clean = text.strip()
    if not text_clean:
        raise HTTPException(status_code=400, detail="Văn bản không được để trống.")

    selected_voice = voice if voice in SUPPORTED_EDGE_VOICES else "vi-VN-HoaiMyNeural"

    # Tính toán rate string theo định dạng của Edge-TTS (+25%, -10%, ...)
    speed = max(0.5, min(2.5, speed))
    pct = int((speed - 1.0) * 100)
    rate_str = f"{'+' if pct >= 0 else ''}{pct}%"

    # Kiểm tra Cache
    cache_key = hashlib.md5(f"{selected_voice}_{rate_str}_{text_clean}".encode("utf-8")).hexdigest()
    if cache_key in TTS_CACHE:
        audio_data = TTS_CACHE[cache_key]
        TTS_CACHE.move_to_end(cache_key)
        return Response(content=audio_data, media_type="audio/mpeg", headers={
            "Cache-Control": "public, max-age=86400",
            "X-TTS-Cache": "HIT"
        })

    try:
        communicate = edge_tts.Communicate(text_clean, selected_voice, rate=rate_str)
        audio_buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        audio_bytes = bytes(audio_buffer)

        # Lưu LRU Cache
        if len(TTS_CACHE) >= MAX_TTS_CACHE:
            TTS_CACHE.popitem(last=False)
        TTS_CACHE[cache_key] = audio_bytes

        return Response(content=audio_bytes, media_type="audio/mpeg", headers={
            "Cache-Control": "public, max-age=86400",
            "X-TTS-Cache": "MISS"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo giọng nói Edge-TTS: {str(e)}")


def run():
    port = int(os.environ.get("PORT", 8088))
    print(f"Khởi động Web Đọc Truyện tại http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    run()
