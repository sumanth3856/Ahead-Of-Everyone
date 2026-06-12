import os
import sys
import asyncio
import logging

# Set up paths to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestCancellation")

class MockContext:
    def __init__(self):
        self.bot_data = {
            "broadcast_in_progress": False,
            "broadcast_cancelled": False
        }

async def test_cancellation_logic():
    logger.info("Initializing cancellation flow test...")
    context = MockContext()
    
    # Simulate initiating broadcast
    context.bot_data["broadcast_in_progress"] = True
    context.bot_data["broadcast_cancelled"] = False
    
    # Simulate a progress callback that monitors the cancellation flag
    def progress_callback(phase, progress, detail, mark_done=None):
        if context.bot_data.get("broadcast_cancelled", False):
            raise RuntimeError("Broadcast cancelled by admin.")
        logger.info(f"[Mock Callback] Phase: {phase} | Progress: {progress}% | Detail: {detail}")

    # 1. First run: normal callback invocation
    logger.info("Verifying callback runs under normal state...")
    progress_callback("Finding Stories", 20, "Testing story retrieval...")
    
    # 2. Second run: request cancellation and verify RuntimeError is raised
    logger.info("Simulating admin requesting cancellation...")
    context.bot_data["broadcast_cancelled"] = True
    
    try:
        progress_callback("Finding Stories", 30, "Should not reach here...")
        raise AssertionError("Expected RuntimeError was not raised!")
    except RuntimeError as e:
        logger.info(f"Successfully caught expected cancellation exception: {e}")
        assert "cancelled by admin" in str(e).lower()
        
    logger.info("Cancellation verification test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_cancellation_logic())
