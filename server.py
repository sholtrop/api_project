#!/usr/bin/env python3
# coding: utf-8

import asyncio
import websockets
import websockets.exceptions
from aiohttp import web
import aiohttp
from nanoid import generate

WS_PORT= 8765
PORT = 3000

def majority(list):
    tally = {}
    for item in list:
        tally.setdefault(item, 0)
        tally[item] += 1
    max = 0
    max_key = None
    for key, value in tally.items():
        if value >= max:
            max = value
            max_key = key
    return max_key


def ws_handler(model, feature_extractor):
    async def handler(websocket, path):
        print("Client connected")
        inferences = []
        try:
            while True:
                # Receive audio stream from the WebSocket
                audio_data = await websocket.recv()

                print('Got audio data', len(audio_data), 'bytes. Running inference...')
                tempid = generate('1234567890abcdef', 14) 
                tempfile = f'/tmp/{tempid}.wav'
                with open(tempfile, 'wb') as fp:
                    fp.write(audio_data)
                print('Wrote to tmpfile', tempfile)
                features = feature_extractor.process_file(tempfile)
                predictions = model.predict(features)
                inferences.append(predictions[0])
                print('Predictions so far:', inferences)
                if len(inferences) == 4:
                    winner = None
                    # Correct model bias
                    if 'chips' in inferences:
                        winner = 'chips'
                    else:
                        winner = majority(inferences)
                    print('winner', winner)
                    await websocket.send(f"winner: {winner}")
                    inferences.pop(0)

        except websockets.exceptions.ConnectionClosedOK:
                print("Client disconnected")
    return handler

async def init():
    app = web.Application()
    app.router.add_get('/', lambda _ : web.FileResponse('./docs/index.html'))
    app.router.add_static('/', './docs')
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


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()