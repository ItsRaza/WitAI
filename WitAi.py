

# from Recorder import record_audio, read_audio
from flask_ngrok import run_with_ngrok
from flask import Flask
from wit import Wit
import json
import requests
import pyaudio
import wave
from flask import jsonify
# Wit speech API endpoint
API_ENDPOINT = 'https://api.wit.ai/speech'
app = Flask(__name__)
run_with_ngrok(app)

# Wit.ai api access token
wit_access_token = 'CKRSJL2VOMUPBHXXFFOKOD63JSLR3ORZ'


def record_audio(RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
    #--------- SETTING PARAMS FOR OUR AUDIO FILE ------------#
    FORMAT = pyaudio.paInt16    # format of wave
    CHANNELS = 2                # no. of audio channels
    RATE = 44100                # frame rate
    CHUNK = 1024                # frames per audio sample
    #--------------------------------------------------------#

    # creating PyAudio object
    audio = pyaudio.PyAudio()

    # open a new stream for microphone
    # It creates a PortAudio Stream Wrapper class object
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    #----------------- start of recording -------------------#
    print("Listening...")

    # list to save all audio frames
    frames = []

    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        # read audio stream from microphone
        data = stream.read(CHUNK)
        # append audio data to frames list
        frames.append(data)

    #------------------ end of recording --------------------#
    print("Finished recording.")

    stream.stop_stream()    # stop the stream object
    stream.close()          # close the stream object
    audio.terminate()       # terminate PortAudio

    #------------------ saving audio ------------------------#

    # create wave file object
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')

    # settings for wave file object
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))

    # closing the wave file object
    waveFile.close()


def read_audio(WAVE_FILENAME):
    # function to read audio(wav) file
    with open(WAVE_FILENAME, 'rb') as f:
        audio = f.read()
    return audio


def RecognizeSpeech(AUDIO_FILENAME, num_seconds=5):

    # record audio of specified length in specified audio file
    # record_audio(num_seconds, AUDIO_FILENAME)

    # reading audio
    audio = read_audio(AUDIO_FILENAME)

    # defining headers for HTTP request
    headers = {'authorization': 'Bearer ' + wit_access_token,
               'Content-Type': 'audio/wav'}

    # making an HTTP post request
    resp = requests.post(API_ENDPOINT, headers=headers,
                         data=audio)

    # converting response content to JSON format
    data = json.loads(resp.content)

    print(data)
    # get text from data
    text = data['text']

    # return the text
    return text


@app.route("/<text>")
def home(text=None):
    client = Wit(wit_access_token)
    # text = "Hello world"
    resp = client.get_message(text)

    print(type(resp))
    return jsonify(resp)


app.run()
