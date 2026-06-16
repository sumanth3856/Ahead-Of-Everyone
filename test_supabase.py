import asyncio
import logging
import os
import sys

# Add the current directory to python path if not already
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from storage import upload_pdf_to_supabase

logging.basicConfig(level=logging.INFO)

async def test():
    # Create a dummy pdf
    dummy_file = "test_dummy.pdf"
    with open(dummy_file, "w") as f:
        f.write("%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj")
    
    path = await upload_pdf_to_supabase(dummy_file, "Test Topic")
    if path:
        print(f"SUCCESS! Uploaded to: {path}")
    else:
        print("FAILED to upload.")
    
    if os.path.exists(dummy_file):
        os.remove(dummy_file)

if __name__ == "__main__":
    asyncio.run(test())
