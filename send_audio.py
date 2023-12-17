"""
Testing script that sends audio of a .wav file to the server via websocket
"""

import asyncio
import websockets
import os
import wave
from sys import argv

async def send_audio_file(websocket, audio_file_path, duration, size):
    try:
        chunk_size = size // duration
        print('Sending', size, 'bytes audio file in', chunk_size, 'byte chunks')
        with open(audio_file_path, 'rb') as audio_file:
            while True:
                # Read a chunk of the audio file, should be about 1sec
                audio_chunk = audio_file.read(chunk_size)

                # Break the loop if the file is fully read
                if not audio_chunk:
                    print("Audio file streaming completed")
                    break
                # Send the audio chunk to the WebSocket server, then sleep
                await websocket.send(audio_chunk)
                await asyncio.sleep(1)


    except websockets.exceptions.ConnectionClosedError:
        print("Connection to the server is closed")

def get_wav_info(file_path):
    # Get the duration of the .wav file
    with wave.open(file_path, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)

    # Get the size of the .wav file in bytes
    file_size = os.path.getsize(file_path)

    return round(duration), file_size

async def main():
    server_url = "ws://localhost:8765"  # Replace with the WebSocket server URL
    audio_file_path = argv[1]
    duration, size = get_wav_info(audio_file_path)
    async with websockets.connect(server_url) as websocket:
        # Send the audio file to the WebSocket server
        await send_audio_file(websocket, audio_file_path, duration, size)

if __name__ == "__main__":
    if len(argv) != 2:
        print(f'Usage: python {argv[0]} /path/to/file.wav')
        exit(1)
    asyncio.get_event_loop().run_until_complete(main())
