from flask import Flask, render_template, request, send_file, url_for, redirect, flash, jsonify, session
import os
import uuid
from yt_dlp import YoutubeDL
import time
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create downloads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Language translations
translations = {
    'en': {
        'title': 'HD Reels Downloader',
        'home': 'Home',
        'about': 'About',
        'download_reels': 'Download Instagram Reels in Original Quality',
        'quality_message': 'Our downloader preserves the original video quality and dimensions, ensuring you get the exact same quality as the original Instagram Reel.',
        'paste_url': 'Paste Instagram Reel URL',
        'check_formats': 'Check Formats',
        'analyzing': 'Analyzing video formats...',
        'finding_best': 'Finding the best quality for you',
        'video_found': 'Video found',
        'select_quality': 'Select Quality',
        'auto_best': '🌟 Auto (Best Quality)',
        'convert_mov': 'Convert to MOV format (Ultra High Quality)',
        'mov_note': 'MOV format preserves the highest possible quality but results in larger file sizes',
        'instagram_compatible': 'Instagram Compatible (H.264 MP4 HD)',
        'instagram_note': 'Optimized for Instagram upload - H.264 codec, high quality, smaller file size',
        'download_selected': 'Download in Selected Quality',
        'back': 'Back to URL Entry',
        'how_works': 'How It Works',
        'copy_url': 'Copy URL',
        'copy_url_desc': 'Copy the URL of the Instagram Reel you want to download',
        'select_quality_step': 'Select Quality',
        'select_quality_desc': 'Choose your preferred quality level, including original MOV format if available',
        'save_video': 'Save Video',
        'save_video_desc': 'Save the video to your device in its original quality',
        'quality_features': 'Quality Features',
        'original_resolution': 'Original resolution (up to 4K)',
        'original_framerate': 'Original frame rate',
        'original_aspect': 'Original aspect ratio',
        'high_quality_audio': 'High-quality audio',
        'mov_support': 'MOV format support',
        'ultra_hd': 'Ultra HD quality',
        'ready_download': 'Ready to download in highest quality?',
        'get_started': 'Get started now and experience the best quality Instagram Reels downloads',
        'start_downloading': 'Start Downloading',
        'footer_text': 'Download Instagram Reels in their original quality',
        'copyright': '© 2023 HD Reels Downloader. All rights reserved.',
        'download_success': 'Download Successful!',
        'processed_ready': 'Your video has been processed and is ready to download in original quality.',
        'video_details': 'Video Details',
        'content_info': 'Content Info',
        'title_label': 'Title',
        'file_label': 'File',
        'quality_info': 'Quality Info',
        'resolution': 'Resolution',
        'format': 'Format',
        'file_type': 'File Type',
        'ultra_hd_badge': 'ULTRA HD',
        'mov_quality_message': 'This video has been downloaded in MOV format for ultra-high quality preservation. This is the highest quality possible!',
        'original_quality_message': 'This video has been downloaded in its original quality to preserve all details and dimensions.',
        'download_now': 'Download Now',
        'back_home': 'Back to Home',
        'want_more': 'Want to download more?',
        'more_downloads': 'You can download more Instagram Reels in original high quality by returning to the home page.',
        'download_another': 'Download Another Reel',
        'language': 'Language',
        'english': 'English',
        'turkish': 'Türkçe',
        'about_description': 'HD Reels Downloader is a powerful web application that allows you to download Instagram Reels videos in the highest quality available, including 4K HD format when available.',
        'about_mission_title': 'Our Mission',
        'about_mission_text': 'Our mission is to provide a simple and efficient way for users to download and save Instagram Reels videos in their original quality for offline viewing.',
        'about_tech_title': 'Technology',
        'about_tech_text': 'We use advanced technologies like yt-dlp and FFmpeg to extract and process videos in their highest quality format, ensuring you get the best possible viewing experience.',
        'about_privacy_title': 'Privacy & Security',
        'about_privacy_text': 'We respect your privacy. We don\'t store your videos permanently, and all downloads are deleted automatically after a short period. We don\'t track or store any personal information.',
        'about_start_title': 'Ready to download your first Reel?',
        'about_start_text': 'Start downloading Instagram Reels in original quality now!',
        'originalize': 'Originalize Video (Slowdown Rate)',
        'originalize_note': 'Slightly slows down the video speed and changes the audio tempo to bypass duplicate content and copyright matching algorithms.',
        'normal_speed': 'Normal Speed',
    },
    'tr': {
        'title': 'HD Reels İndirici',
        'home': 'Ana Sayfa',
        'about': 'Hakkında',
        'download_reels': 'Instagram Reels\'i Orijinal Kalitede İndir',
        'quality_message': 'İndirme aracımız, orijinal video kalitesini ve boyutlarını korur, böylece orijinal Instagram Reel ile tamamen aynı kaliteyi elde edersiniz.',
        'paste_url': 'Instagram Reel URL\'sini Yapıştır',
        'check_formats': 'Formatları Kontrol Et',
        'analyzing': 'Video formatları analiz ediliyor...',
        'finding_best': 'Sizin için en iyi kaliteyi buluyoruz',
        'video_found': 'Video bulundu',
        'select_quality': 'Kalite Seç',
        'auto_best': '🌟 Otomatik (En İyi Kalite)',
        'convert_mov': 'MOV formatına dönüştür (Ultra Yüksek Kalite)',
        'mov_note': 'MOV formatı mümkün olan en yüksek kaliteyi korur ancak daha büyük dosya boyutlarına neden olur',
        'instagram_compatible': 'Instagram Uyumlu (H.264 MP4 HD)',
        'instagram_note': 'Instagram yükleme için optimize edilmiş - H.264 codec, yüksek kalite, küçük dosya boyutu',
        'download_selected': 'Seçilen Kalitede İndir',
        'back': 'URL Girişine Geri Dön',
        'how_works': 'Nasıl Çalışır',
        'copy_url': 'URL\'yi Kopyala',
        'copy_url_desc': 'İndirmek istediğiniz Instagram Reel\'in URL\'sini kopyalayın',
        'select_quality_step': 'Kalite Seç',
        'select_quality_desc': 'Orijinal MOV formatı dahil olmak üzere tercih ettiğiniz kalite seviyesini seçin',
        'save_video': 'Videoyu Kaydet',
        'save_video_desc': 'Videoyu orijinal kalitesinde cihazınıza kaydedin',
        'quality_features': 'Kalite Özellikleri',
        'original_resolution': 'Orijinal çözünürlük (4K\'ya kadar)',
        'original_framerate': 'Orijinal kare hızı',
        'original_aspect': 'Orijinal en-boy oranı',
        'high_quality_audio': 'Yüksek kaliteli ses',
        'mov_support': 'MOV format desteği',
        'ultra_hd': 'Ultra HD kalite',
        'ready_download': 'En yüksek kalitede indirmeye hazır mısınız?',
        'get_started': 'Hemen başlayın ve en iyi kalitede Instagram Reels indirme deneyimini yaşayın',
        'start_downloading': 'İndirmeye Başla',
        'footer_text': 'Instagram Reels\'i orijinal kalitesinde indirin',
        'copyright': '© 2023 HD Reels İndirici. Tüm hakları saklıdır.',
        'download_success': 'İndirme Başarılı!',
        'processed_ready': 'Videonuz işlendi ve orijinal kalitede indirilmeye hazır.',
        'video_details': 'Video Detayları',
        'content_info': 'İçerik Bilgisi',
        'title_label': 'Başlık',
        'file_label': 'Dosya',
        'quality_info': 'Kalite Bilgisi',
        'resolution': 'Çözünürlük',
        'format': 'Format',
        'file_type': 'Dosya Türü',
        'ultra_hd_badge': 'ULTRA HD',
        'mov_quality_message': 'Bu video, ultra yüksek kalite koruması için MOV formatında indirildi. Bu mümkün olan en yüksek kalitedir!',
        'original_quality_message': 'Bu video, tüm detayları ve boyutları korumak için orijinal kalitesinde indirildi.',
        'download_now': 'Şimdi İndir',
        'back_home': 'Ana Sayfaya Dön',
        'want_more': 'Daha fazla indirmek ister misiniz?',
        'more_downloads': 'Ana sayfaya dönerek daha fazla Instagram Reels\'i orijinal yüksek kalitede indirebilirsiniz.',
        'download_another': 'Başka Bir Reel İndir',
        'language': 'Dil',
        'english': 'English',
        'turkish': 'Türkçe',
        'about_description': 'HD Reels İndirici, Instagram Reels videolarını mümkün olan en yüksek kalitede, mevcut olduğunda 4K HD formatı dahil olmak üzere indirmenize olanak tanıyan güçlü bir web uygulamasıdır.',
        'about_mission_title': 'Misyonumuz',
        'about_mission_text': 'Misyonumuz, kullanıcılara Instagram Reels videolarını orijinal kalitelerinde çevrimdışı izlemek için indirme ve kaydetme konusunda basit ve verimli bir yol sunmaktır.',
        'about_tech_title': 'Teknoloji',
        'about_tech_text': 'Videoları en yüksek kalite formatında çıkarmak ve işlemek için yt-dlp ve FFmpeg gibi gelişmiş teknolojiler kullanıyoruz, böylece mümkün olan en iyi izleme deneyimini elde edersiniz.',
        'about_privacy_title': 'Gizlilik ve Güvenlik',
        'about_privacy_text': 'Gizliliğinize saygı duyuyoruz. Videolarınızı kalıcı olarak saklamıyoruz ve tüm indirmeler kısa bir süre sonra otomatik olarak siliniyor. Hiçbir kişisel bilgiyi takip etmiyor veya saklamıyoruz.',
        'about_start_title': 'İlk Reel\'inizi indirmeye hazır mısınız?',
        'about_start_text': 'Instagram Reels\'i orijinal kalitede şimdi indirmeye başlayın!',
        'originalize': 'Videoyu Özgünleştir (Hız Ayarı)',
        'originalize_note': 'Telif ve kopya içerik tespiti algoritmalarını aşmak için video hızını hafifçe yavaşlatır ve ses temposunu senkronize eder.',
        'normal_speed': 'Normal Hız',
    }
}

