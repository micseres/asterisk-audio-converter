from pydub import AudioSegment
from flask import Flask, Response
from flask_cors import CORS
import re
import os
from dotenv import load_dotenv
import urllib.request
import io

dirname = os.path.dirname(__file__)

dotenv_path = os.path.join(dirname, '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv('APP_SECRET_KEY')

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config.from_object(__name__)


def build_url(name):
    reg_exp = re.compile('(^\w+-\w+-\w+-)(\d{4})(\d{2})(\d{2})(.+)')
    abs_url = os.getenv('APP_AUDIO_SERVER_URL')
    matches = re.match(reg_exp, name)
    return abs_url + '/' + matches[2] + '/' + matches[3] + '/' + matches[4] + '/' + name


@app.route("/audio/<string:name>", methods=['GET'])
def audio(name):
    import_buf = io.BytesIO()

    with urllib.request.urlopen(build_url(name)) as url:
        import_buf.write(url.read())

    song = AudioSegment.from_file(import_buf, format="wav")

    export_buf = io.BytesIO()
    song.export(export_buf, format="mp3")

    def generate():
        with export_buf as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)

    return Response(generate(), mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(host=os.getenv('APP_HOST'), port=os.getenv('APP_PORT'), threaded=True)