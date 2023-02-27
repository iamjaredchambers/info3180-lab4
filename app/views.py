import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name=" Jared Chambers")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
   
    # Instantiate your form class
        photoupload = UploadForm()
    # Validate file upload on submit
        if request.method == 'POST':
            if photoupload.validate_on_submit():
                photo = photoupload.file.data
            
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File Uploaded', 'success')
                return redirect(url_for('files'))  
        return render_template('upload.html', form = photoupload)
   
# Update this to redirect the user to a route that displays all uploaded image files
@app.route('/upload/<filename>') 
def get_image(filename):
    rootdir = os.getcwd()
    return send_from_directory(rootdir + '/' + app.config['UPLOAD_FOLDER'], filename)
    


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

    # change this to actually validate the entire form submission
    # and not just one field
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()
        # Get the username and password values from the form.
        
        if user is not None and  check_password_hash(user.password, password):
            login_user(user) 
            flash('Logged in successfully.', 'success')
            session['logged_in'] = True
            return redirect(url_for("upload"))
        else:
            flash('Username or Password is incorrect', 'danger') 
            
        flash_errors(form)
    return render_template("login.html", form=form)

def get_uploaded_images():
    rootdir = os.getcwd()
    #print (rootdir)
    filelist = []
    for subdir, dirs, files in os.walk(rootdir + '/uploads'):
        for file in files:
            filelist.append(file)
        return filelist


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('home'))



        
        

        # if user is already logged in, just redirect them to our secure page
        # or some other page like a dashboard
        
        # Remember to flash a message to the user
        
        # The user should be redirected to the upload form instead
   

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')
            
          
@app.route('/files')
@login_required
def files():
    if not session.get('logged_in'):
        abort(401)

    pictures = get_uploaded_images
    return render_template("files.html", pictures = pictures)


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
