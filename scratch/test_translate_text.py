import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
import translator

c = database.get_chapter(2002)
text = c["content_zh"]
print(f"Content length: {len(text)}")

paragraphs = text.split("\n")
chunks = []
current_chunk = []
current_len = 0
for p in paragraphs:
    p_len = len(p)
    if current_len + p_len + 1 > 1200 and current_chunk:
        chunks.append("\n".join(current_chunk))
        current_chunk = [p]
        current_len = p_len
    else:
        current_chunk.append(p)
        current_len += p_len + 1
if current_chunk:
    chunks.append("\n".join(current_chunk))

print(f"Total chunks: {len(chunks)}")
for i, chk in enumerate(chunks):
    print(f"Chunk {i} len: {len(chk)}")
    res = translator.translate_chunk_smart(chk)
    print(f"Chunk {i} result len: {len(res)}")
    print(f"Chunk {i} is_mostly_chinese: {translator.is_mostly_chinese(res)}")
    print(f"Chunk {i} sample:\n{res[:150]}\n")
