import os
import logging
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

# Premium Colors
BRAND_ACCENT = (113, 27, 209) # Purple #711bd1
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
LIGHT_GREY = (245, 245, 245)
DARK_GREY = (30, 30, 30)

class CustomPDF(FPDF):
    def __init__(self, date_str: str, issue_num: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.date_str = date_str
        self.issue_num = issue_num
        self.set_auto_page_break(auto=True, margin=15)
        
        # Make sure assets exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        try:
            self.add_font("Montserrat", "", "assets/Montserrat-Regular.ttf")
            self.add_font("Montserrat", "B", "assets/Montserrat-Bold.ttf")
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")

    def header(self):
        # The cover page header and conclusion page are completely custom, so skip auto-header
        if self.page_no() == 1:
            return
            
        self.set_y(15)
        # Highlighted Logo on left
        self.set_font("Montserrat", "B", 9)
        w = self.get_string_width("AHEAD OF EVERYONE")
        self.set_fill_color(*BRAND_ACCENT)
        self.rect(20, 13, w + 4, 6, 'F')
        self.set_xy(22, 14)
        self.set_text_color(*WHITE)
        self.cell(w, 4, "AHEAD OF EVERYONE", ln=0, align="L")
        
        # Issue and date on right
        self.set_font("Montserrat", "B", 8)
        self.set_text_color(*BLACK)
        header_text = f"EDITION {self.issue_num} . {self.date_str.upper()}"
        self.set_y(14)
        self.cell(0, 4, header_text, ln=1, align="R")
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
            
        self.set_y(-20)
        self.set_font("Montserrat", "", 8)
        self.set_text_color(150, 150, 150)
        footer_text = f"Ahead of Everyone . {self.date_str}"
        self.cell(100, 10, footer_text, ln=0, align="L")
        
        self.set_font("Montserrat", "B", 10)
        self.set_text_color(*BLACK)
        page_num = str(self.page_no() - 1).zfill(2)
        self.cell(0, 10, page_num, ln=0, align="R")

def draw_neon_highlight(pdf, text, font_size, x, y):
    pdf.set_font("Montserrat", "B", font_size)
    width = pdf.get_string_width(text) + 4
    height = font_size * 0.4
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(x - 2, y - height + 2, width, height + 4, 'F')
    
def draw_cover_page(pdf: CustomPDF, top_story: dict):
    pdf.add_page()
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Header
    pdf.set_y(20)
    pdf.set_x(20)
    pdf.set_font("Montserrat", "B", 10)
    w = pdf.get_string_width("AHEAD OF EVERYONE")
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(20, 18, w + 6, 8, 'F')
    pdf.set_xy(23, 20)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 5, "AHEAD OF EVERYONE", ln=0)
    
    pdf.set_font("Montserrat", "B", 9)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 5, f"EDITION {pdf.issue_num}", ln=1, align="R")
    
    pdf.set_font("Montserrat", "B", 9)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.set_x(20)
    pdf.cell(0, 5, pdf.date_str.upper(), ln=1, align="R")
    
    pdf.set_draw_color(50, 50, 50)
    pdf.line(20, 35, 190, 35)
    
    # Headline Section
    pdf.set_y(80)
    pdf.set_x(20)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(20, 82, 10, 1, 'F')
    
    pdf.set_x(35)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(0, 5, "FEATURED STORY", ln=1)
    
    pdf.set_y(95)
    pdf.set_x(20)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*WHITE)
    
    headline = top_story.get("headline", "Major Tech News Event")
    highlight = top_story.get("headline_highlight", "")
    
    words = headline.split()
    line = ""
    for word in words:
        if pdf.get_string_width(line + word) > 160:
            pdf.set_x(20)
            pdf.cell(0, 15, line, ln=1)
            line = word + " "
        else:
            line += word + " "
            
    pdf.set_x(20)
    if highlight and highlight in line:
        parts = line.split(highlight)
        pdf.cell(pdf.get_string_width(parts[0]), 15, parts[0], ln=0)
        
        hx = pdf.get_x()
        hy = pdf.get_y()
        draw_neon_highlight(pdf, highlight, 36, hx, hy + 11)
        
        pdf.set_text_color(*WHITE) # Because purple on black is hard to read
        pdf.cell(pdf.get_string_width(highlight), 15, highlight, ln=0)
        
        pdf.set_text_color(*WHITE)
        if len(parts) > 1:
            pdf.cell(pdf.get_string_width(parts[1]), 15, parts[1], ln=1)
        else:
            pdf.ln(15)
    else:
        pdf.cell(0, 15, line, ln=1)
        
    pdf.set_y(pdf.get_y() + 15)
    pdf.set_x(20)
    pdf.set_font("Montserrat", "", 12)
    pdf.set_text_color(200, 200, 200)
    pdf.multi_cell(160, 6, top_story.get("the_brief", ""))
    
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(20)
    pdf.multi_cell(160, 6, "It has been a long 24 hours. Here is the rundown.")
    
    # Footer
    pdf.set_y(-35)
    pdf.set_draw_color(50, 50, 50)
    pdf.line(20, 262, 190, 262)
    
    pdf.set_y(267)
    pdf.set_x(20)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.get_string_width("Empowering your daily "), 5, "Empowering your daily ", ln=0)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(20, 5, "edge.", ln=0)
    
    pdf.set_font("Montserrat", "B", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, "CURATED BY", ln=1, align="R")
    
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 5, "Sumanth", ln=1, align="R")

