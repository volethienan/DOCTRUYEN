import sys
import os
import re
import sqlite3

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("."))
import database
import translator

# 1. Các đoạn câu tiếng Trung dài còn sót lại
PHRASE_REPLACEMENTS = [
    # Câu hội thoại / tự sự dài
    (r'竟然引得两位鼎鼎大名的人物亲临', 'không ngờ lại khiến hai nhân vật đại danh đỉnh đỉnh đích thân đến'),
    (r'竟然弄来了这么多五磁神砂，居心叵测', 'lại có thể kiếm được nhiều Ngũ Từ Thần Sa như vậy, tâm địa khó lường'),
    (r'竟然弄来了这么多五磁神砂', 'lại có thể kiếm được nhiều Ngũ Từ Thần Sa như vậy'),
    (r'居心叵测', 'tâm địa khó lường'),
    (r'早就偷偷摸摸逃到了另一边', 'đã sớm lén lút trốn sang phía bên kia'),
    (r'竟然私下做了这么多布置，那个Tiêu Sán都是 giả tượng,真正的Tiêu Sán早就偷偷摸摸逃到了另一边',
     'không ngờ ngầm làm nhiều bố trí như vậy, tên Tiêu Sán kia đều là giả tượng, Tiêu Sán chân chính đã sớm lén lút trốn sang phía bên kia'),
    (r'竟然私下做了这么多布置', 'không ngờ ngầm làm nhiều bố trí như vậy'),
    (r'真正的Tiêu Sán', 'Tiêu Sán chân chính'),
    (r'那个Tiêu Sán', 'tên Tiêu Sán kia'),
    (r'都是 giả tượng', 'đều là giả tượng'),
    (r'竟然掌握了浩然正氣本源', 'không ngờ lại nắm giữ Hạo Nhiên Chính Khí Bản Nguyên'),
    (r'竟然掌握了這種力量', 'không ngờ lại nắm giữ được loại sức mạnh này'),
    (r'算是仙君中比较窮的了', 'coi như là người nghèo tương đối trong số các Tiên Quân rồi'),
    (r'難怪我搜索這麼久，都沒發現此地的異常，原來藏得這麼深',
     'Thảo nào ta tìm kiếm lâu như vậy đều không phát hiện dị thường nơi này, hóa ra lại giấu sâu như thế'),
    (r'難怪我搜索這麼久', 'Thảo nào ta tìm kiếm lâu như vậy'),
    (r'都沒發現此地的異常', 'đều không phát hiện dị thường nơi này'),
    (r'原來藏得這麼深', 'hóa ra lại giấu sâu như thế'),
    (r'连血無影都解決不了', 'ngay cả Huyết Vô Ảnh cũng không giải quyết được'),
    (r'竟然瞬间就修复了', 'không ngờ trong nháy mắt đã khôi phục lại'),
    (r'竟然不惜下此血本', 'không ngờ lại không tiếc vốn liếng như vậy'),
    (r'连七杀都能击退', 'ngay cả Thất Sát cũng có thể đẩy lui'),
    (r'裂开了一道缝隙', 'nứt ra một khe hở'),
    (r'一直没有消息', 'vẫn luôn không có tin tức'),
    (r'竟然埋有', 'lại chôn giấu'),
    (r'既然如此', 'nếu đã như thế'),
    (r'一直跟踪', 'vẫn luôn theo dõi'),
    (r'都没有', 'đều không có'),
    (r'连汤都', 'ngay cả nước canh cũng'),
    (r'连一点', 'ngay cả một chút'),
    (r'连一滴', 'ngay cả một giọt'),
    (r'算聪明', 'coi như thông minh'),
    (r'算离谱', 'coi như thái quá'),
    (r'竟然将', 'không ngờ lại đem'),
    (r'秦玄機', 'Tần Huyền Cơ'),
    (r'真正的', 'chân chính'),
    (r'一直在', 'vẫn luôn ở'),
    (r'那个', 'kẻ đó'),
    (r'还是', 'vẫn là'),
    (r'解除', 'giải trừ'),
    (r'裁决', 'Tài Quyết'),
    (r'符阵', 'phù trận'),
    (r'符文', 'phù văn'),
    (r'确实', 'thực sự'),
    (r'派人', 'phái người'),
    (r'星宮|星宫', 'Tinh Cung'),
    (r'整齐', 'chỉnh tề'),
    (r'投入', 'ném vào'),
    (r'愿意', 'nguyện ý'),
    (r'姿態', 'dáng vẻ'),
    (r'夺心', 'Đoạt Tâm'),
    (r'呵呵', 'Haha'),
    (r'勉强', 'miễn cưỡng'),
    (r'共有', 'tổng cộng có'),
    (r'介意', 'để ý'),
    (r'也拿', 'cũng không làm gì được'),
    (r'不会', 'sẽ không'),
    (r'温(?:馨|馨)?提示.*?(?=\n|$)', ''),  # Xóa dòng quảng cáo/lưu ý trình duyệt còn sót

    # Tên riêng bị dính chữ Hán
    (r'Tr楚 Hắc', 'Sở Hắc'),
    (r'楚 Hắc', 'Sở Hắc'),
    (r'姜 Thái Tổ', 'Khương Thái Tổ'),
    (r'姜 Vô Dung', 'Khương Vô Dung'),
    (r'gia tộc姜', 'gia tộc Khương'),
    (r'nhà họ姜', 'nhà họ Khương'),
    (r'姬 Thiên Mệnh', 'Cơ Thiên Mệnh'),
    (r'Thái Âm仙', 'Thái Âm Tiên'),

    # Các từ 2 chữ phổ biến
    (r'竟然', 'không ngờ'),
    (r'根本', 'căn bản'),
    (r'既然', 'nếu đã'),
    (r'一直', 'vẫn luôn'),
    (r'就是', 'chính là'),
    (r'明明', 'rõ ràng'),
    (r'都是', 'đều là'),
    (r'不过|不過', 'tuy nhiên'),
    (r'这时|這時', 'lúc này'),

    # Từ 1 chữ Hán đơn lẻ lọt vào câu tiếng Việt
    (r'\bngươi\s*可是\b', 'ngươi chính là'),
    (r'\bNgươi\s*可是\b', 'Ngươi chính là'),
    (r'\bta\s*可是\b', 'ta chính là'),
    (r'\bTa\s*可是\b', 'Ta chính là'),
    (r'\bchúng ta\s*可是\b', 'chúng ta chính là'),
    (r'\bChúng ta\s*可是\b', 'Chúng ta chính là'),
    (r'可是', 'thế nhưng'),

    (r'huyết\s*脉', 'huyết mạch'),
    (r'pháp\s*則|pháp\s*则', 'pháp tắc'),
    (r'kiếm\s*修', 'kiếm tu'),
    (r'ma\s*族', 'Ma Tộc'),
    (r'dị\s*族|tộc\s*異', 'dị tộc'),
    (r'tiên\s*僵', 'tiên cương'),
    (r'liên\s*界', 'liên giới'),
    (r'phá\s*局', 'phá cục'),
    (r'phản\s*噬', 'phản phệ'),
    (r'khí\s*爽', 'khí sảng'),
    (r'cực\s*致', 'cực hạn'),
    (r'toàn\s*盛', 'toàn thịnh'),
    (r'linh\s*台', 'linh đài'),
    (r'cải\s*造', 'cải tạo'),
    (r'triệu\s*召|đã\s*召\s*tập', 'đã triệu tập'),
    (r'chữ\s*[“"]卍[”"]', 'chữ “Vạn” (卍)'),
    (r'hai mươi\s*枚', 'hai mươi viên'),
    (r'xé\s*咬', 'xé cắn'),
    (r'bị\s*炸\s*bay', 'bị nổ tung bay'),
    (r'vô\s*奈', 'bất đắc dĩ'),
    (r'tuyệt\s*境', 'tuyệt cảnh'),
    (r'Bạch Tr织', 'Bạch Dệt'),
    (r'Bạch\s*Tr织', 'Bạch Dệt'),
    (r'tớ\s*就\s*biết', 'đã sớm biết'),
    (r'gia tộc Giang\s*愿\s*phục', 'gia tộc Giang nguyện quy phục'),
    (r'[Nn]gười ngoài\s*虽\s*tò mò', 'Người ngoài tuy tò mò'),
    (r'chữ\s*[“"\'\s]*卍[”"\'\s]*', 'chữ “Vạn” (卍)'),
    (r'卍', 'Vạn'),
    (r'愿', 'nguyện'),
    (r'虽', 'tuy'),
    (r'就', 'liền'),
    (r'织', 'dệt'),

    (r'rồng\s*符', 'long phù'),
    (r'linh\s*符', 'linh phù'),
    (r'tiên\s*符', 'tiên phù'),
    (r'bảo\s*符', 'bảo phù'),
    (r'tờ\s*符', 'tờ phù'),
    (r'lá\s*符', 'lá phù'),
    (r'đạo\s*符', 'đạo phù'),
    (r'Phiên\s*符', 'Phiên phù'),
    (r'Phù\s*符', 'Phù văn'),
    (r'符', 'phù'),

    (r'cũng\s*算', 'cũng coi như'),
    (r'còn\s*算', 'còn tính là'),
    (r'mới\s*算', 'mới tính là'),
    (r'không\s*算', 'không tính là'),
    (r'có\s*算', 'có tính là'),
    (r'算\s*là', 'coi như là'),
    (r'算', 'coi như'),

    (r'Th\s*碎\s*Long Ngâm', 'Toái Long Ngâm'),
    (r'Thanh Long Th\s*碎', 'Thanh Long Toái'),
    (r'T\s*碎\s*Linh Đan', 'Toái Linh Đan'),
    (r'chữ\s*[——–-]*\s*[“"]碎[”"]', 'chữ “Toái” (Vỡ)'),
    (r'碎', 'vỡ vụn'),

    (r'phá\s*阵', 'phá trận'),
    (r'hàm\s*阵', 'hàm trận'),
    (r'trận\s*阵', 'trận pháp'),
    (r'bàn\s*阵', 'trận bàn'),
    (r'阵', 'trận'),

    (r'thỉnh thoảng\s*派\s*người', 'thỉnh thoảng phái người'),
    (r'chưa\s*派\s*người', 'chưa phái người'),
    (r'phái\s*派', 'phái'),
    (r'派', 'phái'),

    (r'vô\s*影', 'vô ảnh'),
    (r'Thiên\s*影', 'Thiên Ảnh'),
    (r'影', 'ảnh'),

    (r'nguyện\s*愿', 'nguyện'),
    (r'khó\s*得', 'hiếm có'),
    (r'khó\s*được', 'hiếm có'),
    (r'lại\s*又', 'lại'),
    (r'nhưng\s*又', 'nhưng lại'),
    (r'liền\s*就', 'liền'),
    (r'r\s*裂', 'rách toạc'),
    (r'người ngoài\s*虽\s*tò mò', 'người ngoài tuy tò mò'),
    (r'đan\s*织', 'đan xen'),
    (r'hiện\s*呈', 'hiện ra'),
    (r'呈\s*hiện', 'hiện ra'),
    (r'quy\s*則|quy\s*tắc', 'quy tắc'),
    (r'則|则', 'quy tắc'),
    (r'竟', 'lại'),
    (r'连', 'ngay cả'),
]

