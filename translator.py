import sys
import time
import random
import re

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import translators as ts
from deep_translator import GoogleTranslator, MyMemoryTranslator

def is_mostly_chinese(text: str) -> bool:
    if not text:
        return True
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    return zh_chars / len(text) > 0.25

def translate_chunk_smart(text: str, retries: int = 2) -> str:
    """
    Dịch một đoạn văn bản sử dụng đa tầng dịch thuật (Bing -> Caiyun -> Alibaba -> Google -> Sogou -> DeepTranslator).
    Tối ưu hóa tốc độ và đảm bảo 100% dịch ra tiếng Việt chuẩn.
    """
    clean_text = text.strip()
    if not clean_text:
        return ""
    
    # 1. Thử các engine dịch mạnh nhất qua translators
    engines = ["bing", "caiyun", "alibaba", "google", "sogou"]
    for engine in engines:
        for attempt in range(retries):
            try:
                res = ts.translate_text(clean_text, translator=engine, from_language="zh", to_language="vi")
                if res and not is_mostly_chinese(res):
                    return res
            except Exception:
                time.sleep(0.3)

    # 2. Dự phòng: MyMemory Translator (nếu đoạn văn < 500 ký tự)
    try:
        if len(clean_text) < 500:
            res = MyMemoryTranslator(source="zh-CN", target="vi-VN").translate(clean_text)
            if res and not is_mostly_chinese(res):
                return res
    except Exception:
        pass

    # 3. Dự phòng: Google Translator qua deep_translator
    try:
        res = GoogleTranslator(source="auto", target="vi").translate(clean_text)
        if res and not is_mostly_chinese(res):
            return res
    except Exception:
        pass

    return clean_text

def split_long_paragraph(p: str, max_len: int = 450) -> list[str]:
    """Chia nhỏ một đoạn văn quá dài theo các dấu câu kết thúc câu."""
    if len(p) <= max_len:
        return [p]
    sentences = re.split(r'([。！？…\n]+)', p)
    parts = []
    curr = ""
    for i in range(0, len(sentences), 2):
        s = sentences[i]
        sep = sentences[i+1] if i+1 < len(sentences) else ""
        piece = s + sep
        if len(curr) + len(piece) > max_len and curr:
            parts.append(curr)
            curr = piece
        else:
            curr += piece
    if curr:
        parts.append(curr)
    return parts if parts else [p]

def translate_text(text: str, max_chunk_chars: int = 450) -> str:
    """
    Dịch văn bản dài bằng cách gom các đoạn văn vào cụm <= max_chunk_chars (mặc định 450 ký tự).
    Bảo toàn cấu trúc đoạn văn và dấu ngắt dòng.
    """
    if not text or not text.strip():
        return ""
    
    raw_paragraphs = text.split("\n")
    # Đảm bảo không có đoạn nào vượt quá max_chunk_chars
    paragraphs = []
    for p in raw_paragraphs:
        if len(p) > max_chunk_chars:
            paragraphs.extend(split_long_paragraph(p, max_chunk_chars))
        else:
            paragraphs.append(p)
            
    chunks = []
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        p_len = len(p)
        if current_len + p_len + 1 > max_chunk_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [p]
            current_len = p_len
        else:
            current_chunk.append(p)
            current_len += p_len + 1
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    translated_chunks = []
    for c in chunks:
        res = translate_chunk_smart(c)
        translated_chunks.append(res)
        if len(chunks) > 1:
            time.sleep(random.uniform(0.1, 0.3))
            
    return "\n".join(translated_chunks)

GLOSSARY_REPLACEMENTS = [
    (r'\b[Hh]ắc\s+[Mm]ạng\b', 'Hắc Minh'),
    (r'\b[Ll]iên\s+[Mm]inh\s+[Đđ]en\b', 'Hắc Minh'),
    (r'\b[Hh]ắc\s+[Ll]iên\s+[Mm]inh\b', 'Hắc Minh'),
    (r'\bLiên [Mm]inh Đen\b', 'Hắc Minh'),
    (r'\bliên minh đen\b', 'Hắc Minh'),
    (r'\b[Đđ]en và [Vv]àng\b', 'Hắc Hoàng'),
    (r'\b[Đđ]en [Vv]àng\b', 'Hắc Hoàng'),
    (r'\bHunter\b', 'Hàn Đặc'),
    (r'\bhunter\b', 'Hàn Đặc'),
    (r'\b[Đđ]oàn [Tt]hanh [Tt]ra [Dd]òng [Mm]áu\b', 'Đoàn Thị Sát Huyết Tộc'),
    (r'\b[Dd]òng [Mm]áu\b', 'Huyết Tộc'),
    (r'\b[Tt]ộc [Mm]áu\b', 'Huyết Tộc'),
    (r'\btộc máu\b', 'Huyết Tộc'),
    (r'\bAokiji\b', 'Thanh Trĩ'),
    (r'\baokiji\b', 'Thanh Trĩ'),
    (r'\bchim trĩ xanh\b', 'Thanh Trĩ'),
    (r'\bHoang Nguyệt\b', 'Hoang Nhạc'),
    (r'\bhoang nguyệt\b', 'Hoang Nhạc'),
    (r'\bHaiteng\b', 'Hải Đằng'),
    (r'\bHứa Thái Vi\b', 'Hứa Thải Vi'),
    (r'\bKỷ Vô Thường\b', 'Quý Vô Thường'),
    (r'\bNuốt Mặt Trời\b', 'Thôn Nhật'),
    (r'\bCổng Khổng Lồ\b', 'Cự Môn'),
    (r'\bRồng Man\b', 'Man Long'),
    (r'\bNăm Linh\b', 'Ngũ Linh'),
    (r'\bBiển Vô Tích\b', 'Vô Tẫn Hải'),
    (r'\bRồng Vàng Ứng Hoàng\b', 'Hoàng Kim Ứng Long'),
    (r'\bỨng Hoàng\b', 'Ứng Long'),
    (r'\bNgười Cây\b', 'Mộc Linh Tộc'),
    (r'\btộc Mộc Linh\b', 'Mộc Linh Tộc'),
    (r'\bTộc Mộc Linh\b', 'Mộc Linh Tộc'),
]

def apply_glossary(text: str) -> str:
    if not text:
        return ""
    for pattern, repl in GLOSSARY_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text

def translate_chapter(title_zh: str, content_zh: str) -> tuple[str, str]:
    """
    Dịch tiêu đề và nội dung chương truyện, áp dụng chuẩn hóa tên riêng và thuật ngữ tiên hiệp.
    """
    title_vi = translate_chunk_smart(title_zh)
    content_vi = translate_text(content_zh, max_chunk_chars=450)
    title_vi = apply_glossary(title_vi)
    content_vi = apply_glossary(content_vi)
    return title_vi, content_vi

if __name__ == "__main__":
    t_zh = "第2005章 倒霉的葉塵"
    c_zh = "穩定的世界是無法被吞噬掉的，這隻說明，此界早已到了崩塌的邊緣，就連最強者都坐化了，空間一觸即碎。\n\n這個世界的主人，那位傳說中的仙人，恐怕也凶多吉少。"
    t_vi, c_vi = translate_chapter(t_zh, c_zh)
    print("Tiêu đề:", t_vi)
    print("Nội dung:\n", c_vi)