def draw_toc_page(pdf: CustomPDF, stories: list):
    pdf.add_page()
    pdf.set_y(30)
    
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(20, 30, 35, 7, 'F')
    pdf.set_xy(20, 31)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*WHITE)
    pdf.cell(35, 5, "DAILY PULSE", align="C", ln=1)
    
    pdf.set_y(45)
    pdf.set_font("Montserrat", "B", 32)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 10, "Today's Agenda.", ln=1)
    
    pdf.set_y(60)
    pdf.set_font("Montserrat", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(170, 6, f"{len(stories)} stories from the last 24 hours. Read in this order and you will be ahead of 90% of people by lunch.")
    
    pdf.set_y(80)
    
    for idx, story in enumerate(stories):
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_y(30)
            
        y_start = pdf.get_y()
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, y_start, 190, y_start)
        
        pdf.set_y(y_start + 5)
        pdf.set_fill_color(*BLACK)
        pdf.rect(20, y_start + 8, 15, 15, 'F')
        pdf.set_xy(20, y_start + 12)
        pdf.set_font("Montserrat", "B", 12)
        pdf.set_text_color(*WHITE)
        pdf.cell(15, 6, str(idx + 1).zfill(2), align="C")
        
        pdf.set_xy(45, y_start + 8)
        pdf.set_font("Montserrat", "B", 12)
        pdf.set_text_color(*BLACK)
        pdf.multi_cell(145, 6, story.get("headline", "News Item"))
        
        pdf.set_x(45)
        pdf.set_font("Montserrat", "", 9)
        pdf.set_text_color(100, 100, 100)
        
        desc = story.get("the_brief", "")
        if len(desc) > 80: desc = desc[:80] + "..."
        pdf.multi_cell(145, 5, desc)
        
        pdf.set_y(pdf.get_y() + 8)