def clean_text_chinese(text: str) -> tuple[str, int]:
    if not text:
        return text, 0
    
    orig = text
    changes = 0
    
    for pattern, repl in PHRASE_REPLACEMENTS:
        matches = len(re.findall(pattern, text))
        if matches > 0:
            changes += matches
            text = re.sub(pattern, repl, text)
            
    return text, changes

def audit_and_clean_all(dry_run: bool = False):
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT chapter_num, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC")
    rows = c.fetchall()
    
    total_cleaned = 0
    modified_chapters = 0
    remaining_zh_list = []
    
    print("=" * 75)
    print(f" TIẾN TRÌNH RÀ SOÁT VÀ LÀM SẠCH TỪ TIẾNG TRUNG BỊ SÓT (CHỮ HÁN)")
    print(f" Chế độ: {'[DRY RUN - KIỂM TRA TRƯỚC]' if dry_run else '[THỰC THI CHÍNH THỨC]'}")
    print("=" * 75)
    
    for r in rows:
        chap_num = r["chapter_num"]
        t_vi = r["title_vi"] or ""
        c_vi = r["content_vi"] or ""
        
        orig_t = t_vi
        orig_c = c_vi
        
        new_t, t_changes = clean_text_chinese(t_vi)
        new_c, c_changes = clean_text_chinese(c_vi)
        
        # Đảm bảo áp dụng lại glossary cho đồng nhất
        new_t = translator.apply_glossary(new_t)
        new_c = translator.apply_glossary(new_c)
        
        # Kiểm tra nếu còn sót ký tự chữ Hán nào
        remaining = re.findall(r'[\u4e00-\u9fff]+', new_t + " " + new_c)
        if remaining:
            remaining_zh_list.append((chap_num, remaining))
            
        if new_t != orig_t or new_c != orig_c:
            modified_chapters += 1
            total_cleaned += (t_changes + c_changes)
            if not dry_run:
                c.execute("""
                    UPDATE chapters 
                    SET title_vi = ?, content_vi = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE chapter_num = ?
                """, (new_t, new_c, chap_num))
                
    if not dry_run:
        conn.commit()
    conn.close()
    
    print(f"\n[KẾT QUẢ] Đã làm sạch và sửa {total_cleaned} vị trí sót trên {modified_chapters} chương!")
    print(f"Số chương còn ký tự chữ Hán chưa xử lý: {len(remaining_zh_list)}")
    if remaining_zh_list:
        print("\nCác ký tự chữ Hán còn lại:")
        for ch, rem in remaining_zh_list:
            print(f"  Chương {ch}: {rem}")

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    audit_and_clean_all(dry_run=dry)