def get_available_formats(url):
    """
    Get all available formats for a video URL
    
    Args:
        url: URL of the Instagram Reel
        
    Returns:
        List of available formats with their details
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            print(f"Extracted {len(info.get('formats', []))} total formats")
            
            # Process and filter formats
            for f in info.get('formats', []):
                # Skip formats without video
                if f.get('vcodec') == 'none':
                    continue
                    
                # Create format info with null handling
                format_info = {
                    'format_id': f.get('format_id', 'unknown'),
                    'ext': f.get('ext', 'mp4'),  # Default to mp4 if null
                    'resolution': f"{f.get('width', 'N/A')}x{f.get('height', 'N/A')}",
                    'fps': f.get('fps', 'N/A'),
                    'vcodec': f.get('vcodec', 'N/A'),
                    'acodec': f.get('acodec', 'N/A'),
                    'filesize': f.get('filesize', 'N/A'),
                    'format_note': f.get('format_note', ''),
                    'quality': f.get('quality', 0),
                }
                formats.append(format_info)
                print(f"Added format: {format_info['format_id']} - {format_info['resolution']} - {format_info['ext']}")
            
            # Sort formats by quality
            formats.sort(key=lambda x: x['quality'], reverse=True)
            
            # Ensure we have at least one format
            if not formats:
                print("No valid formats found, creating default format")
                # Create a default format if none are available
                formats = [{
                    'format_id': 'best',
                    'ext': 'mp4',
                    'resolution': 'N/AxN/A',
                    'fps': 'N/A',
                    'vcodec': 'N/A',
                    'acodec': 'N/A',
                    'filesize': 'N/A',
                    'format_note': 'Default format',
                    'quality': 0,
                }]
            
            print(f"Returning {len(formats)} valid formats")
            return formats, info.get('title', 'Video')
    except Exception as e:
        print(f"Error getting formats: {str(e)}")
        # Return a default format if there's an error
        return [{
            'format_id': 'best',
            'ext': 'mp4',
            'resolution': 'N/AxN/A',
            'fps': 'N/A',
            'vcodec': 'N/A',
            'acodec': 'N/A',
            'filesize': 'N/A',
            'format_note': 'Default format (error occurred)',
            'quality': 0,
        }], 'Video'

def transcode_video(filepath, instagram_compatible=False, slowdown_percent=0):
    """
    Transcode the downloaded video file to standard H.264 / AAC 8-bit to ensure
    maximum compatibility with Adobe Premiere Pro and standard video editors.
    """
    if not filepath or not os.path.exists(filepath):
        return filepath

    import subprocess
    temp_output_path = os.path.splitext(filepath)[0] + "_transcoded" + os.path.splitext(filepath)[1]
    
    ffmpeg_cmd = ['ffmpeg', '-y', '-i', filepath]
    
    if instagram_compatible:
        ffmpeg_cmd.extend([
            '-c:v', 'libx264',
            '-profile:v', 'high',
            '-level', '4.2',
            '-pix_fmt', 'yuv420p',
            '-crf', '18',
            '-preset', 'slow',
            '-movflags', '+faststart',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-ac', '2'
        ])
    else:
        ffmpeg_cmd.extend([
            '-c:v', 'libx264',
            '-crf', '15',
            '-preset', 'slow',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '256k'
        ])

    if slowdown_percent > 0:
        setpts_val = 1.0 + (slowdown_percent / 100.0)
        atempo_val = 1.0 - (slowdown_percent / 100.0)
        ffmpeg_cmd.extend([
            '-vf', f'setpts={setpts_val:.2f}*PTS',
            '-af', f'atempo={atempo_val:.2f}'
        ])

    ffmpeg_cmd.extend([
        '-map_metadata', '-1',
        '-metadata', 'title=HD Reels Downloader',
        '-metadata', 'artist=seghobs',
        '-metadata', 'comment=Downloaded via reelsdownloadHDv2'
    ])
    
    ffmpeg_cmd.append(temp_output_path)
    
    try:
        print(f"Running custom ffmpeg transcoding: {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if os.path.exists(temp_output_path):
            os.remove(filepath)
            os.rename(temp_output_path, filepath)
            print("Transcoding completed successfully!")
    except Exception as e:
        print(f"Custom ffmpeg transcoding failed: {str(e)}")
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
            except Exception:
                pass
    return filepath

def download_reel(url, output_dir, format_id=None, convert_to_mov=False, instagram_compatible=False, slowdown_percent=0):
    """
    Download Instagram Reels video in specified quality
    
    Args:
        url: URL of the Instagram Reel
        output_dir: Directory to save the downloaded video
        format_id: Specific format ID to download (if None, best quality is chosen)
        convert_to_mov: Whether to convert the output to MOV format
        instagram_compatible: Whether to make the video Instagram-compatible (H.264 MP4)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate unique filename to prevent conflicts
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(output_dir, f"{unique_id}_%(title)s.%(ext)s")
    
    # Configure yt-dlp options for highest quality download
    ydl_opts = {
        'outtmpl': output_template,
        'writethumbnail': True,
        'verbose': True,
    }
    
    # If format_id is specified and not empty, use it
    if format_id and format_id.strip():
        ydl_opts['format'] = format_id
    else:
        # Otherwise use best quality available with fallback options
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        # 8K (7680x4320), 4K (3840x2160), 1440p, 1080p, 720p öncelik sırası
        ydl_opts['format_sort'] = ['res:7680', 'res:4320', 'res:3840', 'res:2160', 'res:1440', 'res:1080', 'res:720', 'fps:60', 'codec:h264']
    
    # Add post-processors
    postprocessors = []
    
    # If convert_to_mov is True, convert to MOV format
    if convert_to_mov:
        postprocessors.append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mov',
        })
    else:
        postprocessors.append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        })
    
    # Add other post-processors
    postprocessors.extend([
        {'key': 'FFmpegMetadata'},
        {'key': 'EmbedThumbnail'},
    ])
    
    ydl_opts['postprocessors'] = postprocessors
    
    # Add FFmpeg parameters
    if instagram_compatible:
        # Instagram-compatible settings
        ydl_opts['postprocessor_args'] = {
            'FFmpegVideoConvertor': [
                '-c:v', 'libx264',           # H.264 codec
                '-profile:v', 'high',        # High profile for better quality
                '-level', '4.2',             # Level 4.2 for compatibility
                '-pix_fmt', 'yuv420p',       # Pixel format compatible with Instagram
                '-crf', '18',                # High quality (lower = better quality)
                '-preset', 'slow',           # Better compression
                '-movflags', '+faststart',   # Optimize for streaming
                '-c:a', 'aac',               # AAC audio codec
                '-b:a', '128k',              # Audio bitrate
                '-ar', '44100',              # Audio sample rate
                '-ac', '2'                   # Stereo audio
            ],
        }
    else:
        # Original high quality parameters (compatible with Premiere Pro and video editors)
        ydl_opts['postprocessor_args'] = {
            'FFmpegVideoConvertor': [
                '-c:v', 'libx264',
                '-crf', '15',
                '-preset', 'slow',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '256k'
            ],
        }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Video')
            
            # Get the filepath of the downloaded video
            if 'requested_downloads' in info and info['requested_downloads']:
                filepath = info['requested_downloads'][0]['filepath']
                
                # Get video details for display
                width = info.get('width', 'Unknown')
                height = info.get('height', 'Unknown')
                format_note = info.get('format_note', 'Unknown')
                ext = os.path.splitext(filepath)[1][1:]  # Get file extension
                
                print(f"Downloaded video: {video_title}")
                print(f"Resolution: {width}x{height}")
                print(f"Format: {format_note}")
                print(f"Extension: {ext}")
                
                filepath = transcode_video(filepath, instagram_compatible, slowdown_percent)
                return filepath, video_title, f"{width}x{height}", format_note, ext
            else:
                print("No requested downloads found in info")
                return None, video_title, "Unknown", "Unknown", "Unknown"
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        # Try with a simpler format if the first attempt fails
        try:
            print("Retrying with simpler format...")
            ydl_opts['format'] = 'best'
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Video')
                
                if 'requested_downloads' in info and info['requested_downloads']:
                    filepath = info['requested_downloads'][0]['filepath']
                    width = info.get('width', 'Unknown')
                    height = info.get('height', 'Unknown')
                    format_note = info.get('format_note', 'Unknown')
                    ext = os.path.splitext(filepath)[1][1:]
                    
                    print(f"Successfully downloaded with fallback format: {video_title}")
                    filepath = transcode_video(filepath, instagram_compatible, slowdown_percent)
                    return filepath, video_title, f"{width}x{height}", format_note, ext
                else:
                    return None, video_title, "Unknown", "Unknown", "Unknown"
        except Exception as fallback_error:
            print(f"Fallback download also failed: {str(fallback_error)}")
            return None, None, "Unknown", "Unknown", "Unknown"

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    lang = session.get('lang', 'en')
    if lang not in translations:
        lang = 'en'
    return render_template('index.html', lang=lang, t=translations[lang])

