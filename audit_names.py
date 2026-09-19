import sys
import re
import database

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# BẢNG TỪ ĐIỂN TÊN RIÊNG & THUẬT NGỮ CHUẨN TIÊN HIỆP
REPLACEMENTS = [
    # 1. Thế lực, tổ chức
    (r'\b[Hh]ắc\s+[Mm]ạng\b', 'Hắc Minh', '黑盟'),
    (r'\b[Ll]iên\s+[Mm]inh\s+[Đđ]en\b', 'Hắc Minh', '黑盟'),
    (r'\b[Hh]ắc\s+[Ll]iên\s+[Mm]inh\b', 'Hắc Minh', '黑盟'),
    (r'\bLiên [Mm]inh Đen\b', 'Hắc Minh', '黑盟'),
    (r'\bliên minh đen\b', 'Hắc Minh', '黑盟'),
    (r'\b[Đđ]oàn [Tt]hanh [Tt]ra [Dd]òng [Mm]áu\b', 'Đoàn Thị Sát Huyết Tộc', '血族視察團'),
    (r'\b[Dd]òng [Mm]áu\b', 'Huyết Tộc', '血族'),
    (r'\b[Tt]ộc [Mm]áu\b', 'Huyết Tộc', '血族'),
    (r'\btộc máu\b', 'Huyết Tộc', '血族'),
    (r'\bNgười Cây\b', 'Mộc Linh Tộc', '木靈族'),
    (r'\btộc Mộc Linh\b', 'Mộc Linh Tộc', '木靈族'),
    (r'\bTộc Mộc Linh\b', 'Mộc Linh Tộc', '木靈族'),

    # 2. Nhân vật chính & Bằng hữu đồng hành
    (r'\b[Đđ]en và [Vv]àng\b', 'Hắc Hoàng', '黑黃'),
    (r'\b[Đđ]en [Vv]àng\b', 'Hắc Hoàng', '黑黃'),
    (r'\bHunter\b', 'Hàn Đặc', '韓特'),
    (r'\bhunter\b', 'Hàn Đặc', '韓特'),
    (r'\bHaiteng\b', 'Hải Đằng', '海騰'),
    (r'\bAokiji\b', 'Thanh Trĩ', '青雉'),
    (r'\baokiji\b', 'Thanh Trĩ', '青雉'),
    (r'\bchim trĩ xanh\b', 'Thanh Trĩ', '青雉'),
    (r'\bHoang Nguyệt\b', 'Hoang Nhạc', '荒岳'),
    (r'\bhoang nguyệt\b', 'Hoang Nhạc', '荒岳'),
    (r'\bHứa Thái Vi\b', 'Hứa Thải Vi', '許採薇'),
    (r'\bKỷ Vô Thường\b', 'Quý Vô Thường', '季無常'),

    # 3. Tiên Quân, Ma Tôn
    (r'\bNuốt Mặt Trời\b', 'Thôn Nhật', '吞日'),
    (r'\bCổng Khổng Lồ\b', 'Cự Môn', '巨門'),
    (r'\bRồng Man\b', 'Man Long', '蠻龍'),
    (r'\bNăm Linh\b', 'Ngũ Linh', '五靈'),

    # 4. Địa danh, Pháp bảo, Thần thú
    (r'\bBiển Vô Tích\b', 'Vô Tẫn Hải', '無燼海'),
    (r'\bRồng Vàng Ứng Hoàng\b', 'Hoàng Kim Ứng Long', '黃金應龍'),
    (r'\bỨng Hoàng\b', 'Ứng Long', '應龍'),
]

