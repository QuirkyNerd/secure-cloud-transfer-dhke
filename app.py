import os
import os.path
from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, send_file, flash
from werkzeug.utils import secure_filename
import DH
import pickle
import random

# Configuration
UPLOAD_FOLDER = os.path.abspath('./media/text-files/')
UPLOAD_KEY = os.path.abspath('./media/public-keys/')
ALLOWED_EXTENSIONS = {'txt'}
DATABASE_DIR = os.path.abspath('./media/database/')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key in production

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_directories_exist():
    """Ensure all required directories exist"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_KEY, exist_ok=True)
    os.makedirs(DATABASE_DIR, exist_ok=True)

'''
-----------------------------------------------------------
                    PAGE REDIRECTS
-----------------------------------------------------------
'''
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def back_home():
    return redirect(url_for('index'))

@app.route('/register')
def call_page_register_user():
    return render_template('register.html')

@app.route('/upload-file')
def call_page_upload():
    return render_template('upload.html')

def post_upload_redirect():
    return render_template('post-upload.html')

'''
-----------------------------------------------------------
                DOWNLOAD KEY-FILE
-----------------------------------------------------------
'''
@app.route('/public-key-directory/retrieve/key/<username>')
def download_public_key(username):
    try:
        for root, dirs, files in os.walk(UPLOAD_KEY):
            for file in files:
                if file.startswith(f"{username}-"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        return send_file(
                            file_path,
                            as_attachment=True,
                            download_name=f"{username}-publicKey.pem"
                        )
        flash('Public key not found')
        return redirect(url_for('downloads_pk'))
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('downloads_pk'))

@app.route('/file-directory/retrieve/file/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if os.path.isfile(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"encrypted_{filename}"
            )
        flash('File not found')
        return redirect(url_for('download_f'))
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('download_f'))

'''
-----------------------------------------------------------
        BUILD - DISPLAY FILE - KEY DIRECTORY
-----------------------------------------------------------
'''
@app.route('/public-key-directory/')
def downloads_pk():
    try:
        usernames = []
        db_file = os.path.join(DATABASE_DIR, 'database_1.pickle')
        
        if os.path.isfile(db_file):
            with open(db_file, 'rb') as f:
                usernames = pickle.load(f)
        
        if not usernames:
            return render_template('public-key-list.html', msg='No public keys found')
        
        return render_template('public-key-list.html', 
                             msg='',
                             itr=0,
                             length=len(usernames),
                             directory=usernames)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route('/file-directory/')
def download_f():
    try:
        files = []
        for entry in os.listdir(UPLOAD_FOLDER):
            full_path = os.path.join(UPLOAD_FOLDER, entry)
            if os.path.isfile(full_path):
                files.append(entry)
        
        if not files:
            return render_template('file-list.html', msg='No files found')
        
        return render_template('file-list.html',
                             msg='',
                             itr=0,
                             length=len(files),
                             list=files)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

'''
-----------------------------------------------------------
                UPLOAD ENCRYPTED FILE
-----------------------------------------------------------
'''
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if file part exists
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Validate file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(destination)
                flash('File successfully uploaded')
                return redirect(url_for('download_f'))
            except Exception as e:
                flash(f'Error saving file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Only .txt files are allowed')
            return redirect(request.url)
    
    return render_template('upload.html')

'''
-----------------------------------------------------------
        REGISTER USER AND GENERATE KEYS
-----------------------------------------------------------
'''
@app.route('/register-new-user', methods=['POST'])
def register_user():
    try:
        # Load existing data
        private_keys = []
        usernames = []
        
        db_file = os.path.join(DATABASE_DIR, 'database.pickle')
        db1_file = os.path.join(DATABASE_DIR, 'database_1.pickle')
        
        if os.path.isfile(db_file):
            with open(db_file, 'rb') as f:
                private_keys = pickle.load(f)
        
        if os.path.isfile(db1_file):
            with open(db1_file, 'rb') as f:
                usernames = pickle.load(f)
        
        # Validate username
        username = request.form.get('username', '').strip()
        if not username:
            flash('Username is required')
            return redirect(url_for('call_page_register_user'))
        
        if username in usernames:
            flash('Username already exists')
            return redirect(url_for('call_page_register_user'))
        
        # Get user details
        firstname = request.form.get('first-name', '').strip()
        secondname = request.form.get('last-name', '').strip()
        
        # Generate keys
        pin = random.randint(1, 128) % 64
        privatekey = DH.generate_private_key(pin)
        
        while str(privatekey) in private_keys:
            privatekey = DH.generate_private_key(pin)
        
        # Save user data
        private_keys.append(str(privatekey))
        usernames.append(username)
        
        with open(db_file, 'wb') as f:
            pickle.dump(private_keys, f)
        
        with open(db1_file, 'wb') as f:
            pickle.dump(usernames, f)
        
        # Generate and save public key
        publickey = DH.generate_public_key(privatekey)
        key_filename = f"{username}-{secondname.upper()}{firstname.lower()}-PublicKey.pem"
        key_path = os.path.join(UPLOAD_KEY, key_filename)
        
        with open(key_path, 'w') as f:
            f.write(str(publickey))
        
        return render_template('key-display.html', privatekey=str(privatekey))
    
    except Exception as e:
        flash(f'Registration error: {str(e)}')
        return redirect(url_for('call_page_register_user'))

'''
-----------------------------------------------------------
                    ERROR HANDLERS
-----------------------------------------------------------
'''
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    ensure_directories_exist()
    app.run(host='0.0.0.0', port=5000, debug=True)