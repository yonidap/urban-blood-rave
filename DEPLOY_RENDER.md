# Deploy Urban Blood Rave to Render

This repository is ready for a Render Blueprint deployment.

## Render settings

- Service type: Web Service
- Runtime: Python
- Plan: Free
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`
- Required secret: `HOST_KEY`

The included `render.yaml` defines all of the above and asks for `HOST_KEY` during initial Blueprint setup.

## After deploy

If Render gives you `https://urban-blood-rave.onrender.com`:

- Main screen: `https://urban-blood-rave.onrender.com/screen`
- Host: `https://urban-blood-rave.onrender.com/host?key=YOUR_HOST_KEY`
- Player links are shown in the Host page and automatically use the public Render origin.

## Keep-awake behavior

The browser clients send a WebSocket `ping` every 25 seconds. The server answers `pong`. This provides inbound WebSocket traffic while the game is open, in addition to the existing HTTP state polling.

## State note

Game state is in server memory. A Render process restart/redeploy resets the current game. Do not deploy new commits during a live game.
