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
        if value > max:
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
                # buffer.extend(audio_data)

                # Enough audio data gathered (about 5 sec), time for inference
                # if (len(buffer) > 5 * 16500):
                # print('Buffered', len(buffer), 'bytes. Running inference...')
                tempid = generate('1234567890abcdef', 14) 
                tempfile = f'/tmp/{tempid}.wav'
                with open(tempfile, 'wb') as fp:
                    fp.write(audio_data)
                print('Wrote to tmpfile', tempfile)
                features = feature_extractor.process_file(tempfile)
                predictions = model.predict(features)
                inferences.append(predictions[0])
                print('Predictions so far:', inferences)
                if len(inferences) == 3:
                    winner = majority(inferences)
                    print('Got 3 predictions. Sending back majority:', winner)
                    await websocket.send(f"\{winner: {winner}\}")
                    inferences.clear()



        except websockets.exceptions.ConnectionClosedOK:
                print("Client disconnected")
    return handler

async def init():
    app = web.Application()
    app.router.add_get('/', lambda _ : web.FileResponse('./www/index.html'))
    app.router.add_static('/', './www')


    # app.add_routes([web.static('/', './www', show_index=True)] )
    # app.router.add_get('/', http_handler)
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