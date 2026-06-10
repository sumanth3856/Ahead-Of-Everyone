import os
import sys
import requests
import urllib.parse
import tempfile
import shutil
from bs4 import BeautifulSoup
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from PIL import Image

# Reconfigure stdout to use UTF-8 to prevent charmap/codec errors on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for Python versions where stdout doesn't have reconfigure
        pass

# Brand Settings
BRAND_NAME = "Ahead of Everyone"
TAGLINE = "Innovating the Future, Today."
COPYRIGHT = "© 2026 Ahead of Everyone. All Rights Reserved."

# Color Palette (Luxury Slate & Neon Green)
COLOR_DARK = (10, 15, 29)        # #0A0F1D (Deep Premium Navy/Slate)
COLOR_GRAY = (74, 85, 104)       # #4A5568 (Slate Grey)
COLOR_LIGHT_GRAY = (247, 250, 252)  # #F7FAFC (Light slate backdrop)
COLOR_NEON = (34, 197, 94)       # #22C55E (Vibrant Neon Green)
COLOR_WHITE = (255, 255, 255)    # #FFFFFF
LOGO_PATH = "logo.svg"

# Fonts directory
FONTS_DIR = "assets"

def download_fonts():
    """Downloads premium editorial fonts from GitHub source repositories."""
    os.makedirs(FONTS_DIR, exist_ok=True)
    fonts = {
        "Montserrat-Bold.ttf": "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf",
        "Montserrat-Regular.ttf": "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Regular.ttf",
        "Merriweather-Regular.ttf": "https://github.com/SorkinType/Merriweather/raw/master/fonts/ttf/Merriweather-Regular.ttf",
        "Merriweather-Italic.ttf": "https://github.com/SorkinType/Merriweather/raw/master/fonts/ttf/Merriweather-Italic.ttf",
        "Merriweather-Bold.ttf": "https://github.com/SorkinType/Merriweather/raw/master/fonts/ttf/Merriweather-Bold.ttf",
    }
    for filename, url in fonts.items():
        filepath = os.path.join(FONTS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Downloading font: {filename}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                print(f"Successfully downloaded {filename}")
            except Exception as e:
                print(f"Error downloading font {filename}: {e}")

class PDF(FPDF):
    def header(self):
        # We don't want headers on cover (page 1) or TOC (page 2)
        if self.page_no() > 2:
            self.set_fill_color(*COLOR_DARK)
            self.rect(0, 0, 210, 25, 'F')
            
            # Draw Logo
            try:
                if os.path.exists(LOGO_PATH):
                    self.image(LOGO_PATH, x=20, y=5, w=15)
            except Exception as e:
                pass
                
            self.set_y(8)
            self.set_x(40)
            self.set_font("Montserrat", "B", 14)
            self.set_text_color(*COLOR_NEON)
            self.cell(w=0, h=10, text=BRAND_NAME.upper(), align="L")
            
            self.set_x(140)
            self.set_font("Montserrat", "", 10)
            self.set_text_color(*COLOR_WHITE)
            date_str = datetime.now().strftime("%B %d, %Y")
            self.cell(w=50, h=10, text=date_str, align="R")
            
            # Bottom border line of header
            self.set_draw_color(*COLOR_NEON)
            self.set_line_width(0.5)
            self.line(20, 25, 190, 25)
            self.set_line_width(0.2)

    def footer(self):
        # We don't want footer on cover (page 1) or TOC (page 2)
        if self.page_no() > 2:
            self.set_y(-20)
            self.set_draw_color(*COLOR_NEON)
            self.set_line_width(0.5)
            self.line(20, self.get_y(), 190, self.get_y())
            self.set_line_width(0.2)
            
            self.set_y(-15)
            self.set_font("Montserrat", "", 9)
            self.set_text_color(*COLOR_GRAY)
            self.set_x(20)
            self.cell(w=80, h=10, text=BRAND_NAME, align="L")
            self.set_x(110)
            self.cell(w=80, h=10, text=f"Page {self.page_no()}", align="R")

def fetch_dynamic_news(limit=5):
    """Scrapes top stories and extracts content & images in single requests."""
    print("Fetching top stories directly from HackerNews HTML...")
    stories = []
    try:
        url = "https://news.ycombinator.com/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all title links
        storylinks = soup.find_all('span', class_='titleline')
        
        for item in storylinks[:limit]:
            link_tag = item.find('a')
            if link_tag:
                title = link_tag.get_text()
                story_url = link_tag.get('href')
                
                # Fix relative URLs
                if story_url.startswith('item?id='):
                    story_url = f"https://news.ycombinator.com/{story_url}"
                
                print(f"Elaborating: {title}")
                content, image_url = elaborate_content_and_image(story_url, title)
                stories.append({
                    "title": title,
                    "url": story_url,
                    "content": content,
                    "image_url": image_url
                })
    except Exception as e:
        print(f"Error fetching news: {e}")
    return stories

def elaborate_content_and_image(url, title):
    """Fetches article page, extracts paragraph texts and official hero image."""
    content = ""
    image_url = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=7)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 1. Try to extract image
        meta_og = soup.find('meta', attrs={'property': 'og:image'}) or soup.find('meta', attrs={'name': 'og:image'})
        if meta_og and meta_og.get('content'):
            image_url = urllib.parse.urljoin(url, meta_og.get('content'))
        else:
            meta_tw = soup.find('meta', attrs={'name': 'twitter:image'}) or soup.find('meta', attrs={'property': 'twitter:image'})
            if meta_tw and meta_tw.get('content'):
                image_url = urllib.parse.urljoin(url, meta_tw.get('content'))
            else:
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        if not any(icon in src.lower() for icon in ['icon', 'logo', 'avatar', 'sprite']):
                            image_url = urllib.parse.urljoin(url, src)
                            break
                            
        # 2. Try to extract paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        # If we couldn't extract paragraphs, fallback
        if len(text) < 200:
            content = f"This report covers breaking updates regarding '{title}'. While detailed public documentation is currently minimal or restricted, industry experts are closely monitoring the situation as it develops. The implications of this update may significantly impact upcoming sector trends and strategies. Please follow the source link below to stay informed on the original publication."
        else:
            content = text
            
    except Exception as e:
        print(f"Error elaborating {url}: {e}")
        content = f"Recent developments surrounding '{title}' have just surfaced. Current public insights are actively evolving, and professionals are analyzing the potential disruptions this may cause in the broader technological landscape. We will continue to monitor the metrics. You can visit the direct source below for raw updates."
        
    return content, image_url

