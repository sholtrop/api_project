import asyncio
from aiohttp import web
import websockets
import os

async def handle(request):
    path = request.match_info.get('path', '.')
    full_path = os.path.join(directory_to_serve, path)

    if os.path.isfile(full_path):
        return web.FileResponse(full_path)
    elif os.path.isdir(full_path):
        return web.FileResponse(os.path.join(full_path, 'index.html'))

async def websocket_handler(request):
    ws = websockets.websockets(request)
    async with ws:
        while True:
            message = await ws.recv()
            print(f"Received message: {message}")
            await ws.send_str(f"Server received: {message}")

async def init():
    app = web.Application()

    # Static file serving
    app.router.add_get('/{path:.*}', handle)

    # WebSocket handling
    app.router.add_get('/websocket', websocket_handler)

    return app

# Specify the directory you want to serve
directory_to_serve = '/path/to/your/directory'

# Set the port number
http_port = 8000
websocket_port = 8765

# Start the combined server
async def main():
    app = await init()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", http_port)
    await site.start()

    print(f"HTTP server started at http://localhost:{http_port}")
    print(f"WebSocket server started at ws://localhost:{websocket_port}")

    # Keep the script running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
