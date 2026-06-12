import os
import sys
import asyncio
import logging

# Set up paths to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestUserCancellation")

class MockContext:
    def __init__(self):
        self.bot_data = {
            "active_user_generations": {}
        }

async def test_session_isolation():
    logger.info("Initializing user-specific session cancellation test...")
    context = MockContext()
    
    user_1_chat_id = 111111111
    user_2_chat_id = 222222222
    
    # 1. Start generation for user 1 and user 2
    context.bot_data["active_user_generations"][user_1_chat_id] = False
    context.bot_data["active_user_generations"][user_2_chat_id] = False
    
    # Define callback creators that capture chat_id
    def make_progress_callback(chat_id):
        def progress_callback(phase, progress, detail, mark_done=None):
            if context.bot_data.get("active_user_generations", {}).get(chat_id, False):
                raise RuntimeError(f"Generation cancelled by user {chat_id}.")
            logger.info(f"[Callback User {chat_id}] Phase: {phase} | Progress: {progress}%")
        return progress_callback
        
    cb1 = make_progress_callback(user_1_chat_id)
    cb2 = make_progress_callback(user_2_chat_id)
    
    # Test normal callback execution
    logger.info("Verifying normal execution for both users...")
    cb1("Finding Stories", 10, "Detail 1")
    cb2("Finding Stories", 10, "Detail 2")
    
    # 2. Cancel user 1's generation and verify user 2 remains unaffected
    logger.info("Cancelling generation for user 1 only...")
    context.bot_data["active_user_generations"][user_1_chat_id] = True
    
    # Call user 2's callback: should execute successfully
    logger.info("Calling user 2 callback (should succeed)...")
    cb2("Finding Stories", 20, "Detail 2")
    
    # Call user 1's callback: should raise RuntimeError
    logger.info("Calling user 1 callback (should raise RuntimeError)...")
    try:
        cb1("Finding Stories", 20, "Detail 1")
        raise AssertionError("Expected RuntimeError for user 1 was not raised!")
    except RuntimeError as e:
        logger.info(f"Successfully caught cancellation exception: {e}")
        assert str(user_1_chat_id) in str(e)
        
    logger.info("Session isolation and cancellation flow verified successfully!")

if __name__ == "__main__":
    asyncio.run(test_session_isolation())
