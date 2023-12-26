import os
from gtts import gTTS
import moviepy.editor as mpe
import random
from Paths import *
import APIKey
import pw
from moviepy.config import change_settings
import requests
from tqdm import tqdm
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from mutagen.mp3 import MP3
import time
import librosa
import pyrubberband
import soundfile as sf
from pydub import AudioSegment


deepgramapiKey = APIKey.WHISPER_KEY

os.environ["PATH"] += os.pathsep + "/usr/local/bin/ffmpeg"

PathtoMagick = "/usr/local/bin/magick"
change_settings({"IMAGEMAGICK_BINARY": PathtoMagick})

save_directory = "/Users/kien/Desktop/RedditVideos"

def get_access_token(client_id, secret_id, username, password):
    auth = requests.auth.HTTPBasicAuth(client_id, secret_id)

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    headers = {'User-Agent': 'MyAPI/1.0.0'}  # Make sure to update the version number

    TOKEN_ACCESS_ENDPOINT = "https://www.reddit.com/api/v1/access_token"

    try:
        response = requests.post(TOKEN_ACCESS_ENDPOINT, data=data, headers=headers, auth=auth)
        response.raise_for_status()  # Check for errors in the request

        if 'access_token' in response.json():
            token_id = response.json()['access_token']
            return token_id
        else:
            print("Error: 'access_token' not found in the response.")
            return None

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(response.text)
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

def get_story_text(token_id, story_id):
    if token_id is not None:
        OAUTH_ENDPOINT = 'https://oauth.reddit.com'
        endpoint = f'/r/AmItheAsshole/comments/{story_id}/'

        headers_get = {
            'User-Agent': 'MyAPI/1.0.0',
            'Authorization': 'Bearer ' + token_id
        }

        try:
            response = requests.get(OAUTH_ENDPOINT + endpoint, headers=headers_get)
            response.raise_for_status()

            post_data = response.json()[0]['data']['children'][0]['data']
            return post_data.get('selftext', 'No text available for this story.')

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            print(response.text)
        except requests.exceptions.RequestException as err:
            print(f"Request Exception: {err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")

    return 'No text available for this story.'

def choose_and_print_random_story(token_id):
    if token_id is not None:
        OAUTH_ENDPOINT = 'https://oauth.reddit.com'
        subreddit = 'AmItheAsshole'
        endpoint = f'/r/{subreddit}/top/'

        params_get = {
            'limit': 100,
            't': 'all',
        }

        headers_get = {
            'User-Agent': 'MyAPI/1.0.0',
            'Authorization': 'Bearer ' + token_id
        }

        try:
            response = requests.get(OAUTH_ENDPOINT + endpoint, headers=headers_get, params=params_get)
            response.raise_for_status()

            top_stories = response.json().get('data', {}).get('children', [])

            if top_stories:
                random_story = random.choice(top_stories)['data']

                title = random_story.get('title', 'N/A')
                context = random_story.get('selftext', 'No context available for this story.')
                url = random_story.get('url', '')

                context_without_url = context.replace(url, '')

                print("Title:", title)
                print("Context:", context_without_url)

                return title, context_without_url, url
            else:
                print("No top stories found.")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            print(response.text)
        except requests.exceptions.RequestException as err:
            print(f"Request Exception: {err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")

    return 'N/A', 'No text available for this story.', 'N/A'

def replace_first_word(title, replacement):
    words = title.split()
    for i, word in enumerate(words):
        if word == "AITA":
            words[i] = replacement
            break
    return ' '.join(words)

def save_mp3(title, context, save_directory):
    language = 'en'
    replacement_string = "Am I the asshole"
    new_title = replace_first_word(title, replacement_string)
    text = new_title + " " + context

    text_without_spaces = text.replace(". ", " ")

    # Save the MP3 files
    mp3_path_title = os.path.join(save_directory, "Title.mp3")
    mp3_path_context = os.path.join(save_directory, "Context.mp3")
    mp3_path_fulltext = os.path.join(save_directory, "FullText.mp3")

    myobjTitle = gTTS(text=new_title, lang=language, slow=False)
    myobjContext = gTTS(text=context, lang=language, slow=False)
    myobjFullText = gTTS(text=text_without_spaces, lang=language, slow=False)

    myobjTitle.save(mp3_path_title)
    myobjContext.save(mp3_path_context)
    myobjFullText.save(mp3_path_fulltext)

    return mp3_path_title, mp3_path_context, mp3_path_fulltext

def combine_audio_random_start(vid_path, aud_path, folder_path, output_filename, fps=60):
    try:
        os.makedirs(folder_path, exist_ok=True)

        # Load video and audio clips
        my_clip = mpe.VideoFileClip(vid_path)
        audio_background = mpe.AudioFileClip(aud_path)

        # Calculate the maximum valid start time
        max_start_time = my_clip.duration - audio_background.duration

        # Generate a random start time within the valid range
        start_time = random.uniform(0, max_start_time)

        # Trim the video clip based on the random start time
        trimmed_clip = my_clip.subclip(start_time, start_time + audio_background.duration)

        # Set the audio of the video clip to the provided audio
        final_clip = trimmed_clip.set_audio(audio_background)

        # Specify the codec and file extension
        output_path = os.path.join(folder_path, output_filename)
        final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=4)

    except Exception as e:
        print(f"Error: {e}")

