# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List
import time
import os

class VoiceGenerator:
    def __init__(self, api_key=None, voice_name=None, lang="en", gender="male"):
        self.lang  = lang
        self.voice = "en-US-ChristopherNeural"

    def generate_sections(self, sections: List[dict], temp_dir: Path) -> List[Path]:
        print(f"   Voice: {self.voice}")
        audio_files = []
        for idx, section in enumerate(sections):
            text     = section["narration"]
            out_path = temp_dir / f"audio_{idx:03d}.mp3"
            print(f"   Section {idx+1}/{len(sections)}: generating audio ...", end=" ")

            success = self._edge_tts(text, str(out_path))
            if not success:
                success = self._gtts(text, str(out_path))
            if not success:
                print("FAILED")
                continue

            # Verify file exists and has content
            if out_path.exists() and out_path.stat().st_size > 100:
                audio_files.append(out_path)
                print("done")
            else:
                print("file empty — retrying")
                time.sleep(1)
                success = self._gtts(text, str(out_path))
                if out_path.exists() and out_path.stat().st_size > 100:
                    audio_files.append(out_path)
                    print("done (retry)")
            time.sleep(0.3)
        return audio_files

    def _edge_tts(self, text: str, out_path: str) -> bool:
        try:
            import asyncio
            import edge_tts

            async def _run():
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(out_path)

            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.run_until_complete(_run())
            except RuntimeError:
                asyncio.run(_run())

            return os.path.exists(out_path) and os.path.getsize(out_path) > 100
        except Exception as e:
            print(f"(edge failed: {e})", end=" ")
            return False

    def _gtts(self, text: str, out_path: str) -> bool:
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=self.lang, tld="co.in", slow=False)
            tts.save(out_path)
            return os.path.exists(out_path) and os.path.getsize(out_path) > 100
        except Exception as e:
            print(f"(gtts failed: {e})", end=" ")
            return False

    def list_voices(self):
        return ["en-US-ChristopherNeural"]
