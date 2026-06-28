import os
import logging
import shutil
import re
import time
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

# Strict 3-Color Premium Palette
BRAND_ACCENT = (113, 27, 209)  # Deep Purple
BLACK = (0, 0, 0)              # Pure Crisp Black
WHITE = (255, 255, 255)        # Crisp White

# Pre-compiled category cleaning pattern
CAT_CLEAN_RE = re.compile(r'^[\d\s\.]+')

import urllib.request

MONTSERRAT_REG_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Regular.ttf"
MONTSERRAT_BOLD_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf"
MONTSERRAT_ITALIC_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Italic.ttf"

def ensure_font_exists(filename: str, url: str) -> bool:
    font_path = f"assets/{filename}"
    if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
        return True
    if not os.path.exists("assets"):
        os.makedirs("assets")
    try:
        logger.info(f"Attempting to download missing font from: {url}")
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response, open(font_path, 'wb') as out_file:
            out_file.write(response.read())
        logger.info(f"Successfully downloaded font: {filename}")
        return True
    except Exception as e:
        logger.warning(f"Failed to download font {filename} from {url}: {e}")
        if os.path.exists(font_path):
            try:
                os.remove(font_path)
            except Exception:
                pass
    return False

def ensure_logo_exists() -> bool:
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
        return True
    # We purposefully don't try to download from broken URLs anymore.
    # The PDF generator will seamlessly fall back to drawing a vector logo (AoE circle).
    return False