def download_image(url):
    """Downloads image file safely to a temporary file path."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5, stream=True)
        if r.status_code == 200:
            content_type = r.headers.get('content-type', '')
            if 'image' in content_type:
                ext = '.jpg'
                if 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                    
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                for chunk in r.iter_content(1024):
                    temp_file.write(chunk)
                temp_file.close()
                return temp_file.name
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return None

def process_and_convert_image(raw_img_path):
    """Converts image to standard JPEG padded to fit 800x600 without cropping."""
    default_img = "default_hero.png"
    try:
        if not raw_img_path or not os.path.exists(raw_img_path):
            return default_img
            
        img = Image.open(raw_img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        temp_jpg = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_jpg_name = temp_jpg.name
        temp_jpg.close()
        
        target_width = 800
        target_height = 600
        
        # Resize using thumbnail to maintain aspect ratio without cropping
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Create a new blank image with background color (light slate) to pad it
        new_img = Image.new("RGB", (target_width, target_height), (247, 250, 252))
        
        paste_x = (target_width - img.width) // 2
        paste_y = (target_height - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        new_img.save(temp_jpg_name, 'JPEG', quality=90)
        
        try:
            os.remove(raw_img_path)
        except:
            pass
            
        return temp_jpg_name
    except Exception as e:
        print(f"Error processing image {raw_img_path}: {e}")
        return default_img

def create_cover_page(pdf):
    pdf.add_page()
    # Dark Navy Background
    pdf.set_fill_color(*COLOR_DARK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Neon Green border frame
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.5)
    pdf.rect(10, 10, 190, 277, 'D')
    pdf.set_line_width(0.2)
    
    # Logo SVG
    try:
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=85, y=55, w=40)
    except Exception as e:
        pass
        
    # Brand Name
    pdf.set_y(115)
    pdf.set_font("Montserrat", "B", 32)
    pdf.set_text_color(*COLOR_WHITE)
    pdf.cell(w=0, h=15, text=BRAND_NAME.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Tagline
    pdf.set_y(135)
    pdf.set_font("Montserrat", "", 14)
    pdf.set_text_color(*COLOR_NEON)
    pdf.cell(w=0, h=10, text=TAGLINE, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Divider line
    pdf.set_draw_color(50, 60, 80)
    pdf.line(40, 155, 170, 155)
    
    # Document Title & Date
    pdf.set_y(170)
    pdf.set_font("Merriweather", "", 18)
    pdf.set_text_color(200, 210, 225)
    date_str = datetime.now().strftime("%B %d, %Y")
    pdf.cell(w=0, h=10, text=f"Daily Tech Digest  |  {date_str}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Curated bottom tagline
    pdf.set_y(210)
    pdf.set_font("Montserrat", "", 10)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(w=0, h=8, text="CURATED INSIGHTS FOR THE MODERN TECH LEADER", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Copyright
    pdf.set_y(265)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(w=0, h=10, text=COPYRIGHT, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

def create_toc_page(pdf, stories):
    pdf.add_page()
    # Light Slate Backdrop
    pdf.set_fill_color(*COLOR_LIGHT_GRAY)
    pdf.rect(10, 10, 190, 277, 'F')
    
    # Border
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.0)
    pdf.rect(10, 10, 190, 277, 'D')
    pdf.set_line_width(0.2)
    
    # Header Title
    pdf.set_y(35)
    pdf.set_font("Montserrat", "B", 24)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(w=0, h=15, text="TABLE OF CONTENTS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    
    # Underline decorator
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.5)
    pdf.line(20, pdf.get_y(), 80, pdf.get_y())
    pdf.set_line_width(0.2)
    
    pdf.ln(20)
    
    # Render table of contents entries
    for i, story in enumerate(stories, 1):
        pdf.set_font("Montserrat", "B", 13)
        pdf.set_text_color(*COLOR_DARK)
        pdf.cell(w=10, h=10, text=f"0{i}.", align="L")
        
        pdf.set_font("Montserrat", "", 13)
            
        title = story['title'].encode('ascii', 'ignore').decode('ascii')
        max_title_len = 55
        if len(title) > max_title_len:
            title = title[:max_title_len - 3] + "..."
            
        pdf.cell(w=125, h=10, text=title, align="L")
        
        # Dots divider line
        curr_x = pdf.get_x()
        pdf.set_text_color(*COLOR_GRAY)
        pdf.set_font("Helvetica", "", 12)
        dots_width = 175 - curr_x
        dots_count = int(dots_width / pdf.get_string_width("."))
        pdf.cell(w=dots_width, h=10, text="." * dots_count, align="R")
        
        # Article Page index
        pdf.set_font("Montserrat", "B", 13)
        pdf.set_text_color(*COLOR_NEON)
        pdf.cell(w=15, h=10, text=f"Pg {i+2}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        pdf.ln(5)

def create_article_page(pdf, index, story):
    pdf.add_page()
    epw = pdf.epw
    pdf.set_y(35)
    
    # Title - Merriweather Bold for highly authoritative typography
    pdf.set_font("Merriweather", "B", 17)
    pdf.set_text_color(*COLOR_DARK)
    title_text = f"0{index}. {story['title']}"
    pdf.multi_cell(w=epw, h=8, text=title_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Underline
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y() + 2, 60, pdf.get_y() + 2)
    pdf.set_line_width(0.2)
    pdf.ln(8)
    
    # Fetch, download & format image
    raw_img = None
    extracted_img_url = story.get("image_url")
    if extracted_img_url:
        print(f"Downloading image from {extracted_img_url} for story {index}...")
        raw_img = download_image(extracted_img_url)
        
    processed_img = process_and_convert_image(raw_img)
    
    # Grid Calculation
    col_y_start = pdf.get_y()
    col_w = 80
    col_0_x = 20
    col_1_x = 110
    bottom_limit = 262
    
    # Draw image inside the LEFT COLUMN
    image_height = 60
    try:
        pdf.image(processed_img, x=col_0_x, y=col_y_start, w=col_w, h=image_height)
        if processed_img != "default_hero.png" and os.path.exists(processed_img):
            try:
                os.remove(processed_img)
            except:
                pass
    except Exception as e:
        print(f"Error rendering image: {e}")
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(col_0_x, col_y_start, col_w, image_height, 'F')
        pdf.set_draw_color(*COLOR_GRAY)
        pdf.rect(col_0_x, col_y_start, col_w, image_height, 'D')
        
    body_text = story['content'].encode('ascii', 'ignore').decode('ascii')
    
    # Use Italic Typography as requested
    pdf.set_font("Merriweather", "I", 10.5)
    pdf.set_text_color(45, 55, 72)
    
    line_height = 5.5
    lines = pdf.multi_cell(w=col_w, h=line_height, text=body_text, dry_run=True, output="LINES")
    
    # Start text flow: Left column text starts BELOW the image
    curr_x = col_0_x
    curr_y = col_y_start + image_height + 5
    col_idx = 0
    
    for line in lines:
        if curr_y + line_height > bottom_limit:
            if col_idx == 0:
                col_idx = 1
                curr_x = col_1_x
                curr_y = col_y_start # Right column starts from the VERY TOP of the grid
            else:
                # Truncate text when page limit is reached
                pdf.set_xy(curr_x, curr_y)
                pdf.set_font("Merriweather", "", 9.5)
                pdf.set_text_color(*COLOR_GRAY)
                pdf.cell(w=col_w, h=line_height, text="... [Content truncated. Click below to read more]")
                break
                
        pdf.set_xy(curr_x, curr_y)
        pdf.cell(w=col_w, h=line_height, text=line)
        curr_y += line_height
        
    # Read Full Source link
    pdf.set_y(266)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(w=epw, h=6, text="READ FULL SOURCE ARTICLE ->", link=story['url'], align="R")

def generate_pdf(stories, filename="Daily_Tech_Digest.pdf"):
    print("Generating beautifully formatted PDF...")
    download_fonts()
    
    pdf = PDF()
    
    try:
        pdf.add_font("Montserrat", style="", fname=os.path.join(FONTS_DIR, "Montserrat-Regular.ttf"))
        pdf.add_font("Montserrat", style="B", fname=os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"))
        pdf.add_font("Merriweather", style="", fname=os.path.join(FONTS_DIR, "Merriweather-Regular.ttf"))
        pdf.add_font("Merriweather", style="I", fname=os.path.join(FONTS_DIR, "Merriweather-Italic.ttf"))
        pdf.add_font("Merriweather", style="B", fname=os.path.join(FONTS_DIR, "Merriweather-Bold.ttf"))
    except Exception as e:
        print(f"Error registering fonts: {e}")
        
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=False)
    
    create_cover_page(pdf)
    if stories:
        create_toc_page(pdf, stories)
        for i, story in enumerate(stories, 1):
            create_article_page(pdf, i, story)
    else:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(w=0, h=10, text="No tech news fetched today.", align="C")
        
    pdf.output(filename)
    print(f"Successfully generated {filename}")
    return filename

def send_pdf_to_telegram(filename, bot_token, chat_id):
    print("Sending PDF to Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        with open(filename, "rb") as file:
            files = {"document": file}
            data = {
                "chat_id": chat_id, 
                "caption": f"📰 *{BRAND_NAME}* | Digest for {datetime.now().strftime('%b %d, %Y')}\n\nInnovating the future, today.",
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=data, files=files)
            
        if response.status_code == 200:
            print("Successfully delivered PDF to Telegram!")
            return True
        elif response.status_code == 401:
            print("Failed to send PDF: Telegram Bot Token is Unauthorized (401).")
            print("Please make sure you have created the bot via @BotFather and configured the correct token.")
            return False
        else:
            print(f"Failed to send PDF: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending PDF to Telegram: {e}")
        return False

def main():
    stories = fetch_dynamic_news(5)
    
    date_str = datetime.now().strftime("%d-%m-%Y")
    pdf_filename = f"AoE Tech News({date_str}).pdf"
    
    generate_pdf(stories, pdf_filename)
    
    # Keep standard name file updated for backwards compatibility
    try:
        shutil.copyfile(pdf_filename, "Daily_Tech_Digest.pdf")
        print("Copied output to Daily_Tech_Digest.pdf for backwards compatibility")
    except Exception as e:
        print(f"Error copying file: {e}")
        
    # Read credentials from environment or fallback
    from dotenv import load_dotenv
    load_dotenv()
    
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        BOT_TOKEN = "8658316403:AAH16J5AC2iGmdzM3LyoUS1-zSf4oavzTF4"
    if not CHAT_ID or CHAT_ID == "YOUR_CHAT_ID_HERE":
        CHAT_ID = "6038057345"
        
    success = send_pdf_to_telegram(pdf_filename, BOT_TOKEN, CHAT_ID)
    if not success:
        print("Delivery failed. Check logs.")

if __name__ == "__main__":
    main()
