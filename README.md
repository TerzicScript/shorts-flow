# 🎬 Shorts Flow v1.0.0

<div align="center">

**An automated Python pipeline that transforms Reddit stories into high-quality TikTok, Reels, and YouTube Shorts using AI.**

[Download Source](https://github.com/TerzicScript/shorts-flow/archive/refs/heads/main.zip) • [Report Bug](https://github.com/TerzicScript/shorts-flow/issues) • [Request Feature](https://github.com/TerzicScript/shorts-flow/issues)

</div>

## 🎯 Overview

**Shorts Flow** is a professional-grade content creation tool. It automates the tedious process of syncing AI-generated voiceovers, transcribing subtitles with high accuracy, and overlaying them onto background gameplay footage.

The script handles the "hook" namecard (Title/Username) at the start and intelligently splits long stories into multiple parts so you can upload them as a series.

---

### 📝 Quick Notice: Example Run

To see exactly how the script performs, I have provided the assets used for a test run and the final results.

**Inputs Used:**
* **Hook Title:** "I have matured so much, and instead of just waiting for my boyfriend to cheat, I have taken control."
* **Username:** `1000andonenites`
* **Story File:** [storyNew.txt](./storyNew.txt) ( it's not full reddit post )
* **Background Video:** [minecraftBG.mp4](./minecraftBG.mp4)
* **Target Duration:** 50 Seconds

**Generated Output:**
The story was automatically split into 3 parts. You can view the rendered results here:
* 📺 [Part 1 - Watch Here](https://streamable.com/revhl3)
* 📺 [Part 2 - Watch Here](https://streamable.com/sxvb12)
* 📺 [Part 3 - Watch Here](https://streamable.com/y59c1q)

---

## ⚙️ How It Works

The application is designed to be a "set and forget" pipeline for short-form content.

1.  **Input**: Place your story in `story.txt` and a background video (like Minecraft parkour or GTA) as `background.mp4`.
2.  **Voice Generation**: Uses **Kokoro TTS** to create a natural, human-like narration.
3.  **Transcription**: Uses **Faster-Whisper** to generate word-level timestamps for perfectly synced subtitles.
4.  **Auto-Splitting**: You input a target duration (e.g., 50 seconds). The script splits the story into Part 1, Part 2, etc., automatically.
5.  **Rendering**: The script composites the background, the "hook" card, and the animated text into a finished `.mp4`.

**Directory Structure:**
```text
Project_Folder/
├── main.py               # The main script
├── story.txt             # Your Reddit story text
├── background.mp4        # Your 9:16 background footage
└── videos/               # Where your finished videos appear
```

---

### Why This Tool?

- Because manual editing takes hours, and this takes minutes. Plus, it's free.

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Kokoro TTS** | Integrated high-fidelity text-to-speech for realistic narration |
| **Faster-Whisper** | AI-powered transcription for pixel-perfect subtitle timing |
| **Auto-Splitting** | Automatically breaks long stories into parts based on your duration input |
| **Hook Generator** | Creates the iconic "Reddit UI" intro card with custom Title/User |
| **Dynamic Subtitles** | Word-for-word text overlays rendered via MoviePy and PIL |
| **Batch Processing** | Handles audio generation and video rendering in one workflow |

---

## 💾 Download & Installation

### Option 1: Run from Source

**Requirements:**
- Python 3.10 or higher
- **FFmpeg** installed and added to your System PATH

**Installation Steps:**

```bash
# Clone the repository
git clone https://github.com/TerzicScript/shorts-flow.git
cd shorts-flow

# Install dependencies
pip install faster-whisper kokoro moviepy soundfile pillow
```

---

## 🛠 Technical Stack

This project leverages some of the best open-source AI tools available:

- **Audio**: [Kokoro](https://github.com/hexgrad/kokoro) & [Soundfile](https://pypi.org/project/soundfile/)
- **Transcription**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
- **Video Editing**: [MoviePy](https://zulko.github.io/moviepy/)
- **Image/Text Rendering**: [Pillow (PIL)](https://python-pillow.org/)

---

## 🚀 Quick Start Guide

### Step 1: Setup
Ensure `story.txt` and `background.mp4` are in the project folder.

### Step 2: Launch
Run the script:
```bash
python main.py
```

### Step 3: Input Data
Follow the terminal prompts:
1. Enter the **Video Title** (for the hook).
2. Enter the **Username** (to show on the card).
3. Enter the **Max Duration** per part (e.g., 60 for one minute).

### Step 4: Finalize
The script will generate audio and ask for confirmation. Press `Y` to start the final video render.

---

## 🤝 Contributing

Contributions are welcome! If you have a better way to style the subtitles or handle transitions, feel free to help out.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/CoolUpdates`)
3. Commit your changes
4. Push and open a Pull Request

## 🙏 Credits

- **The AI Community** - For providing the TTS and Whisper models.
- **My Coffee Machine** - For keeping me awake while debugging MoviePy errors.

---

<div align="center">

[⬆ Back to Top](#-shorts-flow-v100)

</div>
