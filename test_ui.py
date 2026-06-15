import sys
import fitz
from pdf_generator import CustomPDF, draw_article_page, draw_toc_page, draw_cover_page, draw_conclusion_page

def generate_mock_ui():
    pdf = CustomPDF("15-06-2026")
    
    # 1. Mock Article Data
    story = {
        "category": "TECH",
        "headline": "A Dummy Headline for Testing UI Centering",
        "the_brief": "This is a brief to fill space.",
        "core_breakdown": [{"tag": "Detail", "detail": "Test detail"}],
        "the_edge": "This edge is super sharp.",
        "deep_dive": "This deep dive goes very deep into the ocean of text."
    }
    
    # 2. Mock Cover
    draw_cover_page(pdf, story, "TEST TOPIC")
    
    # 3. Draw Article
    draw_article_page(pdf, 1, story)
    
    # 4. Mock TOC
    stories = [story]
    synthesis = {
        "meta_theme": "Test theme",
        "takeaway": "Always write good code and test it well."
    }
    draw_toc_page(pdf, stories, "TEST TOPIC", synthesis)
    
    # 4. Mock Conclusion
    draw_conclusion_page(pdf)
    
    pdf_path = "mock_test.pdf"
    pdf.output(pdf_path)
    
    # Convert to images
    doc = fitz.open(pdf_path)
    
    for i, name in enumerate(["cover", "article", "toc", "conclusion"]):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        img_path = f"C:/Users/hp/.gemini/antigravity/brain/adc0e1e6-00b7-44ff-b8e3-b8ea4fe5723b/{name}_page_ui_fix_v9.png"
        pix.save(img_path)
    
    print("Images saved successfully.")

if __name__ == "__main__":
    generate_mock_ui()
