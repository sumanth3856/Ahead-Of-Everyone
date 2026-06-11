import os
import logging
import shutil
import re
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

# Strict 3-Color Premium Palette
BRAND_ACCENT = (113, 27, 209)  # Deep Purple
BLACK = (10, 10, 10)           # Pitch Black
WHITE = (255, 255, 255)        # Crisp White

# Pre-compiled category cleaning pattern
CAT_CLEAN_RE = re.compile(r'^[\d\s\.]+')

def sanitize_text(text: str) -> str:
    if not isinstance(text, str): return text
    replacements = {
        '\u2011': '-', '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00a0': ' ',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def clean_category(raw_cat: str) -> str:
    """Removes leading numbers and dots from the AI category."""
    return CAT_CLEAN_RE.sub('', raw_cat).upper()

class CustomPDF(FPDF):
    def __init__(self, date_str: str, custom_topic: str = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.date_str = date_str
        self.custom_topic = custom_topic
        # Uniform 12mm margins everywhere
        self.set_left_margin(12)
        self.set_right_margin(12)
        self.set_top_margin(12)
        self.set_auto_page_break(auto=True, margin=12)
        
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        try:
            self.add_font("Montserrat", "", "assets/Montserrat-Regular.ttf")
            self.add_font("Montserrat", "B", "assets/Montserrat-Bold.ttf")
            self.use_fallback_fonts = False
        except Exception as e:
            logger.error(f"Error loading fonts, falling back to built-in fonts: {e}")
            self.use_fallback_fonts = True

    def set_font(self, family, style="", size=0):
        if getattr(self, 'use_fallback_fonts', False):
            family = "helvetica"
        try:
            super().set_font(family, style, size)
        except RuntimeError:
            self.use_fallback_fonts = True
            super().set_font("helvetica", style, size)

    def header(self):
        if self.page_no() == 1 or getattr(self, 'suppress_header', False):
            return
            
        # Minimalist Header
        self.set_y(12)
        self.set_font("Montserrat", "B", 8)
        self.set_text_color(*BLACK)
        
        meta_text = f"INTELLIGENCE FEED   |   {self.date_str.upper()}"
        if self.custom_topic:
            meta_text += f"   |   TOPIC: {self.custom_topic.upper()}"
            
        self.cell(0, 4, meta_text, ln=1, align="R")
        
        # Hairline
        self.set_draw_color(*BLACK)
        self.set_line_width(0.2)
        self.line(12, 18, 198, 18)
        self.ln(8)

    def footer(self):
        if self.page_no() == 1 or getattr(self, 'suppress_footer', False):
            return
            
        self.set_y(-16)
        self.set_font("Montserrat", "B", 8)
        self.set_text_color(*BLACK)
        self.set_x(12)
        self.cell(100, 10, "AHEAD OF EVERYONE", ln=0, align="L")
        
        self.set_font("Montserrat", "B", 10)
        self.set_text_color(*BRAND_ACCENT)
        page_num = str(self.page_no()).zfill(2)
        self.cell(0, 10, page_num, ln=0, align="R")

def draw_cover_page(pdf: CustomPDF, top_story: dict, custom_topic: str = None):
    pdf.add_page()
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Highlighted Date at Top Right
    pdf.set_y(12)
    date_text = f" {pdf.date_str.upper()} "
    pdf.set_font("Montserrat", "B", 10)
    w = pdf.get_string_width(date_text) + 16
    pdf.set_x(210 - 12 - w)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 8, date_text, align="C", ln=1, fill=True)
    
    # Logo
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        # A4 width is 210. Centered x for 25mm width is (210-25)/2 = 92.5
        pdf.image(logo_path, x=92.5, y=20, w=25, h=25)
        
    # Title - Centered, massive
    pdf.set_y(50)
    pdf.set_font("Montserrat", "B", 52)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 18, "AHEAD OF", align="C", ln=1)
    pdf.cell(0, 18, "EVERYONE", align="C", ln=1)
    
    # Tagline - Centered
    pdf.set_y(90)
    pdf.set_font("Montserrat", "", 12)
    pdf.set_text_color(*WHITE)
    if custom_topic:
        tagline = f"ON-DEMAND TACTICAL BRIEFING: {custom_topic.upper()}"
    else:
        tagline = "DAILY AUTONOMOUS TECH INTELLIGENCE"
    pdf.cell(0, 8, tagline, align="C", ln=1)
    
    # Vertical Stripe (Anchor for Feature Block)
    # x=12, w=5, starting from y=130 down to the bottom margin
    wy = 130
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(12, wy, 5, 297 - wy - 12, 'F')
    
    # Featured Content
    pdf.set_y(wy + 10)
    pdf.set_x(24) # Leaves 12mm margin + 5mm stripe + 7mm gap = 24
    pdf.set_font("Montserrat", "B", 11)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(0, 10, "01 . THE APEX", align="L", ln=1)
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_x(24)
    pdf.set_font("Montserrat", "B", 24)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(160, 10, top_story.get("headline", "Featured News"), align="L")
    
    pdf.set_y(pdf.get_y() + 8)
    pdf.set_x(24)
    pdf.set_font("Montserrat", "", 13) # Increased font weight simulation
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(160, 7, top_story.get("the_brief", ""), align="L")

