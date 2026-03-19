import os
import random
import warnings
import shutil
from pathlib import Path
import soundfile as sf
from faster_whisper import WhisperModel
from kokoro import KPipeline
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import textwrap

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KOKORO_LOG_LEVEL"] = "ERROR"


def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def final_cleanup(generated_videos, story_file, hook_img):

    project_name = Path(story_file).stem
    target_dir = Path("videos") / project_name
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\n--- FINALIZING AND ORGANIZING ---")

    for video in generated_videos:
        if Path(video).exists():
            shutil.move(video, str(target_dir / video))
            print(f"Moved Video: {video} -> {target_dir}")

    for asset in [story_file, hook_img]:
        if Path(asset).exists():
            shutil.move(asset, str(target_dir / asset))
            print(f"Moved Asset: {asset} -> {target_dir}")

    for temp in ["output_0.wav", "temp_full_audio.wav"]:
        temp_path = Path(temp)
        if temp_path.exists():
            try:
                temp_path.unlink()
                print(f"Deleted temp file: {temp}")
            except Exception as e:
                print(f"Could not delete {temp}: {e}")


def create_reddit_hook(username, title_text, output_path="hook.png"):
    width, height = 1560, 1170
    bg_color = (255, 255, 255)
    text_color = (28, 28, 28)
    user_color = (119, 119, 119)
    reddit_orange = (255, 69, 0)

    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    card_margin_x, card_margin_y = 100, 250
    card_coords = [card_margin_x, card_margin_y, width - card_margin_x, height - card_margin_y]
    draw.rounded_rectangle(card_coords, radius=45, fill=bg_color)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 65)
        font_user = ImageFont.truetype("arialbd.ttf", 45)
        font_stats = ImageFont.truetype("arialbd.ttf", 40)
    except:
        font_title = ImageFont.load_default()
        font_user = ImageFont.load_default()
        font_stats = ImageFont.load_default()

    pfp_x, pfp_y = card_margin_x + 60, card_margin_y + 60
    try:
        avatar = Image.open("reddit_logo.png").convert("RGBA")
        avatar = avatar.resize((100, 100))
        img.paste(avatar, (pfp_x, pfp_y), avatar)
    except:
        draw.ellipse([pfp_x, pfp_y, pfp_x + 100, pfp_y + 100], fill=reddit_orange)

    draw.text((pfp_x + 130, pfp_y + 25), f"u/{username}", font=font_user, fill=text_color)

    wrapped_lines = textwrap.wrap(title_text, width=38)
    y_text = pfp_y + 160
    for line in wrapped_lines:
        draw.text((pfp_x, y_text), line, font=font_title, fill=text_color)
        y_text += 85

    stats_y = card_coords[3] - 100
    icon_size = 40

    draw.polygon([
        (pfp_x, stats_y + icon_size),
        (pfp_x + icon_size // 2, stats_y),
        (pfp_x + icon_size, stats_y + icon_size)
    ], fill=user_color)

    draw.text((pfp_x + 60, stats_y - 10), f"{random.randint(1000, 9999)}", font=font_stats, fill=user_color)

    draw.polygon([
        (pfp_x + 220, stats_y),
        (pfp_x + 220 + icon_size // 2, stats_y + icon_size),
        (pfp_x + 220 + icon_size, stats_y)
    ], fill=user_color)

    draw.text((pfp_x + 450, stats_y - 10), f"{random.randint(100, 500)} Comments", font=font_stats, fill=user_color)

    draw.text((width - card_margin_x - 200, stats_y - 10), "Share", font=font_stats, fill=user_color)

    img.save(output_path)
    print(f"-> Hook Image Updated: {output_path} ({width}x{height})")

def get_audio_and_timestamps(full_text, words_per_chunk=3):
    print("-> Step 1: Generating Narration (Kokoro)...")
    pipeline = KPipeline(lang_code='a')
    generator = pipeline(full_text, voice='af_heart', speed=1)

    audio_segments = []
    for _, _, audio in generator:
        audio_segments.extend(audio)

    temp_audio = "temp_full_audio.wav"
    sf.write(temp_audio, audio_segments, 24000)

    print("-> Step 2: Transcribing & Smart Chunking...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(temp_audio, word_timestamps=True)

    all_words = []
    for segment in segments:
        for w in segment.words:
            all_words.append({'word': w.word.strip(), 'start': w.start, 'end': w.end})

    chunks = []
    current_chunk = []

    for w_info in all_words:
        current_chunk.append(w_info)
        word_text = w_info['word']

        has_punctuation = any(word_text.endswith(p) for p in [".", "!", "?"])

        if len(current_chunk) >= words_per_chunk or has_punctuation:
            chunk_text = " ".join([w['word'] for w in current_chunk])
            chunks.append({
                'start': current_chunk[0]['start'],
                'end': current_chunk[-1]['end'],
                'text': chunk_text
            })
            current_chunk = []

    if current_chunk:
        chunk_text = " ".join([w['word'] for w in current_chunk])
        chunks.append({
            'start': current_chunk[0]['start'],
            'end': current_chunk[-1]['end'],
            'text': chunk_text
        })

    return temp_audio, chunks


def process_video(title_text, story_file, bg_path, hook_img_path, part_duration):
    if not os.path.exists(story_file):
        print(f"Error: {story_file} not found.")
        return
    with open(story_file, 'r', encoding='utf-8') as f:
        story_body = f.read().strip()

    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    full_script = f"{title_text}. {story_body}"

    audio_path, chunks = get_audio_and_timestamps(full_script, words_per_chunk=3)
    full_audio = AudioFileClip(audio_path)

    title_words = len(title_text.split())
    title_audio_end = 0
    word_count = 0
    for c in chunks:
        word_count += len(c['text'].split())
        if word_count >= title_words:
            title_audio_end = c['end']
            break

    story_chunks = [c for c in chunks if c['start'] >= title_audio_end]

    MAX_PART_DURATION = random.randint(part_duration-5, part_duration)
    available_story_time = MAX_PART_DURATION - title_audio_end

    parts_data = []
    current_part_chunks = []
    current_part_duration = 0

    for c in story_chunks:
        duration = c['end'] - c['start']
        current_part_chunks.append(c)
        current_part_duration += duration

        if current_part_duration >= available_story_time:
            if any(c['text'].endswith(p) for p in [".", "!", "?"]):
                parts_data.append(current_part_chunks)
                current_part_chunks = []
                current_part_duration = 0

    if current_part_chunks:
        parts_data.append(current_part_chunks)

    print(f"\n--- PROPOSED VIDEO DETAILS ---")
    print(f"Base Title: {story_file.replace('.txt', '')}")
    print(f"Total Parts to Create: {len(parts_data)}")

    if input("\nProceed with rendering? (y/n): ").strip().lower() != 'y':
        full_audio.close()
        return

    generated_files = []

    for i, part_chunks in enumerate(parts_data):
        part_num = i + 1
        print(f"\n--- RENDERING PART {part_num} ---")

        from moviepy import concatenate_audioclips
        title_audio = full_audio.subclipped(0, title_audio_end)
        story_part_audio = full_audio.subclipped(part_chunks[0]['start'], part_chunks[-1]['end'])
        part_audio = concatenate_audioclips([title_audio, story_part_audio])

        bg_video = VideoFileClip(bg_path).without_audio()
        start_point = random.uniform(0, max(0, bg_video.duration - part_audio.duration - 2))
        video_seg = bg_video.subclipped(start_point, start_point + part_audio.duration)

        w, h = video_seg.size
        target_w = int((h * (9 / 16)) // 2) * 2
        video_seg = video_seg.cropped(x_center=int(w / 2), width=target_w)

        clips = [video_seg]

        hook_layer = (ImageClip(hook_img_path).with_duration(title_audio_end)
                      .with_position("center").resized(width=int(target_w * 0.9)))
        clips.append(hook_layer)

        offset = part_chunks[0]['start'] - title_audio_end
        for c in part_chunks:
            sub = (TextClip(text=c['text'].upper(), font_size=30, color='white', font=font_path,
                            stroke_color='black', stroke_width=2, method='caption',
                            size=(int(target_w * 0.85), 200))
                   .with_start(c['start'] - offset)
                   .with_end(c['end'] - offset)
                   .with_position(('center', 'center')))
            clips.append(sub)

        PART_FILENAME = story_file.replace(".txt", "") + f"_Part{part_num}.mp4"
        final_video = CompositeVideoClip(clips).with_audio(part_audio)

        final_video.write_videofile(PART_FILENAME, fps=30, codec="libx264", audio_codec="aac",
                                    ffmpeg_params=["-pix_fmt", "yuv420p"], logger='bar')

        generated_files.append(PART_FILENAME)
        bg_video.close()

    full_audio.close()
    print("\n--- FINALIZING AND ORGANIZING ---")
    final_cleanup(generated_files, story_file, hook_img_path)

if __name__ == "__main__":

    TITLE = input("Insert title you want: ")
    USERNAME = input("Insert username you want to be on image: ")
    create_reddit_hook(USERNAME, TITLE)
    STORY_FILE = input("Enter the story file name ( example -> story.txt ): ")
    BG_VIDEO = input("Enter name of background video ( example -> minecraftBG.mp4 ): ")
    PART_DUR = int(input("Enter duration of videos in seconds: "))
    HOOK_IMG = "hook.png"

    process_video(TITLE, STORY_FILE, BG_VIDEO, HOOK_IMG, PART_DUR)