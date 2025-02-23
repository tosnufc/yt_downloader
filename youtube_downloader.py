import yt_dlp
import sys
import urllib.parse

def list_formats(url):
    # Clean and decode the URL
    url = urllib.parse.unquote(url).replace('\\', '')
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        
        # Filter for video formats and sort by quality
        video_formats = [f for f in formats if f.get('height') is not None]
        video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
        
        print("\nAvailable video formats:")
        print("Format ID  |  Resolution  |  Filesize  |  Extension")
        print("-" * 50)
        
        for i, f in enumerate(video_formats, 1):
            filesize = f.get('filesize', 'N/A')
            if filesize != 'N/A':
                filesize = f"{filesize / 1024 / 1024:.1f}MB"
            print(f"{i:2d}. {f['format_id']:8s} | {f.get('height', 'N/A'):4d}p      | {filesize:9s} | {f['ext']}")
        
        return video_formats

def download_video(url, output_path=".", format_id=None):
    try:
        # Clean and decode the URL
        url = urllib.parse.unquote(url).replace('\\', '')
        
        ydl_opts = {
            'format': format_id if format_id else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: print(f"Downloading: {d.get('_percent_str', '?%')} of {d.get('_total_bytes_str', '?MB')}")],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nFetching video information...")
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info['title']}")
            print(f"Duration: {info['duration']} seconds")
            print("Starting download...")
            ydl.download([url])
            print("Download completed successfully!")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <youtube_url> [output_path]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # List available formats
    video_formats = list_formats(url)
    
    # Get user choice
    while True:
        try:
            choice = int(input("\nEnter the number of the format you want to download (0 for best quality): "))
            if choice == 0:
                format_id = None
                break
            elif 1 <= choice <= len(video_formats):
                format_id = video_formats[choice-1]['format_id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Download the video
    download_video(url, output_path, format_id)