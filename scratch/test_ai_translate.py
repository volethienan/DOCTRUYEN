import os
from openai import OpenAI

api_key = os.environ.get("NINE_ROUTER_API_KEY")
print("Key length:", len(api_key))

# Test with openrouter.ai
try:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    res = client.models.list()
    print("OpenRouter models count:", len(res.data))
    
    # Try a quick test translation
    completion = client.chat.completions.create(
        model="google/gemini-2.5-flash" if "gemini" in [m.id for m in res.data[:10]] else "meta-llama/llama-3-8b-instruct:free",
        messages=[
            {"role": "user", "content": "Dịch tiêu đề sang tiếng Việt: 第2005章 倒霉的葉塵"}
        ],
        max_tokens=50
    )
    print("OpenRouter translation:", completion.choices[0].message.content)
except Exception as e:
    print("OpenRouter error:", e)
