import nodriver as uc
import asyncio
import os

# Force Windows to use an absolute, full file path
PROFILE_DIR = os.path.abspath(os.path.join(os.getcwd(), "pplx_profile"))

async def main():
    print(f"Launching persistent browser profile at:\n{PROFILE_DIR}")
    
    # Pass the absolute path into nodriver
    browser = await uc.start(headless=False, user_data_dir=PROFILE_DIR)
    
    page = await browser.get("https://www.perplexity.ai/")
    
    print("\n" + "="*50)
    print("ACTION REQUIRED: Please log into Perplexity.")
    print("You have 3 minutes to complete the login.")
    print("="*50 + "\n")
    
    await asyncio.sleep(180)
    
    print("Time's up! Saving your session cookies and closing...")
    browser.stop()

if __name__ == "__main__":
    asyncio.run(main())