import yt_dlp
import sys
import urllib.parse
import pyperclip
import os
import re

def is_youtube_url(url):
    """Check if the URL is a valid YouTube URL"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+',
    ]
    
    for pattern in youtube_patterns:
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

def format_bitrate(bitrate):
    """Convert bitrate to human readable format"""
    if bitrate is None:
        return "Unknown"
    return f"{bitrate/1000:.1f}kbps"

def format_fps(fps):
    """Format FPS value"""
    if fps is None:
        return "N/A"
    return f"{fps:.0f}"

def estimate_size(format_info, duration):
    """Estimate file size using multiple methods"""
    # Try direct filesize first
    if format_info.get('filesize'):
        return format_info['filesize']
    
    # Try approximate filesize
    if format_info.get('filesize_approx'):
        return format_info['filesize_approx']
    
    # Try to estimate from bitrate
    if format_info.get('tbr') and duration:
        # tbr is in kbps, convert to bytes
        return (format_info['tbr'] * 1000 * duration) / 8
    
    return None

def list_formats(url):
    # Clean and decode the URL
    url = urllib.parse.unquote(url).replace('\\', '')
    
    # Validate YouTube URL
    if not is_youtube_url(url):
        print("Error: The provided URL is not a valid YouTube URL!")
        return []
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        duration = info.get('duration')
        
        # Filter for video formats and sort by quality (highest first)
        video_formats = [f for f in formats if f.get('height') is not None and f.get('ext') != 'mhtml']
        video_formats.sort(key=lambda x: (x.get('height', 0), x.get('tbr', 0), x.get('filesize', 0)), reverse=True)
        
        print("\nAvailable video formats (highest quality first):")
        print("Resolution  |  Filesize  |  Bitrate   |  FPS  |  Extension")
        print("-" * 60)
        
        for i, f in enumerate(video_formats, 1):
            filesize = estimate_size(f, duration)
            filesize_str = format_size(filesize)
            bitrate = f.get('tbr', f.get('vbr', None))
            bitrate_str = format_bitrate(bitrate)
            fps_str = format_fps(f.get('fps'))
            print(f"{i:2d}. {f.get('height', 'N/A'):4d}p      | {filesize_str:9s} | {bitrate_str:9s} | {fps_str:4s} | {f['ext']}")
        
        return video_formats

def get_quality_label(height):
    """Convert video height to quality label"""
    if height is None:
        return "Unknown"
    elif height <= 480:
        return "SD"
    elif height <= 720:
        return "HD"
    elif height <= 1080:
        return "FHD"
    elif height <= 1440:
        return "QHD"
    elif height <= 2160:
        return "4K"
    elif height <= 4320:
        return "8K"
    else:
        return f"{height}p"

def download_video(url, output_path="results", format_id=None):
    try:
        # Clean and decode the URL
        url = urllib.parse.unquote(url).replace('\\', '')
        
        # Validate YouTube URL
        if not is_youtube_url(url):
            print("Error: The provided URL is not a valid YouTube URL!")
            return
        
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # First, get video info to determine quality
        info_opts = {
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            print("\nFetching video information...")
            info = ydl.extract_info(url, download=False)
            
            # Get the best format to determine quality
            if format_id:
                selected_format = next((f for f in info['formats'] if f.get('format_id') == format_id), None)
            else:
                # Get the format that would be selected by our format string
                formats = info['formats']
                video_formats = [f for f in formats if f.get('height') is not None and f.get('vcodec') != 'none']
                if video_formats:
                    selected_format = max(video_formats, key=lambda x: (x.get('height', 0), x.get('tbr', 0)))
                else:
                    selected_format = max(formats, key=lambda x: (x.get('height', 0) or 0, x.get('tbr', 0) or 0))
            
            quality_label = get_quality_label(selected_format.get('height') if selected_format else None)
            
            print(f"Title: {info['title']}")
            print(f"Duration: {info['duration']} seconds")
            print(f"Quality: {quality_label}")
            print(f"Downloading to: {os.path.abspath(output_path)}")
        
        ydl_opts = {
            'format': format_id if format_id else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(title)s [{quality_label}].%(ext)s',
            'progress_hooks': [lambda d: print(f"Downloading: {d.get('_percent_str', '?%')} of {format_size(d.get('_total_bytes', d.get('_total_bytes_estimate', None)))}")],
            'verbose': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Starting download...")
            ydl.download([url])
            print("Download completed successfully!")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Get URL from clipboard
    url = pyperclip.paste().strip()
    
    if not url:
        print("No URL found in clipboard!")
        sys.exit(1)
    
    if not is_youtube_url(url):
        print("The provided URL is not a valid YouTube URL!")
        sys.exit(1)
    
    print(f"Found URL in clipboard: {url}")
    
    # Get output path from command line if provided, otherwise use results folder
    output_path = sys.argv[1] if len(sys.argv) > 1 else "results"
    
    print("Downloading best quality video with audio...")
    
    # Download the video with best quality that includes audio
    download_video(url, output_path)