from deepgram import Deepgram
import asyncio
import aiohttp
import time

# Your personal API key
DEEPGRAM_API_KEY = '93801d36c39b63190bcd5e539a7d245da7e0bd78'

# URL for the real-time streaming audio you would like to transcribe
URL = 'http://stream.live.vc.bbcmedia.co.uk/bbc_world_service'
URL1 = 'https://www.youtube.com/user/gatewaytokorea/live'
# Fill in these parameters to adjust the output as you wish!
# See our docs for more info: https://developers.deepgram.com/documentation/
PARAMS = {"punctuate": True,
          "numerals": True,
          "model": "general",
          "language": "en-US",
          "tier": "nova" }

# The number of *seconds* you wish to transcribe the livestream.
# Set this equal to `float(inf)` if you wish to stream forever.
# (Or at least until you wish to cut off the function manually.)
TIME_LIMIT = 30

# Set this variable to `True` if you wish only to
# see the transcribed words, like closed captions.
# Set it to `False` if you wish to see the raw JSON responses.
TRANSCRIPT_ONLY = True

'''
Function object.

Input: JSON data sent by a live transcription instance, which is named
`deepgramLive` in main().

Output: The printed transcript obtained from the JSON object
'''
def print_transcript(json_data):
    try:
      print(json_data['channel']['alternatives'][0]['transcript'])
    except KeyError:
      print()

async def main():
    start = time.time()
    # Initializes the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    # Create a websocket connection to Deepgram
    try:
        deepgramLive = await deepgram.transcription.live(PARAMS)
    except Exception as e:
        print(f'Could not open socket: {e}')
        return

    # Listen for the connection to close
    deepgramLive.registerHandler(deepgramLive.event.CLOSE,
                                 lambda _: print('✅ Transcription complete! Connection closed. ✅'))

    # Listen for any transcripts received from Deepgram & write them to the console
    if TRANSCRIPT_ONLY:
        deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED,
                                  print_transcript)
    else:
        deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, print)

    # Listen for the connection to open and send streaming audio from the URL to Deepgram
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as audio:
            while time.time() - start < TIME_LIMIT:
                data = await audio.content.readany()
                if data:
                    deepgramLive.send(data)
                else:
                    break

    # Indicate that we've finished sending data by sending the customary
    # zero-byte message to the Deepgram streaming endpoint, and wait
    # until we get back the final summary metadata object
    await deepgramLive.finish()

await main()
