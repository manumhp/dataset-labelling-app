



import os
# from flask_migrate import migrate

from crypt import methods
# from dotenv import load_dotenv
from sqlalchemy import ForeignKey


from cProfile import label
from hashlib import new
from click import password_option

from werkzeug.security import generate_password_hash, check_password_hash

from asyncore import read
from platformdirs import user_cache_dir, user_config_dir
from flask import Blueprint, render_template,redirect, url_for, request, flash, Flask
from flask_login import LoginManager, login_required, current_user, login_user, login_required, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import random
import os
from dotenv import load_dotenv

load_dotenv()


app =  Flask(__name__, template_folder='templates')
 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace("://", "ql://", 1)

app.config['SECRET_KEY'] = str(os.environ['SECRET_KEY'])


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy(app)



class Labeller(UserMixin, db.Model):
    __tablename__ = 'labeller_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100))

class ImageInfo(db.Model):
    image_id = db.Column(db.String(200), primary_key=True)
    image_url = db.Column(db.String(300), unique=True)
    labelled = db.Column(db.Boolean, default=False)

class ResponseInfo(UserMixin, db.Model):

    dataset_entry_id = db.Column(db.Integer, primary_key=True)
    labeller_id = db.Column(db.Integer, ForeignKey("labeller_info.id"))
    image_1_id = db.Column(db.String(200), ForeignKey("image_info.image_id"))
    image_2_id = db.Column(db.String(200), ForeignKey("image_info.image_id"))
    
    image_1_score = db.Column(db.Float)
    image_2_score = db.Column(db.Float)    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    # login code
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    labeller = Labeller.query.filter_by(username=username).first()

    # check if the user exists
    # take the user supplied password, hash it and compare it against the hashed password stored in the database
    if not labeller or not check_password_hash(labeller.password, password):
        flash('Please check your login details and try again')
        return redirect(url_for('login'))
    
    login_user(labeller, remember=remember)
    return redirect(url_for('survey_instructions'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database
    username = request.form.get('username')
    password = request.form.get('password')

    labeller = Labeller.query.filter_by(username=username).first()  ## if this returns a user,  the user already exists in the database

    if labeller:
        flash('Labeller already exists in the database')
        return redirect(url_for('signup'))

    # new_labeller = Labeller(email=email, username=username, password=generate_password_hash(password, method='sha256'))
    new_labeller = Labeller(username=username, password=generate_password_hash(password, method='sha256'))

    

    db.session.add(new_labeller)
    db.session.commit()

    new_labeller = Labeller.query.filter_by(username=username).first()
    message = 'Your labeller id is ' + str(new_labeller.id) + '. Please remember it so that you can use it if you forget your password'
    flash(message)
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/survey_instructions')
@login_required
def survey_instructions():
    return render_template('survey_instructions.html', username=current_user.username)


@app.route('/survey-check-no', methods=['POST'])
@login_required
def call_survey():
    return display_survey('survey5.html')

def display_survey(survey_template):
    return render_template(survey_template)

@app.route('/survey')
@login_required
def survey():
    return display_survey('survey5.html')

###3 survey POST... Shows that the survey has been submitted
### create an entry in the table 

@app.route('/labelling_instructions')
@login_required
def labelling_instructions():
    return render_template('labelling_instructions.html', username = current_user.username, id = current_user.id)


@app.route('/survey-check-yes', methods = ['POST'])    
@login_required
def go_to_dataset_create():
    
    images = read_random_images()
    url1 = images['image_1']['image_url']
    url2 = images['image_2']['image_url']        
    id1 = images['image_1']['image_id']
    id2 = images['image_2']['image_id']

    return display_dataset_page('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)


def display_dataset_page(template, id, image_1_url , image_2_url , image_1_id , image_2_id ):
    return render_template(template, id=current_user.id, image_1_url = image_1_url, image_2_url = image_2_url, image_1_id = image_1_id, image_2_id = image_2_id)


@app.route('/dataset', methods=['GET'])
@login_required
def dataset():
    image_1_url = request.args.get('image_1_url')
    image_2_url = request.args.get('image_2_url')
    image_1_id = request.args.get('image_1_id')
    image_2_id = request.args.get('image_2_id')


    if not image_1_url:
        images = read_random_images()
        url1 = images['image_1']['image_url']
        url2 = images['image_2']['image_url']        
        id1 = images['image_1']['image_id']
        id2 = images['image_2']['image_id']
    
    else:
        url1 = image_1_url
        url2 = image_2_url
        id1 = image_1_id
        id2 = image_2_id

    displayed_page = display_dataset_page('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)

    return displayed_page


def read_random_images():
    images = ImageInfo.query.all()
    results = [
        {
            "image_id": image.image_id,
            "image_url": image.image_url,
            "labelled": image.labelled
        } for image in images
    ]
    counts = int(len(results)/3)
    random_indices = random.sample(range(0, counts), 2)
    
    result_first = results[random_indices[0]]
    result_second = results[random_indices[1]]

    result = {"image_1": result_first, "image_2": result_second}
    return result




@app.route('/dataset', methods=['POST'])
@login_required
def dataset_post():
    image_1_score = request.form.get('slider1WithValue')
    image_2_score = request.form.get('slider2WithValue')

    user_id = current_user.id
    image_1_id = request.form.get('image_1_id')
    image_2_id = request.form.get('image_2_id')
    images = {}
    if image_1_score == '0' and image_2_score == '0':

        image_1 = ImageInfo.query.filter_by(image_id=image_1_id).first()
        image_1_url = image_1.image_url

        image_2 = ImageInfo.query.filter_by(image_id=image_2_id).first()
        image_2_url = image_2.image_url

        images = {
            "image_1": {
                "image_url": image_1_url,
                "image_id": image_1_id,
            },
            "image_2": {
                "image_url": image_2_url,
                "image_id": image_2_id,
            }

        }

        zero_message = "Please do not give a 0 for both images"
        flash(zero_message)

        return redirect(url_for('dataset', image_1_url=image_1_url, image_2_url=image_2_url, image_1_id=image_1_id, image_2_id= image_2_id))
    else:

        new_response = ResponseInfo(labeller_id = user_id, image_1_id=image_1_id, image_2_id=image_2_id, image_1_score=image_1_score, image_2_score=image_2_score)

        db.session.add(new_response)
        db.session.commit()

        return redirect(url_for('dataset'))

    

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.init_app(app)

@login_manager.user_loader

def load_user(user_id):
    return Labeller.query.get(int(user_id))


if __name__ == '__main__':
    app.run()
