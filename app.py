from flask import Flask, render_template, Response, request
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
from vidgear.gears import CamGear

app = Flask(__name__)

stream = CamGear(source='https://www.youtube.com/watch?v=ZO5lV0gh5i4', stream_mode=True, logging=True).start() # default video

def process_stream():
    count = 0
    while True:
        frame = stream.read()
        count += 1
        if count % 6 != 0:
            continue

        frame = cv2.resize(frame, (1020, 600))
        bbox, label, conf = cv.detect_common_objects(frame)
        frame = draw_bbox(frame, bbox, label, conf)
        c = label.count('person')
        cv2.putText(frame, str(c), (50, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_video', methods=['POST'])
def set_video():
    global stream
    video_url = request.form['video_url']
    if video_url:
        stream.stop()
        stream = CamGear(source=video_url, stream_mode=True, logging=True).start()
    return '', 204

@app.route('/video_feed')
def video_feed():
    return Response(process_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=False, host ='0.0.0.0')