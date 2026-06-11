import os
import logging
import shutil
import re
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

# Premium Dark Palette (Black, Purple, White)
BRAND_ACCENT = (113, 27, 209)  # Deep Purple
BLACK = (10, 10, 10)           # Main Background
WHITE = (255, 255, 255)        # Primary Text
DARK_GREY = (25, 25, 25)       # Card Background (Dark Mode)
MID_GREY = (50, 50, 50)        # Borders
LIGHT_GREY = (180, 180, 180)   # Secondary Text (Dark Mode)
CARD_BG_LIGHT = (245, 245, 245) # Card Background (Light Mode)
TEXT_DARK = (40, 40, 40)       # Secondary Text (Light Mode)

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
    return re.sub(r'^[\d\s\.]+', '', raw_cat).upper()

class CustomPDF(FPDF):
    def __init__(self, date_str: str, custom_topic: str = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.date_str = date_str
        self.custom_topic = custom_topic
        self.set_left_margin(12)
        self.set_right_margin(12)
        self.set_auto_page_break(auto=True, margin=15)
        
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
        # Logo on left
        if os.path.exists("assets/logo.png"):
            self.image("assets/logo.png", 12, 15, w=25)
            
        self.set_font("Montserrat", "B", 9)
        text = "AHEAD OF EVERYONE"
        w = self.get_string_width(text) + 6
        self.set_fill_color(*BRAND_ACCENT)
        self.set_text_color(*WHITE)
        self.set_x(12)
        self.cell(w, 6, text, ln=0, align="C", fill=True)
        
        self.set_font("Montserrat", "B", 8)
        self.set_text_color(*BLACK) # header text on white background
        
        meta_text = f"INTELLIGENCE FEED   |   {self.date_str.upper()}"
        if self.custom_topic:
            meta_text += f"   |   TOPIC: {self.custom_topic.upper()}"
            
        self.set_y(14)
        self.cell(0, 4, meta_text, ln=1, align="R")
        
        self.set_draw_color(*BRAND_ACCENT)
        self.line(12, 22, 198, 22)
        self.ln(10)

    def footer(self):
        if self.page_no() == 1 or getattr(self, 'suppress_footer', False):
            return
            
        self.set_y(-20)
        self.set_font("Montserrat", "B", 8)
        self.set_text_color(*MID_GREY)
        footer_text = "Ahead of Everyone"
        self.set_x(12)
        self.cell(100, 10, footer_text, ln=0, align="L")
        
        self.set_font("Montserrat", "B", 10)
        self.set_text_color(*BRAND_ACCENT)
        page_num = str(self.page_no()).zfill(2) # Started from 1 (the actual page no)
        self.cell(0, 10, page_num, ln=0, align="R")

def draw_cover_page(pdf: CustomPDF, top_story: dict, custom_topic: str = None):
    pdf.add_page()
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Large Vertical Purple Accent
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(6, 0, 4, 297, 'F')
    
    # Title
    pdf.set_y(40)
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 42)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 15, "AHEAD OF", ln=1)
    pdf.set_x(12)
    pdf.cell(0, 15, "EVERYONE", ln=1)
    
    # Date & Subtitle
    pdf.set_y(75)
    pdf.set_x(12)
    # Increased font size +2 for highlighted blocks
    pdf.set_font("Montserrat", "B", 14)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    date_text = pdf.date_str.upper()
    w = pdf.get_string_width(date_text) + 8
    pdf.cell(w, 10, date_text, ln=1, align="C", fill=True)
    
    pdf.set_x(12)
    pdf.set_font("Montserrat", "", 10)
    pdf.set_text_color(*LIGHT_GREY)
    if custom_topic:
        pdf.cell(0, 8, f"ON-DEMAND TACTICAL BRIEFING: {custom_topic.upper()}", ln=1)
    else:
        pdf.cell(0, 8, "DAILY AUTONOMOUS TECH INTELLIGENCE", ln=1)
        
    # Featured Block Outline
    pdf.set_y(120)
    pdf.set_draw_color(*MID_GREY)
    pdf.rect(12, 120, 186, 100, 'D')
    
    # Featured Tag
    pdf.set_xy(12, 115)
    pdf.set_font("Montserrat", "B", 11) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "01 . THE APEX"
    w = pdf.get_string_width(text) + 12
    pdf.cell(w, 10, text, align="C", ln=1, fill=True)
    
    # Featured Headline
    pdf.set_y(135)
    pdf.set_x(22)
    pdf.set_font("Montserrat", "B", 22)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(166, 9, top_story.get("headline", "Featured News"), align="L")
    
    # Brief
    pdf.set_y(pdf.get_y() + 10)
    pdf.set_x(22)
    pdf.set_font("Montserrat", "B", 16)
    pdf.set_text_color(*LIGHT_GREY)
    pdf.multi_cell(166, 8, top_story.get("the_brief", ""), align="L")
    
    # Removed curated text from bottom

