import nodriver as uc
import asyncio
import os
import shutil
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Union, Dict, Any

app = FastAPI()

# --- OPENAI COMPATIBLE MODELS ---
class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]] # Fixed 422 Error

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "Claude Sonnet 4.6"
    thinking: Optional[bool] = True

async def get_perplexity_response(query: str, target_model: str = None) -> str:
    # --- CONCURRENCY SETUP ---
    session_id = str(uuid.uuid4())[:8]
    temp_profile = os.path.abspath(f"pplx_temp_{session_id}")
    master_profile = os.path.abspath("pplx_profile")

    if os.path.exists(master_profile):
        shutil.copytree(master_profile, temp_profile, dirs_exist_ok=True)
    
    print(f"[{session_id}] Launching browser for: {query[:30]}...")
    
    browser = await uc.start(
        headless=False, 
        user_data_dir=temp_profile,
        browser_args=["--restore-last-session", "--disable-infobars"]
    )
    
    try:
        page = await browser.get("https://www.perplexity.ai/")
        await asyncio.sleep(5)
        
        # 1. KILL "RESTORE PAGES" POPUP
        await page.evaluate('''
            const elements = document.querySelectorAll('div, button');
            for (const el of elements) {
                if (el.textContent.includes('Restore') || el.textContent.includes('shut down correctly')) {
                    el.remove();
                }
            }
        ''')

        # 2. MODEL SELECTION (TreeWalker Logic)
        if target_model:
            print(f"[{session_id}] Selecting model: {target_model}")
            open_js = '''
                (function() {
                    const keywords = ['Claude', 'GPT', 'Sonar', 'Gemini', 'Best', 'Pro'];
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while(node = walker.nextNode()) {
                        if (keywords.some(k => node.nodeValue.includes(k))) {
                            let btn = node.parentElement;
                            while(btn && btn.tagName !== 'BUTTON') btn = btn.parentElement;
                            if (btn) {
                                ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                                    btn.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
                                });
                                return true;
                            }
                        }
                    }
                })();
            '''
            await page.evaluate(open_js)
            await asyncio.sleep(1.5)
            
            # DOUBLE CURLY BRACES FIXED HERE
            click_js = f'''
                (function() {{
                    const target = "{target_model}";
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let node;
                    while(node = walker.nextNode()) {{
                        if (node.nodeValue.trim().includes(target)) {{
                            const el = node.parentElement;
                            ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {{
                                el.dispatchEvent(new MouseEvent(evt, {{ bubbles: true, cancelable: true, view: window }}));
                            }});
                            return true;
                        }}
                    }}
                }})();
            '''
            await page.evaluate(click_js)
            await asyncio.sleep(1)

        # 3. LOCATE SEARCH BOX
        search_box = None
        for trigger in ["Type /", "Ask anything", "Type @", "Search"]:
            try:
                search_box = await page.find(trigger)
                if search_box: break
            except: continue

        if not search_box:
            elements = await page.select_all("textarea")
            if elements:
                search_box = elements[-1]

        if not search_box:
            return "Error: Could not find search box."

        await search_box.click()
        await asyncio.sleep(0.5)
        await search_box.send_keys(query)
        await asyncio.sleep(1)
        
        # 4. SUBMIT
        await page.evaluate('''
            const btn = document.querySelector('button[aria-label="Submit"]') || 
                        document.querySelector('button.bg-accentMain');
            if (btn) btn.click();
            else {
                const ta = document.querySelector('textarea');
                ta.dispatchEvent(new KeyboardEvent('keydown', {bubbles: true, key: 'Enter', code: 'Enter', keyCode: 13}));
            }
        ''')

        # 5. WAIT FOR STABILITY
        prev_text = ""
        stable_count = 0
        for _ in range(90):
            await asyncio.sleep(1)
            elements = await page.select_all(".prose, .break-words")
            if not elements: continue
            
            curr_text = elements[-1].text
            if curr_text and curr_text == prev_text:
                stable_count += 1
                if stable_count >= 3: 
                    return curr_text
            else:
                stable_count = 0
            prev_text = curr_text

        return "Error: Generation timed out."

    finally:
        print(f"[{session_id}] Cleaning up session...")
        browser.stop()
        await asyncio.sleep(1)
        shutil.rmtree(temp_profile, ignore_errors=True)

# --- API ENDPOINT ---
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    last_msg = request.messages[-1]
    
    if isinstance(last_msg.content, list):
        user_query = ""
        for block in last_msg.content:
            if block.get("type") == "text":
                user_query += block.get("text", "")
    else:
        user_query = last_msg.content
    
    try:
        content = await get_perplexity_response(user_query, request.model)
        
        return {
            "id": f"pplx-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": 123456789,
            "model": request.model,
            "choices": [{
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
                "index": 0
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)