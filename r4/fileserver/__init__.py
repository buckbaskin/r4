from flask import Flask, request
from werkzeug.utils import secure_filename
import os
UPLOAD_FOLDER = "/home/robert/Github/r4/r4/fileserver/uploads/"
server = Flask(__name__)
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from r4.fileserver import api
