# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List
import gc
import config

try:
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
    from moviepy.editor import (
        AudioFileClip, ColorClip, ImageClip,
        VideoFileClip, concatenate_videoclips,
    )

    MOVIEPY_OK = True
except ImportError:
    MOVIEPY_OK = False

CHANGE_EVERY  = 10  # seconds
FADE_DURATION = 0.3 # seconds

class VideoAssembler:
    def __init__(self):
        if not MOVIEPY_OK:
            raise ImportError("moviepy is not installed.")
        self.w   = config.VIDEO_WIDTH
        self.h   = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        self._media_counter = 0

    def assemble(self, script, audio_files, media_files, output_path):
        sections    = script.get("sections", [])
        n           = len(sections)
        total_media = len(media_files)
        all_clips   = []

        print(f"   Media files: {total_media} | Change every: {CHANGE_EVERY}s")
        print(f"   Resolution : {self.w}x{self.h} @ {self.fps}fps")

        for idx in range(n):
            print(f"   Section {idx+1}/{n}: compositing ...", end=" ", flush=True)

            audio_clip = AudioFileClip(str(audio_files[idx]))
            duration   = audio_clip.duration
            chunks     = []
            elapsed    = 0.0

            while elapsed < duration:
                chunk_dur = min(CHANGE_EVERY, duration - elapsed)
                if chunk_dur < 0.3:
                    break

                media_path = media_files[self._media_counter % total_media]
                self._media_counter += 1

                bg = self._load_bg(media_path, chunk_dur)

                # No fade transition (causes shape errors)
                pass

                chunks.append(bg)
                elapsed += chunk_dur

            if not chunks:
                chunks = [ColorClip(size=(self.w,self.h),color=(0,0,0)).set_duration(duration)]

            section_bg = concatenate_videoclips(chunks, method="compose") if len(chunks) > 1 else chunks[0]
            final = section_bg.set_audio(audio_clip).set_duration(duration)
            all_clips.append(final)

            for c in chunks:
                try: c.close()
                except: pass
            gc.collect()

            print(f"done ({len(chunks)} clips)")

        print(f"   Joining {n} sections ...", end=" ", flush=True)
        full = concatenate_videoclips(all_clips, method="compose")
        print("done")

        print(f"   Writing: {output_path} ...", end=" ", flush=True)
        full.write_videofile(
            output_path, fps=self.fps,
            codec="libx264", audio_codec="aac",
            temp_audiofile="temp_audio_merge.m4a",
            remove_temp=True, logger=None,
            threads=2, preset="ultrafast",
        )
        print("done")

        for c in all_clips:
            try: c.close()
            except: pass
        try: full.close()
        except: pass
        gc.collect()

    def _load_bg(self, path: Path, duration: float):
        if not path.exists():
            return ColorClip(size=(self.w,self.h),color=(0,0,0)).set_duration(duration)
        try:
            suf = path.suffix.lower()
            if suf in (".mp4",".mov",".avi",".mkv"):
                clip = VideoFileClip(str(path), audio=False)
                clip = self._fill(clip)
                if clip.duration < duration:
                    from moviepy.video.fx.all import loop as vfx_loop
                    clip = vfx_loop(clip, duration=duration)
                return clip.subclip(0, duration)
            elif suf in (".jpg",".jpeg",".png"):
                # Ensure RGB — convert grayscale to RGB
                try:
                    from PIL import Image as PILImage
                    import numpy as np
                    img = PILImage.open(str(path)).convert("RGB")
                    clip = ImageClip(np.array(img)).set_duration(duration)
                except:
                    clip = ImageClip(str(path)).set_duration(duration)
                return self._fill(clip)
        except Exception as e:
            print(f"\n   Could not load {path.name}: {e}")
        return ColorClip(size=(self.w,self.h),color=(0,0,0)).set_duration(duration)

    def _fill(self, clip):
        try:
            sw, sh = clip.size
            tr = self.w / self.h
            sr = sw / sh
            if sr > tr:
                clip = clip.resize(height=self.h)
                x1 = (clip.w - self.w) // 2
                clip = clip.crop(x1=x1, y1=0, x2=x1+self.w, y2=self.h)
            else:
                clip = clip.resize(width=self.w)
                y1 = (clip.h - self.h) // 2
                clip = clip.crop(x1=0, y1=y1, x2=self.w, y2=y1+self.h)
        except: pass
        return clip
