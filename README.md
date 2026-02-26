### For the Python + Mistral devs:

![Mistral + Python Examples](/screenshot.png)


- /examples-cli/ai-mistral-text/command.py (most common use case)
- /examples-cli/ai-mistral-embeddings/command.py (for vector database)
- /examples-cli/ai-mistral-image-gen/command.py (image generation)

Usage: 
```
uv init # modern Python package manager https://github.com/astral-sh/uv
uv add mistralai # install sdk for ai-mistral-image-gen
uv run examples-cli/ai-mistral-image-gen/command.py test-data/ai-mistral-image-gen.json
```


### For Python + Mistral + GUI builders:
![Nyno examples connecting multiple AI nodes](https://github.com/flowagi-eu/nyno/raw/main/h/c0f8c2c19f52c63ba139a25e5fa5fbc80a36a865c1368534bac204c3fc3d683f/screenshot-from-2026-01-12-13-26-24.webp)

#### GUI Builder + Engine
- For Windows: [How to run Nyno on Windows using Docker Desktop](https://nyno.dev/how-to-run-nyno-on-windows-using-docker-desktop)
- For Linux: [Nyno Core GUI AI Workflow Builder & Engine](https://github.com/flowagi-eu/nyno)

#### Run Any .nyno File in Python:
```
from nynoclient import NynoClient
client = NynoClient(
    credentials="change_me",
    host="127.0.0.1",
    port=9024,
)

with open('your-nyno-file.nyno','r') as r:
    content = r.read()

result = client.run_nyno(content)
print(result) # { "status": "OK", "execution": [...] }
```
- [Nyno Python Driver (PyPi)](https://github.com/flowagi-eu/nyno-python-driver)
- [Learn to use Powerful Nyno (AI) Workflows build using a GUI in Python!](https://github.com/flowagi-eu/learn-python-nyno-with-examples)

## Add Your Awesome Mistral-Python-Nyno Example:
- [Submit a Post to the Nyno Subreddit](https://reddit.com/r/Nyno)
