# -*- coding: utf-8 -*-
import json, re, requests
from pathlib import Path
import config

WPM = 140

class ScriptGenerator:
    def __init__(self, api_key=None):
        self.api_key    = api_key or config.OPENAI_API_KEY
        self.n_sections = config.SCRIPT_SECTIONS

    def generate(self, topic: str, target_minutes: int = 0) -> dict:
        if target_minutes > 0:
            n     = max(4, target_minutes * 2)
            words = max(80, (target_minutes * WPM) // n)
        else:
            n     = self.n_sections
            words = 120

        prompt = f"""You are a YouTube scriptwriter. Generate a script for: {topic}

Return ONLY valid JSON — no markdown:
{{
  "title": "<catchy title>",
  "sections": [
    {{
      "narration": "<exactly {words} words>",
      "search_query": "<3-5 English keywords for stock images>",
      "on_screen_text": "<max 8 word caption>"
    }}
  ]
}}

Rules:
- Exactly {n} sections
- Each narration exactly {words} words
- search_query in English only
- search_query must be GENERIC visual keywords, NOT brand/product names
- Good: "gaming laptop screen", "computer processor chip", "technology office"
- Bad: "Microsoft RTX Spark", "Apple MacBook", "Nvidia GPU"
- No markdown, only JSON"""

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.7, "max_tokens": 8000},
            timeout=60,
        )
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        return self._parse(raw)

    def load_from_file(self, path: str, target_minutes: int = 0) -> dict:
        text = Path(path).read_text(encoding="utf-8").strip()
        try:
            data = json.loads(text)
            self._validate(data)
            return data
        except: pass
        return self._plain_to_script(text, Path(path).stem, target_minutes=target_minutes)

    @staticmethod
    def _parse(raw: str) -> dict:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            data = json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}\nRaw: {raw}")
        ScriptGenerator._validate(data)
        return data

    @staticmethod
    def _validate(data: dict):
        if "title" not in data or "sections" not in data:
            raise ValueError("Missing title or sections")
        for i, s in enumerate(data["sections"]):
            if "narration" not in s:
                raise ValueError(f"Section {i} missing narration")
            q = s.get("search_query", "").encode('ascii','ignore').decode('ascii').strip()
            s["search_query"] = q if q and len(q) > 2 else "nature landscape"
            if "on_screen_text" not in s:
                s["on_screen_text"] = " ".join(s["narration"].split()[:8])

    @staticmethod
    def _plain_to_script(text: str, title: str = "My Video", target_minutes: int = 0) -> dict:
        lines = text.split('\n')
        actual_title = title
        body = []
        for line in lines:
            if line.startswith('#'): actual_title = line.lstrip('#').strip()
            else: body.append(line)

        full_text = ' '.join(body).strip()
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", '\n'.join(body)) if p.strip()]

        # If target_minutes set, split text into more sections
        if target_minutes > 0:
            n_sections = max(target_minutes * 2, len(paragraphs))
            words = full_text.split()
            words_per_section = max(1, len(words) // n_sections)
            paragraphs = []
            for i in range(0, len(words), words_per_section):
                chunk = ' '.join(words[i:i+words_per_section])
                if chunk.strip():
                    paragraphs.append(chunk)

        queries = ["news broadcast","world map","city street","government building",
                   "military army","economy finance","nature landscape","technology digital",
                   "crowd people","ocean horizon"]
        sections = []
        for i, para in enumerate(paragraphs):
            sections.append({
                "narration": para,
                "search_query": queries[i % len(queries)],
                "on_screen_text": " ".join(para.split()[:8]),
            })
        return {"title": actual_title, "sections": sections}

    def save_script(self, script, path):
        Path(path).write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"   Script saved: {path}")
