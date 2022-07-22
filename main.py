from asyncore import read
from platformdirs import user_cache_dir, user_config_dir
from flask import Blueprint, render_template,redirect, url_for, request, flash
from flask_login import login_required, current_user
# from nbformat import read
from . import db
from .models import ImageInfo, Labeller, ResponseInfo
import random
from pandas import DataFrame

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/survey_instructions')
@login_required
def survey_instructions():
    return render_template('survey_instructions.html', username=current_user.username)


@main.route('/survey-check-no', methods=['POST'])
@login_required
def call_survey():
    return display_survey('survey5.html')

def display_survey(survey_template):
    return render_template(survey_template)

@main.route('/survey')
@login_required
def survey():
    return display_survey('survey5.html')

@main.route('/labelling_instructions')
@login_required
def labelling_instructions():
    return render_template('labelling_instructions.html', username = current_user.username, id = current_user.id)


@main.route('/survey-check-yes', methods = ['POST'])    
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


@main.route('/dataset', methods=['GET'])
@login_required
def dataset():

    ## check the database if the user is logging his 20th databaset entry. If so, repeat the first databaset entry
    
    # response_info = ResponseInfo.query.filter_by(labeller_id = current_user.id).all()
    # i = 0

    # df = DataFrame(response_info[0].fetchall())
    # df.columns = response_info[0].keys()


    # # for response in response_info:
    # #     i = i+1
    
    #     # if len(response_info) % 20 == 0:

    # # print("Response type is ", type(response))
    # print("Response info type is ", type(response_info))

    # print("First Response info ", response_info[0])

    # print("Dataframe is ")
    # print(df)
    


    # print("First Response info type ", type(response_info[0]))

    # rinfo = response_info[0]

    # print("First info fields", response_info.image_1_url)

    # print("First info fields", rinfo.image_1_url)

    # counts = len(response_info)
    # print(counts)
    # print("url is", response_info[2].query.with_entities((response_info.image_1_url)))
    
    # response_info[2]
    # if counts%2 == 0:
        


    ## code from display random images
    ## get the urls for two random images from the database and display them
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

    # return render_template('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)

def read_random_images():
    print("Random images generated")
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

# @main.route('/dataset_entry_reshow', methods=['GET'])
# @login_required
# def dataset_entry_reshow(url1, url2, id1, id2):
#     return render_template('dataset4.html', id=current_user.id, image_1_url = url1, image_2_url = url2, image_1_id = id1, image_2_id = id2)




@main.route('/dataset', methods=['POST'])
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
        # print(images['image_1']['image_url'])
        # print(images['image_2']['image_url'])
        # print(images['image_1']['image_id'])
        # print(images['image_2']['image_id'])

        # render_template('dataset4.html', id=current_user.id, image_1_url = image_1_url, image_2_url = image_2_url, image_1_id = image_1_id, image_2_id = image_2_id)
        # return
        # return redirect(url_for('main.dataset', images=images))
        return redirect(url_for('main.dataset', image_1_url=image_1_url, image_2_url=image_2_url, image_1_id=image_1_id, image_2_id= image_2_id))
    else:
        # response_info = ResponseInfo.query.filter_by(image_1_id=image_1_id, image_2_id= image_2_id,
        #                                             labeller_id = user_id).first()
        
        # if response_info:
        #     flash('Dataset entry already exists in the database')        
        #     return redirect(url_for('main.dataset'))

        new_response = ResponseInfo(labeller_id = user_id, image_1_id=image_1_id, image_2_id=image_2_id, image_1_score=image_1_score, image_2_score=image_2_score)

        db.session.add(new_response)
        db.session.commit()

        return redirect(url_for('main.dataset'))