import yt_dlp
import sys
import urllib.parse

def download_video(url, output_path="."):
    try:
        # Clean and decode the URL
        url = urllib.parse.unquote(url).replace('\\', '')
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: print(f"Downloading: {d.get('_percent_str', '?%')} of {d.get('_total_bytes_str', '?MB')}")],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Fetching video information...")
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
    
    download_video(url, output_path)