## Overview

This Python script creates a subtitled film based on a randomly chosen Reddit story from the "AmItheAsshole" forum by utilizing multiple libraries and APIs.

## Features

- **Random Story Selection:** Using the Reddit API, the script selects a top story at random from the "AmItheAsshole" forum.
- **Text-to-Speech:** Creates MP3 audio files from story text by using Google Text-to-Speech.
- **Video Editing:** To provide a refined touch, audio is combined with a randomly selected video at a random start time.
- **Deepgram Transcription:** Produces word-level subtitles by transcribing the audio using the Deepgram API.
- **Screenshot Generation:** Uses Selenium to capture a screenshot of the Reddit story's title.
- **Subtitle Addition:** Uses FFmpeg to add subtitles to the video, producing a professional-looking end product.
- **Audio Speed Modification:** Modifies audio speed to improve the flow of the video.

## Instillations

Ensure you have the following dependencies installed:

- Python (3.x)
- [gtts](https://pypi.org/project/gTTS/)
- [moviepy](https://zulko.github.io/moviepy/)
- [requests](https://pypi.org/project/requests/)
- [tqdm](https://pypi.org/project/tqdm/)
- [selenium](https://pypi.org/project/selenium/)
- [mutagen](https://pypi.org/project/mutagen/)
- [librosa](https://pypi.org/project/librosa/)
- [pyrubberband](https://pypi.org/project/pyrubberband/)
- [soundfile](https://pypi.org/project/SoundFile/)
- [pydub](https://pypi.org/project/pydub/)

  ## Configuration

Clone the repository, get needed api keys, assign different file types to needed variables, then run the program.





