#!/usr/bin/env python3
# coding: utf-8


import asyncio
import os
import http.server
import socketserver
import websockets
import websockets.exceptions
from aiohttp import web
import aiohttp
from nanoid import generate

WS_PORT= 8765
PORT = 3000

# new_data = smile.process_file('./cabbage_10_01.wav')

# new_feature = new_data._append(new_data,ignore_index=True)

# predictions = model.predict(new_feature)

# print(predictions)
def ws_handler(model, feature_extractor):
    async def handler(websocket, path):
        print("Client connected")
        inferences = []
        try:
            while True:
                # Receive audio stream from the WebSocket
                audio_data = await websocket.recv()

                print('Got audio data', len(audio_data), 'bytes. Running inference...')
                # buffer.extend(audio_data)

                # Enough audio data gathered (about 5 sec), time for inference
                # if (len(buffer) > 5 * 16500):
                # print('Buffered', len(buffer), 'bytes. Running inference...')
                tempid = generate('1234567890abcdef', 14) 
                tempfile = f'/tmp/{tempid}.webm'
                with open(tempfile, 'wb') as fp:
                    fp.write(audio_data)
                print('Wrote to tmpfile', tempfile)
                features = feature_extractor.process_file(tempfile)
                predictions = model.predict(features)
                inferences.append(predictions[0])
                print('Predictions so far:', inferences)
                if len(predictions) == 3:
                    print('Sending back predictions')
                    # TODO send back majority vote winner
                    predictions = []



        except websockets.exceptions.ConnectionClosedOK:
                print("Client disconnected")
    return handler

async def http_handler(request):
    path = request.match_info.get('path', '.')
    full_path = os.path.join("./www", path)

    if os.path.isfile(full_path):
        return web.FileResponse(full_path)
    elif os.path.isdir(full_path):
        return web.FileResponse(os.path.join(full_path, 'index.html'))

async def init():
    app = web.Application()
    app.router.add_get('/', http_handler)
    return app

async def main():
    print('Loading model and feature extractor...')
    from joblib import load
    from smile import smile
    model = load('./rf_model.xz')
    print('Loaded model and feature extractor')
    app = await init()
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "localhost", PORT)
    await site.start()
    print(f"HTTP server started at http://localhost:{PORT}")
    await websockets.serve(ws_handler(model, feature_extractor=smile), 'localhost', WS_PORT)
    print(f"WS server started at ws://localhost:{WS_PORT}")

    # Keep the script running

    # Start the WebSocket server
    # start_server = websockets.serve(ws_handler(model, smile), "localhost", WS_PORT)
    # print('WS server running on port', WS_PORT)


    # Run the server until it is manually stopped


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()