@app.route('/get_formats', methods=['POST'])
def get_formats():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL (basic check)
    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    try:
        formats, title = get_available_formats(url)
        return jsonify({
            'formats': formats,
            'title': title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    lang = session.get('lang', 'en')
    if lang not in translations:
        lang = 'en'
    t = translations[lang]
    
    if request.method == 'POST':
        url = request.form.get('url')
        format_id = request.form.get('format_id')
        convert_to_mov = request.form.get('convert_to_mov') == 'true'
        instagram_compatible = request.form.get('instagram_compatible') == 'true'
        try:
            slowdown_percent = int(request.form.get('slowdown_percent', 0))
        except ValueError:
            slowdown_percent = 0
        
        if not url:
            flash('Please enter a valid URL', 'error')
            return redirect(url_for('index'))
        
        # Validate URL (basic check)
        if not url.startswith(('http://', 'https://')):
            flash('Please enter a valid URL starting with http:// or https://', 'error')
            return redirect(url_for('index'))
        
        # Handle null or empty format_id
        if format_id is None or format_id.strip() == '':
            format_id = None  # This will trigger auto-best quality selection
        
        try:
            # Show processing message
            flash('Processing your download request...', 'info')
            
            # Download the video with specified format
            filepath, video_title, resolution, format_note, ext = download_reel(
                url, 
                app.config['UPLOAD_FOLDER'], 
                format_id=format_id,
                convert_to_mov=convert_to_mov,
                instagram_compatible=instagram_compatible,
                slowdown_percent=slowdown_percent
            )
            
            if filepath and os.path.exists(filepath):
                # Get filename from path
                filename = os.path.basename(filepath)
                # Return success template with download link and video details
                return render_template('success.html', 
                                      filename=filename,
                                      video_title=video_title,
                                      resolution=resolution,
                                      format_note=format_note,
                                      file_extension=ext,
                                      download_url=url_for('download_file', filename=filename),
                                      lang=lang,
                                      t=t)
            else:
                flash('Failed to download video. Please check the URL and try again.', 'error')
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    lang = session.get('lang', 'en')
    if lang not in translations:
        lang = 'en'
    return render_template('about.html', lang=lang, t=translations[lang])

if __name__ == '__main__':
    app.run(debug=True) 