def draw_article_page(pdf: CustomPDF, index: int, story: dict):
    pdf.add_page()
    
    pdf.set_y(30)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(20, 30, 2, 6, 'F')
    
    pdf.set_xy(25, 30)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*BLACK)
    cat_text = story.get("category", "TECH . NEWS")
    pdf.cell(0, 6, f"{str(index).zfill(2)} . {cat_text.upper()}", ln=1)
    
    pdf.set_y(42)
    pdf.set_font("Montserrat", "B", 28)
    pdf.set_text_color(*BLACK)
    
    headline = story.get("headline", "News Story")
    highlight = story.get("headline_highlight", "")
    
    words = headline.split()
    line = ""
    for word in words:
        if pdf.get_string_width(line + word) > 160:
            pdf.set_x(20)
            pdf.cell(0, 12, line, ln=1)
            line = word + " "
        else:
            line += word + " "
            
    pdf.set_x(20)
    if highlight and highlight in line:
        parts = line.split(highlight)
        pdf.cell(pdf.get_string_width(parts[0]), 12, parts[0], ln=0)
        
        hx = pdf.get_x()
        hy = pdf.get_y()
        draw_neon_highlight(pdf, highlight, 28, hx, hy + 9)
        
        pdf.set_text_color(*WHITE)
        pdf.cell(pdf.get_string_width(highlight), 12, highlight, ln=0)
        
        pdf.set_text_color(*BLACK)
        if len(parts) > 1:
            pdf.cell(pdf.get_string_width(parts[1]), 12, parts[1], ln=1)
        else:
            pdf.ln(12)
    else:
        pdf.cell(0, 12, line, ln=1)
        
    pdf.set_y(pdf.get_y() + 10)
    start_y = pdf.get_y()
    
    pdf.set_fill_color(*LIGHT_GREY)
    pdf.rect(20, start_y, 170, 40, 'F')
    
    pdf.set_fill_color(*BLACK)
    pdf.rect(25, start_y - 3, 22, 6, 'F')
    pdf.set_xy(25, start_y - 2)
    pdf.set_font("Montserrat", "B", 7)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(22, 4, "THE BRIEF", align="C", ln=1)
    
    pdf.set_xy(25, start_y + 8)
    pdf.set_font("Montserrat", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(160, 6, story.get("the_brief", ""))
    
    pdf.set_y(max(pdf.get_y(), start_y + 40) + 10)
    
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(20, pdf.get_y() + 1, 4, 4, 'F')
    pdf.set_x(28)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 6, "CORE BREAKDOWN", ln=1)
    
    pdf.set_y(pdf.get_y() + 5)
    
    bullets = story.get("core_breakdown", [])
    for bullet in bullets:
        if pdf.get_y() > 220:
            pdf.add_page()
            pdf.set_y(30)
            
        pdf.set_x(20)
        pdf.set_font("Montserrat", "B", 12)
        pdf.cell(10, 6, "—", ln=0)
        
        topic = bullet.get("topic", "")
        if topic:
            pdf.set_font("Montserrat", "B", 10)
            pdf.cell(pdf.get_string_width(topic + ": "), 6, topic + ": ", ln=0)
            
        pdf.set_font("Montserrat", "", 10)
        pdf.multi_cell(0, 6, bullet.get("description", bullet.get("text", "")))
        pdf.ln(4)
        
    if pdf.get_y() > 230:
        pdf.add_page()
        pdf.set_y(30)
        
    pdf.set_y(pdf.get_y() + 10)
    wy = pdf.get_y()
    pdf.set_fill_color(*BLACK)
    pdf.rect(20, wy, 170, 35, 'F')
    
    pdf.set_xy(25, wy + 5)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(0, 6, "THE EDGE", ln=1)
    
    pdf.set_xy(25, wy + 12)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(160, 6, story.get("the_edge", ""))

def draw_conclusion_page(pdf: CustomPDF):
    # This disables header/footer automatically because page_no checks might not work
    # We will just suppress header/footer in the logic or draw over it
    pdf.add_page()
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(100)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 15, "You are now caught up.", align="C", ln=1)
    
    pdf.set_y(120)
    pdf.set_font("Montserrat", "", 14)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 10, "See you tomorrow.", align="C", ln=1)
    
    pdf.set_y(160)
    pdf.set_font("Montserrat", "B", 18)
    w = pdf.get_string_width("AHEAD OF EVERYONE")
    center_x = (210 - w) / 2
    
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(center_x - 4, 158, w + 8, 12, 'F')
    
    pdf.set_xy(center_x, 160)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 8, "AHEAD OF EVERYONE", align="C", ln=1)
    
    pdf.set_y(260)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Curated by Sumanth", align="C", ln=1)

def generate_digest_pdf(stories: list) -> str:
    date_str = datetime.now().strftime("%d %B %Y")
    issue_num = "003"
    
    pdf = CustomPDF(date_str, issue_num)
    
    if not stories:
        return ""
        
    draw_cover_page(pdf, stories[0])
    draw_toc_page(pdf, stories)
    
    for idx, story in enumerate(stories):
        draw_article_page(pdf, idx + 1, story)
        
    draw_conclusion_page(pdf)
        
    file_name = f"AoE Tech News({datetime.now().strftime('%d-%m-%Y')}).pdf"
    pdf.output(file_name)
    return file_name