def get_mp3_duration(mp3_path):
    try:
        if not os.path.isfile(mp3_path):
            raise FileNotFoundError(f"MP3 file not found: {mp3_path}")

        # Get the duration using mutagen
        audio = MP3(mp3_path)
        duration_seconds = audio.info.length

        return duration_seconds

    except Exception as e:
        print(f"Error: {e}")
        return None

def getDeepgramTranscription(file_path, deepgram_api_key, delay_seconds):
    url = "https://api.deepgram.com/v1/listen?model=whisper-large&language=en&punctuate=true&diarize=true&smart_format=true"

    files = {
        'audio': ('file.mp4', open(file_path, 'rb')),
    }

    headers = {
        "Authorization": 'Token ' + deepgram_api_key,
    }

    response = requests.post(url, headers=headers, files=files, stream=True)

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB

    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

    with open("transcription_result.json", 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)

    progress_bar.close()

    with open("transcription_result.json", 'r') as f:
        output = json.load(f)

    return output


def convert_to_srt(data, output_filename):
    def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds * 1000):03d}"

    with open(output_filename, 'w') as f:
        for i, entry in enumerate(data, start=1):
            start_time = format_time(entry['start'])
            end_time = format_time(entry['end'])
            subtitle_text = entry['punctuated_word']
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{subtitle_text}\n\n")

def delete_all_files_in_folder(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Iterate through the files and delete each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def titleScreenShot(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome()

    try:
        # Open the webpage
        driver.get(url)
        # Find the first h1 element
        h1_element = driver.find_element(By.TAG_NAME, 'h1')

        # Take a screenshot of the h1 element
        screenshot_path = '/Users/kien/Desktop/RedditVideos/ScreenShots/screenshot.png'
        h1_element.screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

    finally:
        # Quit the browser
        driver.quit()

def AddingScreenShot(video_path, title_path, output_path, duration):
    video = mpe.VideoFileClip(video_path)

    title = mpe.ImageClip(title_path).set_start(0).set_duration(duration).set_pos(("center", "center")).resize(
            height=100)

    final = mpe.CompositeVideoClip([video, title])
    final.write_videofile(output_path)


def choose_random_video(video_paths):
    if not video_paths:
        raise ValueError("The list of video paths is empty.")

    return random.choice(video_paths)

def speedAudioChange(originalMP3file, wav_filepath, wav_increasedSpeed_filepath):
    mp3_filepath = originalMP3file
    audio = AudioSegment.from_mp3(mp3_filepath)
    wavaudio = audio.export(wav_filepath, format='wav')
    y, sr = librosa.load(wavaudio, sr=None)
    y_stretched = pyrubberband.time_stretch(y, sr, 1.5)
    sf.write(wav_increasedSpeed_filepath, y_stretched, sr, format='wav')
    audio = AudioSegment.from_wav(wav_increasedSpeed_filepath)
    audio.export(originalMP3file, format='mp3')



def main():
    videoPath = choose_random_video(videoLibrry)


    delete_all_files_in_folder(foldertoDelete)
    SECRET_ID = APIKey.SECRET_ID
    password = pw.PASSWORD
    token = get_access_token(CLIENT_ID, SECRET_ID, username, password)
    title, context, url = choose_and_print_random_story(token)

    print("Title:", title)
    print("Context:", context)
    print("URL:", url)
    titleScreenShot(url)
    # Save MP3 files
    mp3_path_title, mp3_path_context, mp3_path_fulltext = save_mp3(title, context, save_directory)
    speedAudioChange(originalMP3file_title, wav_filepath_title, wav_increasedSpeed_filepath_title)
    speedAudioChange(originalMP3file_Context, wav_filepath_title_Context, wav_increasedSpeed_filepath_title_Context)
    speedAudioChange(originalMP3file_FullText, wav_filepath_title_FullText, wav_increasedSpeed_filepath_title_FullText)

    titleLength = get_mp3_duration(mp3_path_title)
    print(titleLength)


    # Combine audio with video
    combine_audio_random_start(videoPath, mp3_path_fulltext, finishedVidPath, finishedVidNameaudio, fps=60)

    # Get Deepgram transcription and generate subtitles
    output = getDeepgramTranscription(originalMP3file_FullText, deepgramapiKey, titleLength)
    subtitle_data = output['results']['channels'][0]['alternatives'][0]['words']

    # Extract the filename from the URL
    filename = os.path.basename(originalMP3file_FullText)
    name, extension = os.path.splitext(filename)
    output_filename = name + ".srt"

    # Write a subtitle (.srt) file with word-level timestamps
    convert_to_srt(subtitle_data, output_filename)
    srtfilename = output_filename

    # Copy the video file
    shutil.copy(os.path.join(finishedVidPath, finishedVidNameaudio), finishedVidwithSubtitles)

    # Add subtitles using FFmpeg
    output_video = finishedVidwithSubtitles.replace(".mp4", "_wordlevel_subtitles.mp4")
    os.system(f"ffmpeg -i {finishedVidwithSubtitles} -vf subtitles={srtfilename}:force_style='Alignment=10' {output_video}")

    # Copy the final video with subtitles
    parent_directory = os.path.dirname(finishedVidwithSubtitles)
    copy_path = os.path.join(parent_directory, output_video)

    if os.path.exists(output_video):
        # Check if source and destination paths are the same
        if output_video != copy_path:
            # Copy the final video with subtitles
            shutil.copy(output_video, copy_path)
        else:
            print(f"Error: Source and destination paths are the same. Cannot copy the file.")
    else:
        print(f"Error: {output_video} does not exist.")

    AddingScreenShot(video_path, title_path, output_path, titleLength)

if __name__ == "__main__":
    main()







