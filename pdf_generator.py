import os
import logging
import requests
from datetime import datetime
from typing import List, Dict
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from config import (
    BRAND_NAME, TAGLINE, COPYRIGHT, COLOR_DARK, COLOR_GRAY, COLOR_LIGHT_GRAY,
    COLOR_NEON, COLOR_WHITE, LOGO_PATH, FONTS_DIR
)
from scraper import download_image, process_and_convert_image

logger = logging.getLogger(__name__)

def download_fonts() -> None:
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
            logger.info(f"Downloading font: {filename}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                logger.info(f"Successfully downloaded {filename}")
            except Exception as e:
                logger.error(f"Error downloading font {filename}: {e}")

class CustomPDF(FPDF):
    def header(self):
        if self.page_no() > 2:
            self.set_fill_color(*COLOR_DARK)
            self.rect(0, 0, 210, 25, 'F')
            try:
                if os.path.exists(LOGO_PATH):
                    self.image(LOGO_PATH, x=20, y=5, w=15)
            except Exception:
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
            self.set_draw_color(*COLOR_NEON)
            self.set_line_width(0.5)
            self.line(20, 25, 190, 25)
            self.set_line_width(0.2)

    def footer(self):
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

def create_cover_page(pdf: CustomPDF) -> None:
    pdf.add_page()
    pdf.set_fill_color(*COLOR_DARK)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.5)
    pdf.rect(10, 10, 190, 277, 'D')
    pdf.set_line_width(0.2)
    try:
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=85, y=55, w=40)
    except Exception:
        pass
    pdf.set_y(115)
    pdf.set_font("Montserrat", "B", 32)
    pdf.set_text_color(*COLOR_WHITE)
    pdf.cell(w=0, h=15, text=BRAND_NAME.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_y(135)
    pdf.set_font("Montserrat", "", 14)
    pdf.set_text_color(*COLOR_NEON)
    pdf.cell(w=0, h=10, text=TAGLINE, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_draw_color(50, 60, 80)
    pdf.line(40, 155, 170, 155)
    pdf.set_y(170)
    pdf.set_font("Merriweather", "", 18)
    pdf.set_text_color(200, 210, 225)
    date_str = datetime.now().strftime("%B %d, %Y")
    pdf.cell(w=0, h=10, text=f"Daily Tech Digest  |  {date_str}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_y(210)
    pdf.set_font("Montserrat", "", 10)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(w=0, h=8, text="CURATED INSIGHTS FOR THE MODERN TECH LEADER", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_y(265)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(w=0, h=10, text=COPYRIGHT, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

def create_toc_page(pdf: CustomPDF, stories: List[Dict]) -> None:
    pdf.add_page()
    pdf.set_fill_color(*COLOR_LIGHT_GRAY)
    pdf.rect(10, 10, 190, 277, 'F')
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.0)
    pdf.rect(10, 10, 190, 277, 'D')
    pdf.set_line_width(0.2)
    pdf.set_y(35)
    pdf.set_font("Montserrat", "B", 24)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(w=0, h=15, text="TABLE OF CONTENTS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(1.5)
    pdf.line(20, pdf.get_y(), 80, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(20)
    
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
        curr_x = pdf.get_x()
        pdf.set_text_color(*COLOR_GRAY)
        pdf.set_font("Helvetica", "", 12)
        dots_width = 175 - curr_x
        dots_count = int(dots_width / pdf.get_string_width("."))
        pdf.cell(w=dots_width, h=10, text="." * dots_count, align="R")
        pdf.set_font("Montserrat", "B", 13)
        pdf.set_text_color(*COLOR_NEON)
        pdf.cell(w=15, h=10, text=f"Pg {i+2}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        pdf.ln(5)

def create_article_page(pdf: CustomPDF, index: int, story: Dict) -> None:
    pdf.add_page()
    epw = pdf.epw
    pdf.set_y(35)
    pdf.set_font("Merriweather", "B", 17)
    pdf.set_text_color(*COLOR_DARK)
    title_text = f"0{index}. {story['title']}"
    pdf.multi_cell(w=epw, h=8, text=title_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*COLOR_NEON)
    pdf.set_line_width(0.8)
    pdf.line(20, pdf.get_y() + 2, 60, pdf.get_y() + 2)
    pdf.set_line_width(0.2)
    pdf.ln(8)
    
    raw_img = None
    extracted_img_url = story.get("image_url")
    if extracted_img_url:
        logger.info(f"Downloading image from {extracted_img_url} for story {index}...")
        raw_img = download_image(extracted_img_url)
        
    processed_img = process_and_convert_image(raw_img)
    
    col_y_start = pdf.get_y()
    col_w = 80
    col_0_x = 20
    col_1_x = 110
    bottom_limit = 262
    
    image_height = 60
    try:
        pdf.image(processed_img, x=col_0_x, y=col_y_start, w=col_w, h=image_height)
        if processed_img != "default_hero.png" and os.path.exists(processed_img):
            try:
                os.remove(processed_img)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error rendering image: {e}")
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(col_0_x, col_y_start, col_w, image_height, 'F')
        pdf.set_draw_color(*COLOR_GRAY)
        pdf.rect(col_0_x, col_y_start, col_w, image_height, 'D')
        
    body_text = story['content'].encode('ascii', 'ignore').decode('ascii')
    
    pdf.set_font("Merriweather", "I", 10.5)
    pdf.set_text_color(45, 55, 72)
    line_height = 5.5
    lines = pdf.multi_cell(w=col_w, h=line_height, text=body_text, dry_run=True, output="LINES")
    
    left_col_lines = int((bottom_limit - (col_y_start + image_height + 5)) / line_height)
    right_col_lines = int((bottom_limit - col_y_start) / line_height)
    
    # Reconstruct text blocks to allow fpdf2 to natively justify them
    left_text = " ".join([line.strip() for line in lines[:left_col_lines]])
    right_text = " ".join([line.strip() for line in lines[left_col_lines : left_col_lines + right_col_lines]])
    
    # Render Left Column
    pdf.set_xy(col_0_x, col_y_start + image_height + 5)
    pdf.multi_cell(w=col_w, h=line_height, text=left_text, align="J")
    
    # Render Right Column
    pdf.set_xy(col_1_x, col_y_start)
    if len(lines) > left_col_lines + right_col_lines:
        right_text += " ... [Click below to read more]"
        
    pdf.multi_cell(w=col_w, h=line_height, text=right_text, align="J")
        
    pdf.set_y(266)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(w=epw, h=6, text="READ FULL SOURCE ARTICLE ->", link=story['url'], align="R")

def generate_pdf(stories: List[Dict], filename: str = "Daily_Tech_Digest.pdf") -> str:
    logger.info("Generating beautifully formatted PDF...")
    download_fonts()
    pdf = CustomPDF()
    
    try:
        pdf.add_font("Montserrat", style="", fname=os.path.join(FONTS_DIR, "Montserrat-Regular.ttf"))
        pdf.add_font("Montserrat", style="B", fname=os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"))
        pdf.add_font("Merriweather", style="", fname=os.path.join(FONTS_DIR, "Merriweather-Regular.ttf"))
        pdf.add_font("Merriweather", style="I", fname=os.path.join(FONTS_DIR, "Merriweather-Italic.ttf"))
        pdf.add_font("Merriweather", style="B", fname=os.path.join(FONTS_DIR, "Merriweather-Bold.ttf"))
    except Exception as e:
        logger.error(f"Error registering fonts: {e}")
        
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
    logger.info(f"Successfully generated {filename}")
    return filename
