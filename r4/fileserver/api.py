from r4.fileserver import server as router
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
@router.route('/' methods = ['GET','POST'])
def testing_upload():
    if request.method = 'POST':
        return redirect(url_for('uploaded_file',username = 'username', bucket = 'bucket'
                                r4id=request.form['r4id']))
    return '''
     <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@router.route('/<username>/<bucket>/<r4id>', methods = ['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(request.form['r4id'])
            file.save(os.path.join(router.config['UPLOAD_FOLDER'], r4id))
            return redirect(url_for('uploaded_file',username = request.form['username'], bucket = request.form['bucket']
                                    r4id=request.form['r4id']))
    return '''
     <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
print(router.config['UPLOAD_FOLDER'])
@router.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(router.config['UPLOAD_FOLDER'],
                               filename)
