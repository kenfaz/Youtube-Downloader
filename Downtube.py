"""
A CLI based downloader to download YouTube videos.
"""
import sys
from pytube import YouTube, Playlist
import argparse
from pytube. innertube import _default_clients
from pytube import cipher
import re
import os
from moviepy.editor import * 
from colorama import Fore
import datetime



_default_clients[ "ANDROID"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients[ "ANDROID_EMBED"][ "context"][ "client"]["clientVersion"] = "19.08.35"
_default_clients[ "IOS_EMBED"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"][ "context"]["client"]["clientVersion"] = "6.41"
_default_clients[ "ANDROID_MUSIC"] = _default_clients[ "ANDROID_CREATOR" ]


def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name

# TODO: Convert date to readable date.
# TODO: Prettify with the rich library.
# TODO: Fix the path problem for file conversion.
# TODO: Create a new directory for playlist downloads.
# TODO: Add a progress bar for playlist downloads.
# TODO: Add download retries for playlist downloads.

def convert_to_audio(file: str, dir=''):
    video = AudioFileClip(os.getcwd() + '\\' + dir + '\\' + file)
    video.write_audiofile(os.getcwd() + '\\' + dir + '\\' + file.rstrip('.mp4') + '.mp3')
    os.remove(os.getcwd() + '\\' + dir + '\\' + file)

def create_logs(items, start: object):
    try:
        os.mkdir('Download Logs')
    except FileExistsError:
        pass

    date = datetime.datetime.now()
    with open(f"{os.getcwd()}\\Download Logs\\Download Logs ({date.strftime('%B %d, %Y')}).txt", "a") as f:
        f.write(('=' * 50) + '\n')
        f.write(f"Downloads started at {start.strftime('%I:%M:%S %p')}\n")
        f.write(('-' * 50) + '\n')
        for i in range(len(items)):
            f.write(f"{i+1}. {items[i]}\n")
        f.write(('-' * 50) + '\n')
        f.write(f"Downloads finished at {date.strftime('%I:%M:%S %p')}\n")
        f.write(('=' * 50) + '\n\n')

def download_yt_object(stream: list, stream_number: int, yt_object: object, audio=False):
    stream = stream.get_by_itag(stream_number)
    print("Download is starting...")
    print("=" * 60)
    print(f"Title: {yt_object.title}")
    print(f"Author: {yt_object.author}")
    print(f"Date Published: {yt_object.publish_date}")
    print(f"Length: {yt_object.length}")
    print(f"Views: {yt_object.views}")
    print(f"Rating: {yt_object.rating}")
    print(f"File size: {stream.filesize}")
    print("=" * 60)
    stream.download()

def download_playlist(url, audio=False):
    playlist = Playlist(url)
    ans = input(f'This playlist contains {len(playlist.video_urls)} items. Proceed to download? Y/N: ')
    if ans.lower() in ['y', 'yes']:
        directory = []
        added_items = []
        date_start = datetime.datetime.now()
        try:
            os.mkdir(playlist.title)
        except FileExistsError:
            directory = os.listdir(playlist.title)
        dirs = (playlist.title)
        failed, success = 0, 0
        for video in playlist.videos:
            if video.title + '.mp3' not in directory and video.title + '.mp4' not in directory:
                try: 
                    video.streams.first().download(os.getcwd() + '\\' + dirs)
                    print(f'Title: {video.title} | Channel: {video.author}')
                except:
                    print('An item cannot be downloaded.')
                if audio:
                    try:
                        print('Converting file to mp3.')
                        print(video.title + '.mp4')
                        convert_to_audio(video.title+'.mp4', dirs)
                        added_items.append(f"{video.title} [SUCCESS]")
                        success += 1
                    except:
                        print('Audio conversion failed.')
                        added_items.append(f"{video.title} [FAILED]")
                        failed += 1
            else:
                print(f'Skipping {video.title} since it already exists.')
        print(f'{Fore.YELLOW}Downloading the playlist is complete with {Fore.GREEN}{success} successful {Fore.YELLOW}downloads and {Fore.RED}{failed}{Fore.RED} failed {Fore.YELLOW}downloads.')
        create_logs(added_items, date_start)
    else:
        print(f'Download for {playlist.title} is cancelled!')

def loading_progress(stream, chunks, chunks_remaining):
    bytes_downloaded = stream.filesize - chunks_remaining
    percentage = (bytes_downloaded/stream.filesize) * 100
    bar = int(percentage // 1) * "#"
    unbar = int(100 - percentage // 1) * "_"
    print(f"[{bar}{unbar}] {percentage:.2f}%", end="\r")

def finished(stream, filepath):
    print(f"\nFinished downloading.")
    print(f"File saved to {filepath}")

def main():
    parser = argparse.ArgumentParser(
        prog="DownTube", description="A program that downloads videos from YouTube", epilog="Have fun!")
    parser.add_argument(
        "-l", "--link", help="The link to the YouTube onject.")
    parser.add_argument(
        "-a", "--mp3", help="Convert downloaded video object to mp3.", action="store_true", default=False)
    parser.add_argument(
        "-p", "--playlist", help="Process a YouTube playlist link.", action="store_true", default=False)
    args = parser.parse_args()
    
    if not args.link:
        if args.playlist:
            link = input("Enter YouTube Playlist link: ")
        else:
            link = input("Enter YouTube link: ")
        try:
            if not args.playlist:
                yt_object = YouTube(
                    link, on_progress_callback=loading_progress, on_complete_callback=finished)
                # Show all streams
                streams = yt_object.streams.filter(progressive=False)
                print(f"Here are available streams:")
                for stream in streams:
                    print(stream)
                stream_number = int(input("Choose stream number to download: "))
                download_yt_object(streams, stream_number, yt_object, args.mp3)
            else:
                download_playlist(link, args.mp3)

        except Exception as e:
            print(e)
            print("YouTube cannot process the given object.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()

