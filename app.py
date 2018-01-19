
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from boto3.s3.transfer import S3Transfer
import boto3
from utils import *
import json


GOOGLE_URL_SHORTEN_API = 'AIzaSyBrnkM64WKqmKa_FmRbR6WIZeAu-hXE-6I' # IP Address restrictions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['bmp', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Send message to SQS
def sendmessage(filename, bucket_name, coordinates):
    sqs = boto3.client('sqs', region_name='eu-central-1' )
    queue_url = 'https://eu-central-1.queue.amazonaws.com/129273668251/this-is-my-first-cli-created-queue'
    response = sqs.send_message(
    QueueUrl=queue_url,
    DelaySeconds=10,
    MessageAttributes={
        'Author': {
            'DataType': 'String',
            'StringValue': 'FlaskApp'
        }
    }, 
    MessageBody=('{"File_Path": "%s", "Bucket_name" : "%s", "Coordinates" : "%s"}' % 
        ('uploads/{}'.format(filename), bucket_name, coordinates))
    )
    return response


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return '''No file part'''
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return '''No file selected'''
        else:
            x1, x2 = int(request.form.get('x1')), int(request.form.get('x2'))
            y1, y2 = int(request.form.get('y1')), int(request.form.get('y2'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
              os.mkdir(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploadfile(os.path.join(app.config['UPLOAD_FOLDER'], filename), "microservice-backet-linuxacademyuser", 'uploads')
            sendmessage(filename, "microservice-backet-linuxacademyuser", (x1, y1, x2, y2))
            removefile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('index.html', error_message="File uploaded!")





if __name__ == '__main__':
    app.run(debug=True)

