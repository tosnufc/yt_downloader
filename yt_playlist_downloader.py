import yt_dlp
import sys
import urllib.parse
import pyperclip
import os
import re

def is_youtube_playlist_url(url):
    """Check if the URL is a valid YouTube playlist URL"""
    playlist_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?.*list=[\w-]+',
    ]
    
    for pattern in playlist_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True
    return False

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes is None:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def download_playlist(url, output_path="playlist_results"):
    try:
        # Clean and decode the URL
        url = urllib.parse.unquote(url).replace('\\', '')
        
        # Validate YouTube playlist URL
        if not is_youtube_playlist_url(url):
            print("Error: The provided URL is not a valid YouTube playlist URL!")
            return
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(playlist_index)02d - %(title)s.%(ext)s',
            'progress_hooks': [lambda d: print(f"Downloading: {d.get('_percent_str', '?%')} of {format_size(d.get('_total_bytes', d.get('_total_bytes_estimate', None)))} - {d.get('filename', 'Unknown')}")],
            'verbose': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,  # Continue downloading even if some videos fail
            'extract_flat': False,  # Extract full info for each video
            'playliststart': 1,  # Start from first video
            'playlistend': None,  # Download all videos
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nFetching playlist information...")
            info = ydl.extract_info(url, download=False)
            
            if 'entries' not in info:
                print("Error: No videos found in the playlist!")
                return
            
            playlist_title = info.get('title', 'Unknown Playlist')
            video_count = len([entry for entry in info['entries'] if entry is not None])
            
            print(f"Playlist: {playlist_title}")
            print(f"Total videos: {video_count}")
            print(f"Downloading to: {os.path.abspath(output_path)}")
            print("=" * 60)
            
            # Download the entire playlist
            ydl.download([url])
            
            print("\n" + "=" * 60)
            print("Playlist download completed successfully!")
            print(f"All videos saved to: {os.path.abspath(output_path)}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_playlist_info(url):
    """Get basic information about the playlist without downloading"""
    try:
        # Clean and decode the URL
        url = urllib.parse.unquote(url).replace('\\', '')
        
        # Validate YouTube playlist URL
        if not is_youtube_playlist_url(url):
            print("Error: The provided URL is not a valid YouTube playlist URL!")
            return None
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # Changed from True to False to get full info
            'skip_download': True,  # Don't download, just extract info
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting playlist information...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("Error: Could not extract information from URL")
                return None
                
            if 'entries' not in info:
                print("Error: No playlist entries found")
                return None
            
            # Filter out None entries
            valid_entries = [entry for entry in info['entries'] if entry is not None]
            
            playlist_info = {
                'title': info.get('title', 'Unknown Playlist'),
                'uploader': info.get('uploader', 'Unknown'),
                'video_count': len(valid_entries),
                'url': url
            }
            
            return playlist_info
            
    except Exception as e:
        print(f"Error getting playlist info: {str(e)}")
        return None

if __name__ == "__main__":
    # Get URL from clipboard
    url = pyperclip.paste().strip()
    
    if not url:
        print("No URL found in clipboard!")
        sys.exit(1)
    
    print(f"Found URL in clipboard: {url}")
    
    if not is_youtube_playlist_url(url):
        print("The provided URL is not a valid YouTube playlist URL!")
        print("Please copy a valid YouTube playlist URL to your clipboard.")
        print("Example: https://www.youtube.com/playlist?list=...")
        sys.exit(1)
    
    print("✓ URL validation passed")
    print(f"Found playlist URL in clipboard: {url}")
    
    # Get playlist info first
    playlist_info = get_playlist_info(url)
    if not playlist_info:
        print("Could not retrieve playlist information!")
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- Invalid or private playlist")
        print("- YouTube access restrictions")
        sys.exit(1)
    
    print(f"\nPlaylist Information:")
    print(f"Title: {playlist_info['title']}")
    print(f"Uploader: {playlist_info['uploader']}")
    print(f"Video Count: {playlist_info['video_count']}")
    
    # Confirm download
    confirm = input(f"\nDo you want to download all {playlist_info['video_count']} videos in highest quality? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Download cancelled.")
        sys.exit(0)
    
    # Get output path from command line if provided, otherwise use playlist_results folder
    output_path = sys.argv[1] if len(sys.argv) > 1 else "playlist_results"
    
    print(f"\nStarting playlist download in highest quality...")
    
    # Download the entire playlist
    download_playlist(url, output_path) 