# Chuẩn hóa các tiêu đề chương đặc thù
TITLE_FIXES = {
    2007: "Chương 2007: Đoàn Thị Sát Huyết Tộc",
    2055: "Chương 2055: Động Hướng Của Hắc Hoàng",
    2093: "Chương 2093: Thí Nghiệm Lớn Của Hắc Minh",
    2145: "Chương 2145: Trở Lại Vô Tẫn Hải",
    2147: "Chương 2147: Hoàng Kim Ứng Long",
    2151: "Chương 2151: Thanh Trĩ Và Bạch Tố Y",
    2156: "Chương 2156: Trận Chiến Song Long",
    2157: "Chương 2157: Long Tranh Hổ Đấu",
    2158: "Chương 2158: Quy Tắc Của Thợ Săn Rồng",
    2159: "Chương 2159: Chiến Thuật Của Hứa Hắc",
    2161: "Chương 2161: Bán Cự Nhân Tiên Quân",
    2163: "Chương 2163: Hợp Tác Nhiều Bên",
    2164: "Chương 2164: Ghen Tuông Tranh Giành",
    2165: "Chương 2165: Sở Hắc Tử",
    2166: "Chương 2166: Điểm Bất Thường",
    2167: "Chương 2167: Chân Tướng Liệt Dương Giáo Phái",
    2169: "Chương 2169: Thu Nhận Tái Biên",
    2171: "Chương 2171: Vượt Trội Nhân Tộc",
    2174: "Chương 2174: Hoang Nhạc Cự Tổ",
    2175: "Chương 2175: Trận Chiến Thảm Liệt",
    2177: "Chương 2177: Xử Lý Hậu Sự",
    2178: "Chương 2178: Liên Minh Phản Hắc",
    2181: "Chương 2181: Cá Voi",
    2182: "Chương 2182: Hàn Ma Tôn",
    2213: "Chương 2213: Danh Hiệu Mãng Phu",
    2220: "Chương 2220: Hắc Hoàng Tiêu Thụ Đồ Gian",
}

def apply_audit_and_fix(dry_run: bool = False):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT chapter_num, title_zh, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC")
    rows = c.fetchall()

    total_changes = 0
    modified_chapters = 0

    print("=" * 75)
    print(" BẮT ĐẦU AUDIT VÀ ĐỒNG NHẤT BẢN DỊCH CHO TOÀN BỘ CSDL NOVEL.DB")
    print(f" Chế độ: {'[DRY RUN - CHỈ KIỂM TRA]' if dry_run else '[THỰC THI CHÍNH THỨC]'}")
    print("=" * 75)

    for r in rows:
        chap_num = r["chapter_num"]
        t_vi = r["title_vi"] or ""
        c_vi = r["content_vi"] or ""
        
        orig_t = t_vi
        orig_c = c_vi

        # 1. Chỉnh sửa tiêu đề từ bảng cố định
        if chap_num in TITLE_FIXES:
            t_vi = TITLE_FIXES[chap_num]

        # 2. Thay thế từ khóa trong tiêu đề
        for pattern, repl, _ in REPLACEMENTS:
            t_vi = re.sub(pattern, repl, t_vi)

        # 3. Thay thế từ khóa trong nội dung chương
        chap_repl_count = 0
        for pattern, repl, _ in REPLACEMENTS:
            matches = len(re.findall(pattern, c_vi))
            if matches > 0:
                chap_repl_count += matches
                c_vi = re.sub(pattern, repl, c_vi)

        if t_vi != orig_t or c_vi != orig_c:
            modified_chapters += 1
            total_changes += chap_repl_count
            if t_vi != orig_t:
                total_changes += 1
                print(f"[Chương {chap_num}] Tiêu đề mới: {t_vi} (Cũ: {orig_t})")
            
            if not dry_run:
                c.execute("""
                    UPDATE chapters 
                    SET title_vi = ?, content_vi = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE chapter_num = ?
                """, (t_vi, c_vi, chap_num))

    if not dry_run:
        conn.commit()
    conn.close()

    print("\n" + "=" * 75)
    print(f" [KẾT QUẢ] Đã chuẩn hóa {total_changes} vị trí trên {modified_chapters} chương!")
    print("=" * 75)

if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    apply_audit_and_fix(dry_run=is_dry_run)