def draw_toc_page(pdf: CustomPDF, stories: list, custom_topic: str = None):
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(25)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*BLACK)
    if custom_topic:
        pdf.cell(0, 15, f"THE {custom_topic.upper()} RADAR", ln=1)
    else:
        pdf.cell(0, 15, "THE RADAR", ln=1)
        
    pdf.set_y(45)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*BRAND_ACCENT)
    text = "READ IN THIS ORDER TO DOMINATE THE CONVERSATION."
    pdf.cell(0, 6, text, align="L", ln=1)
    
    # Elegant list layout - dynamically condensed to guarantee single page
    y_ptr = 60
    
    for idx, story in enumerate(stories):
        pdf.set_xy(12, y_ptr)
        
        # Purple indicator stripe
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(12, y_ptr + 0.5, 1.5, 5, 'F')
        
        # Indicator
        pdf.set_xy(16, y_ptr)
        pdf.set_font("Montserrat", "B", 12)
        pdf.set_text_color(*BRAND_ACCENT)
        cat_text = f"{str(idx + 1).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
        pdf.cell(0, 6, cat_text, align="L", ln=1)
        
        # Headline
        pdf.set_xy(12, y_ptr + 8)
        pdf.set_font("Montserrat", "B", 14)
        pdf.set_text_color(*BLACK)
        headline = story.get("headline", "")
        if len(headline) > 90: headline = headline[:87] + "..."
        pdf.multi_cell(186, 6, headline, align="L")
        
        # Brief
        pdf.set_xy(12, pdf.get_y() + 2)
        pdf.set_font("Montserrat", "", 12) # Simulating weight with size
        pdf.set_text_color(*BLACK)
        brief = story.get("the_brief", "")
        # Hard truncate to ensure it fits (max ~130 chars for TOC)
        if len(brief) > 130: brief = brief[:127] + "..."
        pdf.multi_cell(186, 5.5, brief, align="L")
        
        y_ptr = pdf.get_y() + 6
        
        # Hairline separator
        pdf.set_draw_color(*BLACK)
        pdf.set_line_width(0.1)
        pdf.line(12, y_ptr, 198, y_ptr)
        y_ptr += 6

