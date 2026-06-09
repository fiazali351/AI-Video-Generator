# -*- coding: utf-8 -*-
import time, json, re, requests
from pathlib import Path
from typing import List
import config

class MediaFetcher:
    IMAGE_DURATION = 10  # seconds per image

    def __init__(self, api_key=None):
        self.api_key = api_key or config.PEXELS_API_KEY

    def fetch_for_sections(self, sections: List[dict], temp_dir: Path, duration_seconds: int = 0) -> List[Path]:
        # Use actual duration if provided, else estimate
        if duration_seconds <= 0:
            duration_seconds = len(sections) * 30  # fallback estimate

        by_sections = len(sections) * 4
        by_duration = int(duration_seconds / self.IMAGE_DURATION) + 2
        needed = max(by_sections, by_duration, 20)

        print(f"   Sections: {len(sections)} | Duration: {duration_seconds}s | Downloading {needed} images ...")

        files, used = [], set()
        ai_queries  = self._get_queries(sections, needed)
        print(f"   Queries: {ai_queries[:3]} ...")

        for idx in range(needed):
            query = ai_queries[idx % len(ai_queries)]
            print(f"   Image {idx+1}/{needed}: '{query}' ...", end=" ")

            path = (self._serper(query, temp_dir, idx, used) or
                    self._pexels(query, temp_dir, idx, used))

            if path is None:
                path = self._colored_bg(temp_dir, idx)
                print("colored bg")
            else:
                print("done")

            files.append(path)
            time.sleep(0.3)

        return files

    def _serper(self, query, temp_dir, idx, used):
        try:
            r = requests.post(
                "https://google.serper.dev/images",
                headers={"X-API-KEY": config.SERPER_API_KEY,
                         "Content-Type": "application/json"},
                json={"q": query, "num": 5},
                timeout=10
            )
            if r.status_code == 200:
                for item in r.json().get("images", []):
                    url = item.get("imageUrl", "")
                    if url and url not in used and url.startswith("http"):
                        used.add(url)
                        out = temp_dir / f"media_{idx:03d}.jpg"
                        try:
                            dl = requests.get(url,
                                headers={"User-Agent": "Mozilla/5.0"},
                                timeout=12, stream=True)
                            if dl.status_code == 200 and len(dl.content) > 5000:
                                with open(out, "wb") as f:
                                    f.write(dl.content)
                                return out
                        except: continue
        except: pass
        return None

    def _pexels(self, query, temp_dir, idx, used):
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": self.api_key},
                params={"query": query, "per_page": 5, "orientation": "landscape"},
                timeout=10
            )
            if r.status_code == 200:
                for p in r.json().get("photos", []):
                    url = p.get("src", {}).get("large")
                    if url and url not in used:
                        used.add(url)
                        out = temp_dir / f"media_{idx:03d}.jpg"
                        dl = requests.get(url, timeout=30, stream=True)
                        if dl.status_code == 200:
                            with open(out, "wb") as f:
                                for chunk in dl.iter_content(65536): f.write(chunk)
                            if out.exists() and out.stat().st_size > 5000:
                                return out
        except: pass
        return None

    def _get_queries(self, sections, count):
        try:
            text = " ".join([s.get("narration","") for s in sections])[:2000]
            prompt = (
                f"Analyze this script and return {count} English image search queries.\n"
                f"Script: {text}\n"
                f"Return ONLY a JSON array.\n"
                f"Each query: 2-5 words, specific and visual."
            )
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.3, "max_tokens": 500},
                timeout=20
            )
            if r.status_code == 200:
                raw = r.json()["choices"][0]["message"]["content"].strip()
                match = re.search(r'\[.*?\]', raw, re.DOTALL)
                if match:
                    queries = json.loads(match.group())
                    queries = [q.encode('ascii','ignore').decode('ascii').strip()
                               for q in queries if len(q) > 2]
                    if queries:
                        print(f"\n   Groq queries: {queries[:3]}")
                        return queries
        except Exception as e:
            print(f"\n   AI error: {e}")

        fallback = [s.get("search_query","").encode('ascii','ignore').decode('ascii').strip()
                    for s in sections]
        return [q for q in fallback if len(q) > 2] or ["nature", "technology", "city"]

    def _colored_bg(self, temp_dir, idx):
        colors = [(15,15,35),(35,15,15),(15,35,15),(35,25,0),(20,0,35),(0,30,35)]
        out = temp_dir / f"media_{idx:03d}_bg.jpg"
        try:
            from PIL import Image
            img = Image.new("RGB", (config.VIDEO_WIDTH, config.VIDEO_HEIGHT),
                           colors[idx % len(colors)])
            img.save(str(out), "JPEG")
        except:
            out.write_bytes(bytes([0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,
                0x00,0x01,0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xC0,0x00,0x0B,
                0x08,0x00,0x01,0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xDA,0x00,0x08,0x01,
                0x01,0x00,0x00,0x3F,0x00,0xFB,0xD5,0xFF,0xD9]))
        return out
