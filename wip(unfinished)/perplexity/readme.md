[this is a bit shit rn cuz i havent converted to full headless yet]
also could probably run as a permanent browser rather than reopening every time to save latency.

Sets up a proxy via uvicorn which serves perplexity requests in openai format

how does it work?

-uses your login to log into perplexity, and save a session

-then runs the prompt, outputs it via perplexity format

NOTE:  This runs with a head, so it'll open a browser every time. you can try running it headless but have found issues with that so far , so i recommend putting it on a server or another pc in your network and then running it from there

USAGE:

install python dependencies

pip install nodriver fastapi uvicorn pydantic

install chromium for nodriver
choco install chromium -y

-run login.py to create a chrome session
-run browserproxy.py

-setup in openclaude under custom with localurl http://localhost:8000/
-apikey sk-bla