def draw_toc_page(pdf: CustomPDF, stories: list, custom_topic: str = None):
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(40)
    pdf.set_font("Montserrat", "B", 32)
    pdf.set_text_color(*BLACK)
    if custom_topic:
        pdf.cell(0, 12, f"THE {custom_topic.upper()} RADAR", ln=1)
    else:
        pdf.cell(0, 12, "THE RADAR", ln=1)
        
    pdf.set_y(55)
    pdf.set_font("Montserrat", "B", 12) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "READ IN THIS ORDER TO DOMINATE THE CONVERSATION."
    w = pdf.get_string_width(text) + 8
    pdf.set_x((210 - w) / 2)
    pdf.cell(w, 10, text, align="C", ln=1, fill=True)
    
    # Implement the cascading/zigzag flow for the TOC
    y_ptr = 80
    card_w = 110
    card_h = 35
    
    for idx, story in enumerate(stories):
        if y_ptr > 250:
            pdf.add_page()
            pdf.set_fill_color(*WHITE)
            pdf.rect(0, 0, 210, 297, 'F')
            y_ptr = 40
            
        is_left = (idx % 2 == 0)
        x_pos = 12 if is_left else 88
        
        # Draw Card
        pdf.set_fill_color(*CARD_BG_LIGHT)
        pdf.rect(x_pos, y_ptr, card_w, card_h, 'F')
        
        # Purple Marker
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(x_pos, y_ptr, 2, card_h, 'F')
        
        # Content
        pdf.set_xy(x_pos + 6, y_ptr + 4)
        pdf.set_font("Montserrat", "B", 10) # +2
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.set_text_color(*WHITE)
        cat_text = f"{str(idx + 1).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
        w = pdf.get_string_width(cat_text) + 6
        pdf.cell(w, 7, cat_text, align="C", ln=1, fill=True)
        
        pdf.set_xy(x_pos + 6, y_ptr + 12)
        pdf.set_font("Montserrat", "B", 10)
        pdf.set_text_color(*BLACK)
        headline = story.get("headline", "")
        if len(headline) > 65: headline = headline[:62] + "..."
        pdf.multi_cell(card_w - 10, 5, headline, align="L")
        
        pdf.set_xy(x_pos + 6, y_ptr + 24)
        pdf.set_font("Montserrat", "", 8)
        pdf.set_text_color(*TEXT_DARK)
        brief = story.get("the_brief", "")
        if len(brief) > 100: brief = brief[:97] + "..."
        pdf.multi_cell(card_w - 10, 4, brief, align="L")
        
        y_ptr += card_h + 5

def draw_article_page(pdf: CustomPDF, index: int, story: dict):
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    

    
    pdf.set_y(35)
    pdf.set_font("Montserrat", "B", 11) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    cat_text = f"{str(index).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
    w = pdf.get_string_width(cat_text) + 6
    pdf.cell(w, 8, cat_text, align="C", ln=1, fill=True)
    
    pdf.set_y(47)
    pdf.set_font("Montserrat", "B", 26)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(0, 10, story.get("headline", "News Story"), align="L")
    
    pdf.set_y(pdf.get_y() + 15)
    
    # THE BRIEF Block
    pdf.set_font("Montserrat", "B", 12) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "THE BRIEF"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 8, text, align="C", ln=1, fill=True)
    
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_font("Montserrat", "B", 16)
    pdf.set_text_color(*TEXT_DARK)
    pdf.multi_cell(0, 8, story.get("the_brief", ""), align="L")
    
    pdf.set_y(pdf.get_y() + 15)
    
    # CORE BREAKDOWN Block
    pdf.set_font("Montserrat", "B", 12) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "CORE BREAKDOWN"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 8, text, align="C", ln=1, fill=True)
    pdf.set_y(pdf.get_y() + 6)
    
    bullets = story.get("core_breakdown", [])
    for bullet in bullets:
        if pdf.get_y() > 240:
            pdf.add_page()
            pdf.set_fill_color(*WHITE)
            pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_y(40)
            
        pdf.set_x(20)
        pdf.set_font("Montserrat", "B", 10)
        pdf.set_text_color(*BLACK)
        
        topic = bullet.get("topic", "")
        if topic:
            pdf.cell(pdf.get_string_width(topic + ": "), 6, topic + ": ", ln=0)
            
        pdf.set_font("Montserrat", "B", 15)
        pdf.set_text_color(*TEXT_DARK)
        
        # We can just rely on the right margin instead of calculating width minus topic_w manually
        # Wait, if we use multi_cell(0) with a topic printed first on the line, the multi_cell drops to the next line.
        # We have to keep calculating the exact width for multi_cell so it stays on the same line.
        topic_w = pdf.get_string_width(topic + ": ") if topic else 0
        pdf.multi_cell(186 - topic_w, 8, bullet.get("description", bullet.get("text", "")), align="L")
        pdf.ln(4)
        
    if pdf.get_y() > 220:
        pdf.add_page()
        pdf.set_fill_color(*WHITE)
        pdf.rect(0, 0, 210, 297, 'F')
        pdf.set_y(40)
        
    pdf.set_y(pdf.get_y() + 15)
    
    # THE EDGE Solid Block
    wy = pdf.get_y()
    pdf.set_fill_color(*CARD_BG_LIGHT)
    pdf.rect(12, wy, 186, 30, 'F')
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(12, wy, 2, 30, 'F')
    
    pdf.set_xy(18, wy + 5)
    pdf.set_font("Montserrat", "B", 10) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "THE EDGE"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 7, text, align="C", ln=1, fill=True)
    
    pdf.set_xy(18, wy + 14)
    pdf.set_font("Montserrat", "B", 16)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(174, 8, story.get("the_edge", ""), align="L")

