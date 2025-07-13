#!/usr/bin/env python3
import os
import sys
import argparse
from yt_dlp import YoutubeDL

def download_reel(url, output_dir=None):
    """
    Download Instagram Reels video in highest quality
    
    Args:
        url: URL of the Instagram Reel
        output_dir: Directory to save the downloaded video
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_template = '%(title)s.%(ext)s'
    if output_dir:
        output_template = os.path.join(output_dir, output_template)
    
    # Configure yt-dlp options for highest quality download with fallback options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prioritize MPD/DASH formats with fallbacks
        'outtmpl': output_template,
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        'verbose': True,
        'format_sort': ['res:2160', 'res:1440', 'res:1080', 'res:720', 'fps:60', 'codec:h264'],  # Quality preferences
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Successfully downloaded: {info.get('title', 'Video')}")
            return info.get('requested_downloads', [{}])[0].get('filepath', None)
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download Instagram Reels in highest quality')
    parser.add_argument('url', help='URL of the Instagram Reel')
    parser.add_argument('-o', '--output-dir', help='Directory to save the downloaded video')
    
    args = parser.parse_args()
    
    downloaded_file = download_reel(args.url, args.output_dir)
    if downloaded_file:
        print(f"Video saved to: {downloaded_file}")
    else:
        print("Failed to download video")

if __name__ == "__main__":
    main() 