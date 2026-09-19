import sys
import sqlite3
import re
from collections import Counter

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = sqlite3.connect('novel.db')
c = conn.cursor()
c.execute("SELECT chapter_num, title_vi, content_vi FROM chapters WHERE chapter_num >= 2000 ORDER BY chapter_num ASC")
rows = c.fetchall()

total_zh_chars = 0
chapters_with_zh = []
all_zh_words = Counter()
long_zh_segments = []

for chap_num, title_vi, content_vi in rows:
    text = (title_vi or "") + "\n" + (content_vi or "")
    # Find all sequences of Chinese characters
    zh_sequences = re.findall(r'[\u4e00-\u9fff]+', text)
    if zh_sequences:
        zh_char_count = sum(len(seq) for seq in zh_sequences)
        total_zh_chars += zh_char_count
        chapters_with_zh.append((chap_num, zh_char_count, len(zh_sequences)))
        for seq in zh_sequences:
            all_zh_words[seq] += 1
            if len(seq) > 5:
                long_zh_segments.append((chap_num, seq[:30]))

print(f"Total chapters with Chinese characters: {len(chapters_with_zh)} / {len(rows)}")
print(f"Total Chinese characters found: {total_zh_chars}")
print("\nTop 15 chapters with most Chinese characters:")
chapters_with_zh.sort(key=lambda x: x[1], reverse=True)
for ch, count, seqs in chapters_with_zh[:15]:
    print(f"  Chapter {ch}: {count} characters across {seqs} segments")

print("\nTop 30 most frequent Chinese words/characters:")
for word, count in all_zh_words.most_common(30):
    print(f"  {word}: {count} times")

print(f"\nLong segments (> 5 chars) found: {len(long_zh_segments)}")
for ch, seg in long_zh_segments[:10]:
    print(f"  Chapter {ch}: {seg}...")