def sanitize_text(text: str) -> str:
    if not isinstance(text, str): return text
    # Strip markdown emphasis characters (e.g. *, _, `, **)
    text = re.sub(r'\*\*+(.*?)\*\*+', r'\1', text)
    text = re.sub(r'\*+(.*?)\*+', r'\1', text)
    text = re.sub(r'__+(.*?)__+', r'\1', text)
    text = re.sub(r'_+(.*?)_+', r'\1', text)
    text = re.sub(r'`+(.*?)`+', r'\1', text)
    
    replacements = {
        '\u2011': '-', '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00a0': ' ',
        '\u200b': '',
        '\u00a9': '(c)', '\u00ae': '(R)', '\u2122': 'TM',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    try:
        text.encode('latin-1')
    except UnicodeEncodeError:
        text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text



def balance_quotes(text: str) -> str:
    """Balances double and single quotes in a string, especially after truncation."""
    # Count occurrences of double quotes
    double_quotes = text.count('"') + text.count('“') + text.count('”')
    if double_quotes % 2 != 0:
        if text.endswith("..."):
            text = text[:-3] + '"...'
        else:
            text = text + '"'
            
    # Count occurrences of single quotes
    single_quotes = text.count("'") + text.count('‘') + text.count('’')
    if single_quotes % 2 != 0:
        if text.endswith("..."):
            text = text[:-3] + "'..."
        else:
            text = text + "'"
    return text

def clean_category(raw_cat: str) -> str:
    """Removes leading numbers and dots from the AI category."""
    return CAT_CLEAN_RE.sub('', raw_cat).upper()

def truncate_to_word_boundary(text: str, limit: int) -> str:
    """Truncates text to a maximum of limit characters, ending on a word boundary and balancing quotes."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return balance_quotes(text)
    slice_limit = limit - 3
    sub_text = text[:slice_limit]
    last_space = sub_text.rfind(' ')
    if last_space != -1:
        truncated = sub_text[:last_space].rstrip(".,;:!- ") + "..."
    else:
        truncated = sub_text + "..."
    return balance_quotes(truncated)

def sanitize_stories(stories: list) -> list:
    """Recursively sanitizes all text fields in a list of story dictionaries for PDF safety."""
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
    return sanitized_stories

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
            
        ensure_font_exists("Montserrat-Regular.ttf", MONTSERRAT_REG_URL)
        ensure_font_exists("Montserrat-Bold.ttf", MONTSERRAT_BOLD_URL)
        ensure_font_exists("Montserrat-Italic.ttf", MONTSERRAT_ITALIC_URL)
        
        try:
            self.add_font("Montserrat", "", "assets/Montserrat-Regular.ttf")
            self.add_font("Montserrat", "B", "assets/Montserrat-Bold.ttf")
            self.add_font("Montserrat", "I", "assets/Montserrat-Italic.ttf")
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

    def multi_cell(self, w, h=None, txt="", *args, **kwargs):
        # Extract text/txt safely to prevent TypeError when fpdf2 calls this recursively
        text = kwargs.pop('text', txt)
        
        old_l_margin = self.l_margin
        current_x = self.x
        if current_x != old_l_margin:
            self.set_left_margin(current_x)
        
        val = super().multi_cell(w, h, text, *args, **kwargs)
        
        if current_x != old_l_margin:
            self.set_left_margin(old_l_margin)
        return val

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
            
        # Draw logo in top right corner
        logo_path = "assets/logo.png"
        logo_w = 8
        logo_h = 8
        try:
            if os.path.exists(logo_path):
                self.image(logo_path, x=198 - logo_w, y=8, w=logo_w, h=logo_h)
        except Exception as e:
            logger.warning(f"Failed to draw header logo: {e}")
            
        self.cell(0, 4, meta_text, ln=1, align="L")
        
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

def draw_text(pdf, text, font="Montserrat", style="", size=10, color=BLACK, x=None, y=None, align="L", w=0, h=6, bg=None, multi=False):
    if y is not None: pdf.set_y(y)
    if x is not None: pdf.set_x(x)
    pdf.set_font(font, style, size)
    pdf.set_text_color(*color)
    if bg:
        pdf.set_fill_color(*bg)
        if multi:
            pdf.multi_cell(w, h, text, align=align, fill=True)
        else:
            pdf.cell(w, h, text, align=align, ln=1, fill=True)
    else:
        if multi:
            pdf.multi_cell(w, h, text, align=align)
        else:
            pdf.cell(w, h, text, align=align, ln=1)

def draw_labeled_badge(pdf, text: str, x: int, y: int, font_size: float = 9, bg_color: tuple = BRAND_ACCENT, text_color: tuple = WHITE):
    pdf.set_xy(x, y)
    pdf.set_font("Montserrat", "B", font_size)
    pdf.set_text_color(*text_color)
    pdf.set_fill_color(*bg_color)
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 5.5, text, align="C", ln=1, fill=True)

def draw_headline_with_highlight(pdf, headline, highlight_word, font_size, line_height=10, default_color=WHITE, highlight_bg=BRAND_ACCENT, highlight_fg=WHITE):
    pdf.set_font("Montserrat", "B", font_size)
    words = headline.split(" ")
    
    # Clean highlight word for matching
    clean_hl = highlight_word.lower().strip(".,;:!?\"'") if highlight_word else ""
    
    for i, word in enumerate(words):
        # Clean current word for comparison
        clean_word = word.lower().strip(".,;:!?\"'")
        is_highlight = False
        if clean_hl and clean_hl in clean_word:
            is_highlight = True
            
        space = " " if i < len(words) - 1 else ""
        word_to_draw = word + space
        w = pdf.get_string_width(word_to_draw)
        
        # Check if word fits on current line
        right_boundary = 210 - pdf.r_margin
        if pdf.x + w > right_boundary:
            pdf.ln(line_height)
            pdf.set_x(pdf.l_margin)
            
        if is_highlight:
            # Draw highlight rectangle
            box_h = font_size * 0.35 + 2
            box_y = pdf.y + (line_height - box_h) / 2
            pdf.set_fill_color(*highlight_bg)
            pdf.rect(pdf.x - 1, box_y, w + 1, box_h, 'F')
            
            pdf.set_text_color(*highlight_fg)
            pdf.write(line_height, word_to_draw)
        else:
            pdf.set_text_color(*default_color)
            pdf.write(line_height, word_to_draw)

def draw_cover_page(pdf: CustomPDF, top_story: dict, custom_topic: str = None):
    pdf.add_page()
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # No gradient, solid black background
    
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
    has_logo = False
    try:
        if ensure_logo_exists():
            # A4 width is 210. Centered x for 25mm width is (210-25)/2 = 92.5
            pdf.image(logo_path, x=92.5, y=20, w=25, h=25)
            has_logo = True
    except Exception as e:
        logger.warning(f"Failed to draw logo image: {e}")
        
    if not has_logo:
        # Fallback: Draw stylized vector placeholder (purple circle with 'AoE' text)
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.ellipse(95, 22.5, 20, 20, 'F')
        pdf.set_text_color(*WHITE)
        # Use Montserrat or fall back to helvetica
        current_font = "Montserrat" if not getattr(pdf, 'use_fallback_fonts', False) else "helvetica"
        pdf.set_font(current_font, "B", 10)
        pdf.set_xy(95, 22.5)
        pdf.cell(20, 20, "AoE", align="C")
        
    # Title - Centered, massive
    draw_text(pdf, "AHEAD OF", style="B", size=52, color=WHITE, y=50, align="C", h=18)
    draw_text(pdf, "EVERYONE", style="B", size=52, color=BRAND_ACCENT, align="C", h=18)
    
    # Tagline - Centered
    tagline = f"CURATED INTELLIGENCE BRIEFING: {custom_topic.upper()}" if custom_topic else "CURATING TOMORROW\'S INNOVATIONS, TODAY."
    pdf.set_y(90)
    pdf.set_font("Montserrat", "", 12)
    w = pdf.get_string_width(tagline) + 8
    pdf.set_x((210 - w) / 2)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 8, tagline, align="C", ln=1, fill=True)
    
    # Vertical Stripe (Anchor for Feature Block)
    # x=12, w=5, starting from y=130 down to the bottom margin
    wy = 130
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(12, wy, 5, 297 - wy - 12, 'F')
    
    # Featured Content
    pdf.set_y(wy + 10)
    pdf.set_x(30) # Leaves 12mm margin + 5mm stripe + 13mm gap = 30
    pdf.set_font("Montserrat", "B", 11)
    apex_text = " 01 . THE APEX "
    w = pdf.get_string_width(apex_text)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 8, apex_text, align="C", ln=1, fill=True)
    
    # Set margins for the column
    old_l_margin = pdf.l_margin
    old_r_margin = pdf.r_margin
    pdf.set_left_margin(30)
    pdf.set_right_margin(15)
    pdf.set_xy(30, pdf.get_y() + 2)
    
    draw_headline_with_highlight(
        pdf=pdf, 
        headline=top_story.get("headline", "Featured News"), 
        highlight_word=top_story.get("headline_highlight", ""), 
        font_size=24, 
        line_height=10, 
        default_color=WHITE, 
        highlight_bg=BRAND_ACCENT, 
        highlight_fg=WHITE
    )
    pdf.ln(10)
    
    # Restore margins
    pdf.set_left_margin(old_l_margin)
    pdf.set_right_margin(old_r_margin)
    
    draw_text(pdf, top_story.get("the_brief", ""), size=13, color=WHITE, x=30, y=pdf.get_y() + 2, w=165, h=7, multi=True)

def draw_toc_page(pdf: CustomPDF, stories: list, custom_topic: str = None, synthesis: dict = None):
    pdf.suppress_header = True
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.suppress_header = False
    pdf.header()
    
    pdf.set_y(25)
    pdf.set_font("Montserrat", "B", 36)
    pdf.set_text_color(*BLACK)
    if custom_topic:
        pdf.multi_cell(186, 15, f"THE {custom_topic.upper()} RADAR", align="L")
    else:
        pdf.multi_cell(186, 15, "THE RADAR", align="L")
        
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(0, 6, "ONE PATTERN. TOLD FIVE DIFFERENT WAYS.", align="L", ln=1)
    
    pdf.set_y(pdf.get_y() + 1)
    pdf.set_font("Montserrat", "", 11)
    pdf.set_text_color(*BLACK)
    intro_text = "The last 24 hours were not a list of unrelated stories. Read in sequence, they are one shift, told in five voices."
    pdf.multi_cell(186, 6, intro_text, align="L")
    
    pdf.ln(3)
    sy = pdf.get_y()
    pdf.set_fill_color(245, 245, 245)
    
    if not synthesis:
        synthesis = {
            "meta_theme": "The cost of intelligence is collapsing, the locus of control is shifting, and the moat is moving from models to compute, sovereignty, and energy.",
            "takeaway": "Stop building on a single model. Build the workflow that lets you swap any model in. The cost wall is collapsing. Your moat is the system around the model, not the model itself."
        }
    meta_theme = synthesis.get("meta_theme", "")
    box_text = f"This is not five stories. This is the same story told five times. {meta_theme}"
    
    pdf.set_font("Montserrat", "B", 11)
    lines = pdf.multi_cell(176, 5.5, box_text, split_only=True)
    box_h = len(lines) * 5.5 + 8
    
    pdf.rect(12, sy, 186, box_h, 'F')
    pdf.set_xy(17, sy + 4)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(176, 5.5, box_text, align="L")
    
    y_ptr = sy + box_h + 6
    
    for idx, story in enumerate(stories):
        pdf.set_xy(12, y_ptr)
        pdf.set_fill_color(*BRAND_ACCENT)
        pdf.rect(12, y_ptr + 1, 1.5, 4.5, 'F')
        
        pdf.set_xy(16, y_ptr)
        pdf.set_font("Montserrat", "B", 11)
        pdf.set_text_color(*BLACK)
        headline = story.get("headline", "")
        hl_text = f"{str(idx + 1).zfill(2)}  {headline}"
        pdf.multi_cell(182, 6, hl_text, align="L")
        
        pdf.set_x(16)
        pdf.set_font("Montserrat", "", 10)
        pdf.set_text_color(100, 100, 100)
        brief = story.get("the_brief", "")
        brief = truncate_to_word_boundary(brief, 120)
        pdf.multi_cell(182, 5, brief, align="L")
        
        y_ptr = pdf.get_y() + 3
        
    takeaway_text = synthesis.get("takeaway", "")
    pdf.set_font("Montserrat", "B", 10.5)
    t_lines = pdf.multi_cell(176, 5.5, takeaway_text, split_only=True)
    takeaway_box_h = len(t_lines) * 5.5 + 15
    
    takeaway_y = 270 - takeaway_box_h
    if takeaway_y < y_ptr + 4:
        takeaway_y = y_ptr + 4
        
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(12, takeaway_y, 186, takeaway_box_h, 'F')
    
    draw_labeled_badge(pdf, "IF YOU TAKE ONE THING FROM THIS", 17, takeaway_y + 4, 8.5)
    pdf.set_xy(17, takeaway_y + 10)
    pdf.set_font("Montserrat", "B", 10.5)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(176, 5.5, takeaway_text, align="L")

def draw_article_page(pdf: CustomPDF, index: int, story: dict):
    pdf.suppress_header = True
    pdf.add_page()
    pdf.set_fill_color(*WHITE)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.suppress_header = False
    pdf.header()
    
    # Purple indicator stripe
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(12, 20.5, 1.5, 5, 'F')
    
    # Category Indicator
    pdf.set_y(20)
    pdf.set_x(15)  # Moved left to start next to the purple indicator
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*BRAND_ACCENT)
    cat_text = f"{str(index).zfill(2)} . {clean_category(story.get('category', 'NEWS'))}"
    pdf.cell(0, 6, cat_text, align="L", ln=1)
    
    # Headline
    pdf.set_y(30)
    pdf.set_font("Montserrat", "B", 28)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(0, 11, story.get("headline", "News Story"), align="L")
    
    pdf.set_y(pdf.get_y() + 8)
    
    # THE BRIEF - Shaded Gray Box
    brief_text = story.get("the_brief", "")
    pdf.set_font("Montserrat", "", 10.5)
    lines = pdf.multi_cell(176, 5.5, brief_text, split_only=True)
    box_h = 4 + 6 + 2 + len(lines) * 5.5 + 4
    
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(12, pdf.get_y(), 186, box_h, 'F')
    
    pdf.set_xy(16, pdf.get_y() + 4)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Montserrat", "B", 8)
    pdf.cell(24, 5.5, "QUICK TAKE", align="C", ln=1, fill=True)
    
    pdf.set_xy(16, pdf.get_y() + 2)
    pdf.set_font("Montserrat", "", 10.5)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(176, 5.5, brief_text, align="L")
    
    pdf.set_y(pdf.get_y() + box_h - (4 + 6 + 2 + len(lines) * 5.5) + 6)
    
    # WHAT YOU NEED TO KNOW header
    pdf.set_x(24)
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    text = "WHAT YOU NEED TO KNOW"
    w = pdf.get_string_width(text) + 6
    pdf.cell(w, 7, text, align="C", ln=1, fill=True)
    pdf.set_y(pdf.get_y() + 4)
    
    # Render structured bullets
    core_breakdown = story.get("core_breakdown", [])
    if not isinstance(core_breakdown, list):
        core_breakdown = [{"tag": "The detail", "detail": str(core_breakdown)}]
        
    for item in core_breakdown:
        tag = item.get("tag", "").strip()
        detail = item.get("detail", "").strip()
        
        old_l_margin = pdf.l_margin
        pdf.set_left_margin(30)
        
        pdf.set_xy(24, pdf.get_y())
        pdf.set_font("Montserrat", "B", 11)
        pdf.set_text_color(*BLACK)
        pdf.cell(6, 6.5, "—", ln=0)
        
        pdf.set_x(30)
        pdf.set_font("Montserrat", "B", 11)
        pdf.write(6.5, f"{tag}: ")
        
        pdf.set_font("Montserrat", "", 11)
        pdf.write(6.5, detail)
        pdf.ln(8)
        
        pdf.set_left_margin(old_l_margin)
        
    if pdf.get_y() > 220:
        pdf.add_page()
        pdf.set_y(20)
        
    pdf.set_y(pdf.get_y() + 4)
    
    # THE EDGE (Solid Black Box)
    edge_text = f"\"{story.get('the_edge', '')}\""
    pdf.set_font("Montserrat", "B", 12)
    lines = pdf.multi_cell(176, 6.5, edge_text, split_only=True)
    box_h = len(lines) * 6.5 + 15
    
    if pdf.get_y() + box_h > 275:
        pdf.add_page()
        wy = pdf.get_y()
    else:
        wy = pdf.get_y()
        
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(12, wy, 186, box_h, 'F')
    
    draw_labeled_badge(pdf, "THE EDGE", 17, wy + 4, 9, (245, 245, 245), BLACK)
    pdf.set_xy(17, wy + 10)
    pdf.set_font("Montserrat", "B", 12)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(176, 6.5, edge_text, align="L")
    
    pdf.set_y(wy + box_h + 4)
    
    # T H E   D E E P   D I V E
    wy = pdf.get_y()
    leftover_height = 275 - wy
    
    if leftover_height < 15:
        return
        
    raw_deep_dive = story.get('deep_dive', story.get('the_deep_dive', ''))
    
    # Draw DEEP DIVE heading
    draw_labeled_badge(pdf, "DEEP DIVE", 16, wy, 9)
    # Draw DEEP DIVE text below heading
    wy_text = wy + 6
    leftover_height_text = 275 - wy_text
    max_lines = int(leftover_height_text / 6.5)
    max_chars = max_lines * 105
    
    if len(raw_deep_dive) > max_chars:
        raw_deep_dive = raw_deep_dive[:max_chars - 3] + "..."
        
    pdf.set_xy(16, wy_text)
    pdf.set_font("Montserrat", "I", 10)
    pdf.set_text_color(*BLACK)
    pdf.set_fill_color(248, 248, 250)
    pdf.multi_cell(176, 6.5, raw_deep_dive, align="J", fill=True)

def draw_custom_toc_page(pdf: CustomPDF, stories: list, custom_topic: str, synthesis: dict = None):
    draw_toc_page(pdf, stories, custom_topic, synthesis)

def draw_conclusion_page(pdf: CustomPDF):
    pdf.suppress_header = True
    pdf.add_page()
    pdf.suppress_footer = True
    pdf.set_fill_color(*BLACK)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # No gradient, solid black background
    
    pdf.set_y(120)
    pdf.set_font("Montserrat", "B", 42)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 15, "YOU ARE AHEAD.", align="C", ln=1)
    
    pdf.set_y(145)
    pdf.set_font("Montserrat", "B", 12)
    text = "MISSION ACCOMPLISHED. SEE YOU TOMORROW."
    w = pdf.get_string_width(text) + 8
    pdf.set_x((210 - w) / 2)
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.set_text_color(*WHITE)
    pdf.cell(w, 10, text, align="C", ln=1, fill=True)

    # Custom Conclusion Footer
    pdf.set_y(275)
    pdf.set_x(12)
    pdf.set_font("Montserrat", "B", 12)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, "AHEAD OF EVERYONE", align="L", ln=0)
    
    # Right corner: Date (e.g. 15 JUNE 2026)
    date_str = pdf.date_str.upper()
    pdf.set_font("Montserrat", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, date_str, align="R", ln=1)

def generate_digest_pdf(stories: list, custom_topic: str = None, progress_callback=None, synthesis: dict = None) -> str:
    """Generates a premium Dark/Light Mode multi-page PDF."""
    date_str = datetime.now().strftime("%d %B %Y")
    
    pdf = CustomPDF(date_str, custom_topic)
    
    start_time = time.time()
    logger.info(f"[PDF] Starting generation. Custom topic: {custom_topic}, Stories: {len(stories)}")
    
    if not stories:
        logger.error("[PDF] No stories provided for PDF generation.")
        return ""
        
    stories = sanitize_stories(stories)
    
    # Use alias for page numbers
    pdf.alias_nb_pages()
    
    # 1. Cover Page
    if progress_callback:
        progress_callback("Creating PDF", 70, "Initiating PDF generation and rendering cover page...")
    draw_cover_page(pdf, stories[0], custom_topic)
    
    if custom_topic:
        # 2. TOC Page (Grid Layout)
        if progress_callback:
            progress_callback("Creating PDF", 75, "Rendering table of contents (Grid Layout)...")
        draw_custom_toc_page(pdf, stories, custom_topic, synthesis)
        # 3. Individual Article Pages
        for idx, story in enumerate(stories):
            if progress_callback:
                progress = 75 + int((idx / len(stories)) * 13)
                progress_callback("Creating PDF", progress, f"Rendering article {idx + 1} page ({story.get('title', 'Untitled')[:20]}...)...")
            draw_article_page(pdf, idx + 1, story)
    else:
        # 2. TOC Page (Cascading/List Layout)
        if progress_callback:
            progress_callback("Creating PDF", 75, "Rendering table of contents (List Layout)...")
        draw_toc_page(pdf, stories, custom_topic, synthesis)
        # 3. Individual Article Pages
        for idx, story in enumerate(stories):
            if progress_callback:
                progress = 75 + int((idx / len(stories)) * 13)
                progress_callback("Creating PDF", progress, f"Rendering article {idx + 1} page ({story.get('title', 'Untitled')[:20]}...)...")
            draw_article_page(pdf, idx + 1, story)
            
    # 4. Conclusion Page
    if progress_callback:
        progress_callback("Creating PDF", 88, "Drawing concluding thoughts page...")
    draw_conclusion_page(pdf)
    
    if custom_topic:
        file_name = f"AoE_{custom_topic.replace(' ', '_')}_({datetime.now().strftime('%d-%m-%Y')}).pdf"
    else:
        file_name = f"AoE_Tech_News_({datetime.now().strftime('%d-%m-%Y')}).pdf"
        
    try:
        if progress_callback:
            progress_callback("Creating PDF", 90, "Saving document to local storage...", mark_done="Creating PDF")
        pdf.output(file_name)
        shutil.copyfile(file_name, "Daily_Tech_Digest.pdf")
        elapsed = time.time() - start_time
        logger.info(f"[PDF] Successfully generated dynamic multi-page PDF: {file_name} in {elapsed:.1f}s")
    except Exception as e:
        logger.error(f"[PDF] Error producing PDF: {e}")
        return ""
        
    return file_name