def draw_custom_toc_page(pdf: CustomPDF, stories: list, custom_topic: str):
    pdf.suppress_header = False
    pdf.suppress_footer = False
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(40)
    pdf.set_font("Montserrat", "B", 32)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 12, f"{custom_topic.upper()} RADAR", ln=1)
        
    pdf.set_y(55)
    pdf.set_font("Montserrat", "", 10)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = " TACTICAL BRIEFING DASHBOARD "
    pdf.set_x((210 - pdf.get_string_width(text)) / 2)
    pdf.cell(pdf.get_string_width(text), 8, text, align="C", ln=1, fill=True)
    
    # 2x2 Grid Layout
    card_w = 85
    card_h = 45
    start_y = 80
    
    for idx, story in enumerate(stories):
        if idx >= 4: # Only show up to 4 stories in grid
            break
            
        col = idx % 2
        row = idx // 2
        
        x_pos = 12 if col == 0 else 113
        y_ptr = start_y + (row * (card_h + 10))
        
        # Draw Card
        pdf.set_fill_color(*CARD_BG_LIGHT)
        pdf.rect(x_pos, y_ptr, card_w, card_h, 'F')
        
        # Purple Top Border instead of side marker
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(x_pos, y_ptr, card_w, 2, 'F')
        
        # Content
        pdf.set_xy(x_pos + 4, y_ptr + 5)
        pdf.set_font("Montserrat", "B", 7)
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.set_text_color(*WHITE)
        cat_text = f" {str(idx + 1).zfill(2)} // {clean_category(story.get('category', 'NEWS'))} "
        pdf.cell(pdf.get_string_width(cat_text), 4, cat_text, ln=1, fill=True)
        
        pdf.set_xy(x_pos + 4, y_ptr + 11)
        pdf.set_font("Montserrat", "B", 9)
        pdf.set_text_color(*BLACK)
        headline = story.get("headline", "")
        if len(headline) > 60: headline = headline[:57] + "..."
        pdf.multi_cell(card_w - 8, 4.5, headline, align="L")
        
        pdf.set_xy(x_pos + 4, y_ptr + 25)
        pdf.set_font("Montserrat", "", 7)
        pdf.set_text_color(*TEXT_DARK)
        brief = story.get("the_brief", "")
        if len(brief) > 130: brief = brief[:127] + "..."
        pdf.multi_cell(card_w - 8, 3.5, brief, align="L")

def draw_conclusion_page(pdf: CustomPDF):
    pdf.suppress_header = True
    pdf.add_page()
    pdf.suppress_footer = True
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_y(120)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 15, "YOU ARE AHEAD.", align="C", ln=1)
    
    pdf.set_y(140)
    pdf.set_font("Montserrat", "B", 14) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "MISSION ACCOMPLISHED. SEE YOU TOMORROW."
    w = pdf.get_string_width(text) + 8
    pdf.set_x((210 - w) / 2)
    pdf.cell(w, 10, text, align="C", ln=1, fill=True)

    # Custom Conclusion Footer
    pdf.set_y(270)
    
    # Left text: Sent everyday...
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*LIGHT_GREY)
    pdf.cell(0, 5, "Sent everyday at 10 AM IST", ln=1)
    
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 8)
    w_prefix = pdf.get_string_width("by Sumanth, under ")
    pdf.cell(w_prefix, 6, "by Sumanth, under ", ln=0)
    
    pdf.set_font("Montserrat", "B", 10) # +2
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "AHEAD OF EVERYONE"
    w = pdf.get_string_width(text) + 4
    pdf.cell(w, 6, text, align="C", ln=0, fill=True)
    
    # Right corner: Date (DD/MM/YYYY)
    date_str = datetime.now().strftime("%d/%m/%Y")
    pdf.set_font("Montserrat", "B", 8)
    pdf.set_text_color(*LIGHT_GREY)
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
        # 3. Individual Article Pages (Full-Width Layout - Same as daily digest)
        for idx, story in enumerate(stories):
            draw_article_page(pdf, idx + 1, story)
    else:
        # 2. TOC Page (Cascading Layout)
        draw_toc_page(pdf, stories, custom_topic)
        # 3. Individual Article Pages (Full-Width Layout)
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
