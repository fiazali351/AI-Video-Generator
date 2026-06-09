# -*- coding: utf-8 -*-
import argparse
import shutil
import sys
import time
import os
from pathlib import Path

if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or higher is required.")

def banner():
    print()
    print("=" * 54)
    print("   AI YouTube Video Generator")
    print("   Groq + gTTS + Pexels + MoviePy")
    print("=" * 54)
    print()

def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--topic", "-t", metavar="TOPIC")
    group.add_argument("--script", "-s", metavar="FILE")
    parser.add_argument("--output", "-o", default="output_video.mp4")
    parser.add_argument("--save-script", action="store_true")
    parser.add_argument("--no-cleanup", action="store_true")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--duration", "-d", type=int, default=0)
    parser.add_argument("--lang", default="en")
    parser.add_argument("--gender", default="male", choices=["male", "female"])
    return parser.parse_args()

def main():
    banner()
    args = parse_args()

    try:
        import config
        from script_generator import ScriptGenerator
        from voice_generator import VoiceGenerator
        from media_fetcher import MediaFetcher
        from video_assembler import VideoAssembler
    except ImportError as exc:
        sys.exit(f"Import error: {exc}")

    # Check API keys
    if "YOUR_GROQ_KEY" in config.OPENAI_API_KEY or "YOUR_SERPER_KEY" in config.SERPER_API_KEY:
        print("API keys not configured!")
        try:
            # Get correct path for exe
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            os.chdir(base_path)
            from setup_keys import run_setup
            run_setup()
            import importlib
            importlib.reload(config)
        except Exception as e:
            print(f"Setup error: {e}", flush=True)
            sys.exit(1)

    if args.list_voices:
        print("Available: Male / Female in English, Urdu, Hindi, Arabic")
        return

    if not args.topic and not args.script:
        print("Please provide --topic or --script")
        sys.exit(1)

    # Use exe/script directory for output
    import sys
    if getattr(sys, 'frozen', False):
        base_path = Path(os.path.dirname(sys.executable))
    else:
        base_path = Path(os.path.dirname(os.path.abspath(__file__)))

    temp_dir = base_path / "temp"
    temp_dir.mkdir(exist_ok=True)
    output_dir = base_path / "output"
    output_dir.mkdir(exist_ok=True)
    # Simple clean output filename
    import re
    clean_output = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', args.output)
    if not clean_output.endswith('.mp4'):
        clean_output += '.mp4'
    output_path = output_dir / clean_output
    start_time = time.time()

    # Convert duration to seconds
    duration_seconds = args.duration * 60  # minutes to seconds

    try:
        print("-" * 54)
        print("STEP 1 - SCRIPT")
        print("-" * 54)
        script_gen = ScriptGenerator(config.OPENAI_API_KEY)

        if args.topic:
            dur_msg = f"{args.duration} min" if args.duration > 0 else "auto"
            print(f"   Topic   : \"{args.topic}\"", flush=True)
            print(f"   Duration: {dur_msg}", flush=True)
            script = script_gen.generate(args.topic, target_minutes=args.duration)
        else:
            print(f"   Loading: {args.script}", flush=True)
            script = script_gen.load_from_file(args.script, target_minutes=args.duration)

        n_sections = len(script["sections"])
        title = script["title"].encode('ascii','ignore').decode('ascii')
        print(f"   Title   : {title}", flush=True)
        print(f"   Sections: {n_sections}", flush=True)

        if args.save_script:
            script_path = str(output_path).replace(".mp4", "_script.json")
            script_gen.save_script(script, script_path)

        print()
        print("-" * 54)
        print(f"STEP 2 - VOICEOVER ({args.lang} / {args.gender}, flush=True)", flush=True)
        print("-" * 54)
        voice_gen = VoiceGenerator(lang=args.lang, gender=args.gender)
        audio_files = voice_gen.generate_sections(script["sections"], temp_dir)
        print(f"   {len(audio_files)} audio clips generated", flush=True)

        print()
        print("-" * 54)
        print("STEP 3 - STOCK MEDIA")
        print("-" * 54)
        fetcher = MediaFetcher(config.PEXELS_API_KEY)
        media_files = fetcher.fetch_for_sections(
            script["sections"],
            temp_dir,
            duration_seconds=duration_seconds  # ✅ pass karo
        )
        print(f"   {len(media_files)} media files downloaded", flush=True)

        print()
        print("-" * 54)
        print("STEP 4 - ASSEMBLING VIDEO")
        print("-" * 54)
        assembler = VideoAssembler()
        assembler.assemble(script, audio_files, media_files, str(output_path))



        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        print()
        print("=" * 54)
        print("   VIDEO CREATED!")
        print(f"   Output : {str(output_path)}", flush=True)
        print(f"   Time   : {mins}m {secs}s", flush=True)
        print("=" * 54)
        print()
        print("Tips:")
        print("   Upload to YouTube Studio -> youtube.com/upload")

    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
    except Exception as exc:
        print(f"\nError: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if not args.no_cleanup and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