def draw_article_page(pdf: CustomPDF, index: int, story: dict):
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Purple indicator stripe
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(12, 20.5, 1.5, 5, 'F')
    
    # Category Indicator
    pdf.set_y(20)
    pdf.set_x(16)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*BRAND_ACCENT)
    cat_text = f"{str(index).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
    pdf.cell(0, 6, cat_text, align="L", ln=1)
    
    # Headline
    pdf.set_y(30)
    pdf.set_font("Montserrat", "B", 28)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(0, 11, story.get("headline", "News Story"), align="L")
    
    pdf.set_y(pdf.get_y() + 15)
    
    # THE BRIEF
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "THE BRIEF"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 7, text, align="C", ln=1, fill=True)
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Montserrat", "", 13) # Using 13pt Regular for "thicker" feel
    pdf.set_text_color(*BLACK)
    # Asymmetric indent for body text
    pdf.set_x(24)
    pdf.multi_cell(174, 7.5, story.get("the_brief", ""), align="L")
    
    pdf.set_y(pdf.get_y() + 15)
    
    # CORE BREAKDOWN
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "CORE BREAKDOWN"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 7, text, align="C", ln=1, fill=True)
    pdf.set_y(pdf.get_y() + 4)
    
    bullets = story.get("core_breakdown", [])
    for bullet in bullets:
        if pdf.get_y() > 240:
            pdf.add_page()
            pdf.set_y(20)
            
        pdf.set_x(24) # Indented bullet
        
        topic = bullet.get("topic", "")
        # Draw small purple square for bullet
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(24, pdf.get_y() + 2.5, 2, 2, 'F')
        
        pdf.set_x(30)
        desc = bullet.get("description", bullet.get("text", ""))
        
        # Inline bolding using write()
        old_l_margin = pdf.l_margin
        pdf.set_left_margin(30)
        pdf.set_x(30)
        
        if topic:
            pdf.set_font("Montserrat", "B", 13)
            pdf.set_text_color(*BLACK)
            pdf.write(7.5, f"{topic.upper()}: ")
            
        pdf.set_font("Montserrat", "", 13)
        pdf.set_text_color(*BLACK)
        pdf.write(7.5, f"{desc}\n\n")
        
        pdf.set_left_margin(old_l_margin)
        
    if pdf.get_y() > 220:
        pdf.add_page()
        pdf.set_y(20)
        
    pdf.set_y(pdf.get_y() + 10)
    
    # T H E   E D G E (Pull-Quote Style)
    wy = pdf.get_y()
    pdf.set_fill_color(*BRAND_ACCENT)
    # Thick bold purple line on the left
    pdf.rect(12, wy, 2, 35, 'F')
    
    pdf.set_xy(18, wy + 2)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "THE EDGE"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 7, text, align="C", ln=1, fill=True)
    
    pdf.set_xy(18, wy + 10)
    pdf.set_font("Montserrat", "B", 16)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(180, 8, f"\"{story.get('the_edge', '')}\"", align="L")

def draw_custom_toc_page(pdf: CustomPDF, stories: list, custom_topic: str):
    pdf.suppress_header = False
    pdf.suppress_footer = False
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(25)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 15, f"{custom_topic.upper()} RADAR", ln=1)
        
    pdf.set_y(45)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*BRAND_ACCENT)
    text = "TACTICAL BRIEFING DASHBOARD"
    pdf.cell(0, 6, text, align="L", ln=1)
    
    # 2x2 Grid Layout with pure typography
    col_w = 90
    start_y = 65
    
    for idx, story in enumerate(stories):
        if idx >= 4:
            break
            
        col = idx % 2
        row = idx // 2
        
        x_pos = 12 if col == 0 else 110
        y_ptr = start_y + (row * 80) # 80mm height per block
        
        # Purple Hairline Top Border
        pdf.set_draw_color(*BRAND_ACCENT)
        pdf.set_line_width(0.5)
        pdf.line(x_pos, y_ptr, x_pos + col_w, y_ptr)
        
        # Purple indicator stripe
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(x_pos, y_ptr + 4.5, 1.5, 4, 'F')
        
        # Content
        pdf.set_xy(x_pos + 4, y_ptr + 4)
        pdf.set_font("Montserrat", "B", 9)
        pdf.set_text_color(*BRAND_ACCENT)
        cat_text = f"{str(idx + 1).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
        pdf.cell(col_w - 4, 5, cat_text, ln=1)
        
        pdf.set_xy(x_pos, y_ptr + 10)
        pdf.set_font("Montserrat", "B", 12)
        pdf.set_text_color(*BLACK)
        headline = story.get("headline", "")
        if len(headline) > 65: headline = headline[:62] + "..."
        pdf.multi_cell(col_w, 5, headline, align="L")
        
        pdf.set_xy(x_pos, pdf.get_y() + 3)
        pdf.set_font("Montserrat", "", 10)
        pdf.set_text_color(*BLACK)
        brief = story.get("the_brief", "")
        if len(brief) > 130: brief = brief[:127] + "..."
        pdf.multi_cell(col_w, 5, brief, align="L")

