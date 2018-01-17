
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from boto3.s3.transfer import S3Transfer
import boto3
from utils import *


UPLOAD_FOLDER = 'uploads'
# CROP_FOLDER = ''
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

            return redirect('/')
    return '''
    <!doctype html>
    <title>Image crop</title>
    <h1>Upload new image to crop</h1>
    <form method=post enctype=multipart/form-data>
    <table>
    <tr>
        <th> X1: <input type=test name=x1 size=4></th>
        <th> Y1: <input type=test name=y1 size=4></th>
    </tr><tr>
        <th> X2: <input type=test name=x2 size=4></th>
        <th> Y2: <input type=test name=y2 size=4></th>
    </tr>
    </table>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

