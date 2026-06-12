import os
import sys
import logging

# Set up paths to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestProgress")

def test_progress_callback():
    logger.info("Starting progress callback test...")
    
    # 1. Import modules to check syntax and import issues
    try:
        import config
        from main import generate_latest_digest, generate_targeted_digest
        from scraper import fetch_dynamic_news, fetch_targeted_news
        from pdf_generator import generate_digest_pdf
        logger.info("Successfully imported all core modules.")
    except Exception as e:
        logger.error(f"Failed to import core modules: {e}", exc_info=True)
        sys.exit(1)

    # 2. Setup mock progress state and callback
    progress_state = {
        "phase": "Finding Stories",
        "progress": 0,
        "detail": "🌐 Initializing test...",
        "done_phases": set()
    }
    
    def mock_progress_callback(phase, progress, detail, mark_done=None):
        progress_state["phase"] = phase
        progress_state["progress"] = progress
        progress_state["detail"] = detail
        if mark_done:
            progress_state["done_phases"].add(mark_done)
        logger.info(f"[CALLBACK] Phase: {phase} | Progress: {progress}% | Detail: {detail} | Done Phases: {progress_state['done_phases']}")

    # 3. Test callback invocation manually
    logger.info("Invoking progress callback manually to test state update...")
    mock_progress_callback("Finding Stories", 10, "Searching Google News...")
    assert progress_state["progress"] == 10
    assert progress_state["phase"] == "Finding Stories"
    
    mock_progress_callback("Writing Summaries", 50, "Generating summaries...", mark_done="Finding Stories")
    assert progress_state["progress"] == 50
    assert "Finding Stories" in progress_state["done_phases"]
    
    logger.info("Callback test passed successfully!")

if __name__ == "__main__":
    test_progress_callback()