def draw_conclusion_page(pdf: CustomPDF):
    pdf.suppress_header = True
    pdf.add_page()
    pdf.suppress_footer = True
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(120)
    pdf.set_font("Montserrat", "B", 42)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 15, "YOU ARE AHEAD.", align="C", ln=1)
    
    pdf.set_y(145)
    pdf.set_font("Montserrat", "B", 12)
    pdf.set_text_color(*BRAND_ACCENT)
    text = "MISSION ACCOMPLISHED. SEE YOU TOMORROW."
    pdf.cell(0, 10, text, align="C", ln=1)

    # Custom Conclusion Footer
    pdf.set_y(270)
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 12)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, "AHEAD OF EVERYONE", align="L", ln=0)
    
    # Right corner: Date (DD/MM/YYYY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, date_str, align="R", ln=1)

def generate_digest_pdf(stories: list, custom_topic: str = None) -> str:
    """Generates a premium Dark/Light Mode multi-page PDF."""
    date_str = datetime.now().strftime("%d %B %Y")
    
    pdf = CustomPDF(date_str, custom_topic)
    
    if not stories:
        logger.error("No stories provided for PDF generation.")
        return ""
        
    sanitized_stories = []
    for story in stories:
        sanitized = {}
        for k, v in story.items():
            if isinstance(v, str):
                sanitized[k] = sanitize_text(v)
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    if isinstance(item, dict):
                        new_list.append({ik: sanitize_text(iv) if isinstance(iv, str) else iv for ik, iv in item.items()})
                    elif isinstance(item, str):
                        new_list.append(sanitize_text(item))
                    else:
                        new_list.append(item)
                sanitized[k] = new_list
            else:
                sanitized[k] = v
        sanitized_stories.append(sanitized)
        
    stories = sanitized_stories
    
    # Use alias for page numbers
    pdf.alias_nb_pages()
    
    # 1. Cover Page
    draw_cover_page(pdf, stories[0], custom_topic)
    
    if custom_topic:
        # 2. TOC Page (Grid Layout)
        draw_custom_toc_page(pdf, stories, custom_topic)
        # 3. Individual Article Pages
        for idx, story in enumerate(stories):
            draw_article_page(pdf, idx + 1, story)
    else:
        # 2. TOC Page (Cascading/List Layout)
        draw_toc_page(pdf, stories, custom_topic)
        # 3. Individual Article Pages
        for idx, story in enumerate(stories):
            draw_article_page(pdf, idx + 1, story)
            
    # 4. Conclusion Page
    draw_conclusion_page(pdf)
    
    if custom_topic:
        file_name = f"AoE_{custom_topic.replace(' ', '_')}_({datetime.now().strftime('%d-%m-%Y')}).pdf"
    else:
        file_name = f"AoE_Tech_News_({datetime.now().strftime('%d-%m-%Y')}).pdf"
        
    try:
        pdf.output(file_name)
        shutil.copyfile(file_name, "Daily_Tech_Digest.pdf")
        logger.info(f"Successfully generated dynamic multi-page PDF: {file_name}")
    except Exception as e:
        logger.error(f"Error producing PDF: {e}")
        return ""
        
    return file_name
