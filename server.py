"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Trip, Dest, TripDest, Attraction, Note
from model import search_attractions, recommend_attractions, convert_url_to_html_link
from model import set_val_user_id, set_val_trip_id, set_val_dest_id, set_val_trip_dest_id, set_val_attraction_id, set_val_note_id

from passlib.hash import argon2

# from get_google_place_photo import get_place_photo_url
from flickr_url import get_flickr_photo_url

from get_wiki_description import get_wiki_description

# import geocoder

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/', methods=['GET'])
def index():
    """Homepage, also the register page"""

    if "user_id" in session:
        return redirect('/dashboard/' + str(session["user_id"]))
    else:
        return render_template("homepage.html", user_action='register')


@app.route('/register', methods=['POST'])
def register_process():
    """Process login."""

    set_val_user_id()

    # Get form variables
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]
    birthyear = request.form["birthyear"].strip()
    zipcode = request.form["zipcode"].strip()

    # hash the password by passlib
    hashed_password = argon2.hash(password)

    if User.query.filter_by(email=email).first():
        flash("This email address has already been taken.")
        return redirect('/')

    # birthyear and zipcode are optional
    if not birthyear:
        birthyear = None
    if not zipcode:
        zipcode = None

    # instantiate a new user

    new_user = User(name=name, email=email, password=hashed_password, birthyear=birthyear, zipcode=zipcode)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.user_id
    session["user_name"] = new_user.name

    flash("User {} registered successfully.".format(name))
    return redirect("/dashboard/{}".format(new_user.user_id))


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("homepage.html", user_action='login')


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    attempt_password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    # Verify if the password matches the hashed password in the db
    hashed_password = user.password

    if not argon2.verify(attempt_password, hashed_password):
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id
    session["user_name"] = user.name

    flash("Welcome Back!")
    return redirect("/dashboard/{}".format(user.user_id))


@app.route('/logout')
def logout():
    """Log out."""

    session.clear()

    flash("Logged Out.")
    return redirect("/")


@app.route("/user.json", methods=['POST'])
def get_user_profile():
    """Get user profile info."""

    #request shortcut for JSON
    user_id = request.get_json().get('user_id')
    print request.get_json()

    user = User.query.get(user_id)

    return jsonify({'name': user.name,
                    'email': user.email,
                    'password': '',
                    'birthyear': user.birthyear if user.birthyear else '',
                    'zipcode': user.zipcode if user.zipcode else ''})


@app.route('/settings', methods=['GET'])
def settings():
    """User's settings."""

    if "user_id" not in session:
        return redirect('/')

    user_id = session["user_id"]

    trips = Trip.query.filter_by(user_id=user_id).all()

    return render_template("user_settings.html", trips=trips)


@app.route("/update_user_profile.json", methods=['POST'])
def update_user_profile():
    """Update user profile"""

    print "update_user_profile:", request.get_json()

    user_id = request.get_json().get('user_id')
    new_name = request.get_json().get("name").strip()
    new_email = request.get_json().get("email").strip()
    new_password = request.get_json().get("password")
    new_birthyear = request.get_json().get("birthyear")
    new_zipcode = request.get_json().get("zipcode")

    #get user from database
    user = User.query.get(user_id)

    to_update = False
    if user.name != new_name and (new_name != ''):
        user.name = new_name
        to_update = True

    if user.email != new_email and (new_email != ''):
        user.email = new_email
        to_update = True

    if user.birthyear != new_birthyear and (new_birthyear != ''):
        user.birthyear = new_birthyear
        to_update = True

    if user.zipcode != new_zipcode and (new_zipcode != ''):
        user.zipcode = new_zipcode
        to_update = True

    # only updating when the password is not empty string and not same as current password
    if new_password and not argon2.verify(new_password, user.password):
        user.password = argon2.hash(new_password)
        to_update = True

    if to_update:
        db.session.commit()

    return jsonify({"msg": "successful"})



@app.route('/get-all-dests', methods=['GET'])
def get_all_dests():
    """Get list of all destinations (and attractions.)"""

    dests = db.session.query(Dest.name).all()
    dests = [dest[0] for dest in dests]
    dests = list(set(dests))

    # json format: {'dests': [dest1, dest2, ...]}
    return jsonify(dests=dests)


@app.route('/search', methods=['POST'])
def search_attraction_by_destination():
    """Search attractions by destination."""

    destination = request.form.get("destination-keyword")
    attractions_found = search_attractions(destination)

    return render_template("search_result.html", destination=destination, attractions=attractions_found)


@app.route('/get-recommendation', methods=['POST'])
def get_recommended_atts():
    """Retrun recommendation for attractions by the given dest name"""

    dest_id = request.form.get("dest_id")
    dest_name = request.form.get("dest_name")

    target_dest = db.session.query(Dest.name, Attraction.name).join(Attraction).filter(Dest.dest_id == dest_id).all()
    #target_dest returns: [(u'Taipei City', u'Ximen'), (u'Taipei City', u'Bitan Scenic Area'), (u'Taipei City', u'Elephant Mountain'), (u'Taipei City', u'Raohe Street Night Market'), (u'Taipei City', u'Tamsui station'), (u'Taipei City', u'Shilin Night Market'), (u'Taipei City', u'Songshan Cultural')]

    existing_atts = [dest_att[1] for dest_att in target_dest]
    #existing_atts returns: [u'Ximen', u'Bitan Scenic Area', u'Elephant Mountain', u'Raohe Street Night Market', u'Tamsui station', u'Shilin Night Market', u'Songshan Cultural']

    recommended_level, recommended_atts = recommend_attractions(dest_name, existing_atts)

    return jsonify(recommended_level=recommended_level, recommended_atts=recommended_atts)


@app.route('/dashboard/<int:user_id>', methods=['GET'])
def show_dashboard(user_id):
    """Show dashboard with most recent trip info."""

    if "user_id" in session and session["user_id"] == user_id:
        # #Use user of user_id = 1 for temporary use
        # user = User.query.get(user_id)

        ####Need to fix to get the most recent trip to show on dashboard###
        trips = Trip.query.filter_by(user_id=user_id).all()

        return render_template("dashboard.html", trips=trips)
    else:
        return redirect("/")


@app.route('/new-trip-id', methods=['POST'])
def make_new_trip_id():
    """Produce new trip id."""

    set_val_trip_id()

    user_id = session["user_id"]

    trip_name = request.form.get('trip').strip()

    #check the trip is existing or not
    trip = Trip.query.filter_by(name=trip_name, user_id=user_id).first()
    if not trip:
        #Add a new trip
        trip = Trip(name=trip_name, user_id=user_id)
        db.session.add(trip)
        db.session.commit()

        #Get the id of the trip
        trip = Trip.query.filter_by(name=trip_name, user_id=user_id).first()

        print "##### Developer msg #### Added:", trip
        return redirect('/new-trip/' + str(trip.trip_id))
    #if the trip is already in the database
    else:
        flash("You've already have the trip. Please create a new trip.")
        return redirect('/')


@app.route('/new-trip/<int:trip_id>', methods=['GET'])
def make_new_trip_form(trip_id):
    """Show new trip form."""

    if "user_id" not in session:
        return redirect('/')

    user_id = session["user_id"]

    trips = Trip.query.filter_by(user_id=user_id).all()

    # trip = Trip.query.filter_by(trip_id=trip_id, user_id=user_id).first()
    # Eagerly loading by using join will be more efficient
    trip_query = Trip.query.options(db.joinedload('dests').joinedload('attractions').joinedload('notes'))
    trip = trip_query.filter_by(trip_id=trip_id, user_id=user_id).first()

    # if trip is None, go back to homepage
    if not trip:
        return redirect('/')

    print "##### Developer msg #### Adding to:", trip

    return render_template("new_trip.html", trip=trip, trips=trips)


@app.route("/trip/<int:trip_id>", methods=['GET'])
def trip_detail(trip_id):
    """Show details of a specific trip."""

    if "user_id" not in session:
        return redirect('/')

    user_id = session["user_id"]

    trips = Trip.query.filter_by(user_id=user_id).all()

    # trip = Trip.query.filter_by(trip_id=trip_id, user_id=user_id).first()
    # Eagerly loading by using join will be more efficient
    trip_query = Trip.query.options(db.joinedload('dests').joinedload('attractions').joinedload('notes'))
    trip = trip_query.filter_by(trip_id=trip_id, user_id=user_id).first()

    trip_tree = {
        "trip_id": trip.trip_id,
        "name": trip.name,
        "created_at": trip.created_at,
        "dests": [
            {
                "dest_id": dest.dest_id,
                "name": dest.name,
                "created_at": dest.created_at,
                "attractions": [
                    {
                        "attraction_id": attraction.attraction_id,
                        "name": attraction.name,
                        "created_at": attraction.created_at,
                        "description": attraction.description,
                        "photo": attraction.photo,
                        "notes": [
                            {
                                'note_id': note.note_id,
                                'created_at' : note.created_at,
                                'content': convert_url_to_html_link(note.content),
                            } for note in attraction.notes]
                    } for attraction in dest.attractions]
            } for dest in trip.dests]
    }

    # if trip is None, go back to homepage
    if not trip:
        return redirect('/')

    # user = User.query.get(user_id)

    return render_template("trip_details.html", trip=trip_tree, trips=trips)


@app.route('/edit-trip/<int:trip_id>', methods=['GET'])
def edit_trip_form(trip_id):
    """Edit an existing trip."""

    if "user_id" not in session:
        return redirect('/')

    user_id = session["user_id"]

    trips = Trip.query.filter_by(user_id=user_id).all()

    # trip = Trip.query.filter_by(trip_id=trip_id, user_id=user_id).first()
    # Eagerly loading by using join will be more efficient
    trip_query = Trip.query.options(db.joinedload('dests').joinedload('attractions').joinedload('notes'))
    trip = trip_query.filter_by(trip_id=trip_id, user_id=user_id).first()

    # if trip is None, go back to homepage
    if not trip:
        return redirect('/')

    # user = User.query.get(user_id)

    print "##### Developer msg #### Editing:", trip

    return render_template("edit_trip.html", trip=trip, trips=trips)


@app.route('/new-dest-id', methods=['POST'])
def make_new_destination_id():
    """Produce new destination id."""

    set_val_dest_id()
    set_val_trip_dest_id()

    trip_id = request.form.get('trip_id')
    dest_name = request.form.get('dest_name').strip()

    # #Use Google geocoder instead
    # #Get geocode of the destination
    # g = geocoder.google(dest_name)
    # if g.status == 'OK':
    #     dest_lat, dest_lng = g.latlng
    # else:
    #     dest_lat, dest_lng = [None, None]

    #Add a new dest to db
    dest = Dest(name=dest_name)
    db.session.add(dest)
    db.session.commit()

    #Get the id of the trip
    dest = Dest.query.filter(Dest.name == dest_name).order_by(Dest.dest_id.desc()).first()
    trip_dest = TripDest(trip_id=trip_id, dest_id=dest.dest_id)
    db.session.add(trip_dest)
    db.session.commit()

    dest_info = {
        'dest_id': dest.dest_id,
        'name': dest.name,
    }

    print "##### Developer msg #### Destination added:", dest

    return jsonify(dest_info)


@app.route('/new-attraction', methods=['POST'])
def make_new_attraction():
    """Process new attraction and its notes."""

    set_val_attraction_id()
    set_val_note_id()

    attraction_name = request.form.get('attraction_name').strip()
    dest_id = request.form.get('dest_id')
    note_contents = request.form.getlist('note[]')  # list

    #Get wiki description
    wiki_content = get_wiki_description(attraction_name)
    if not wiki_content:
        wiki_content = None

    #Add a new attraction to db
    attraction = Attraction(name=attraction_name, dest_id=dest_id, description=wiki_content)
    db.session.add(attraction)
    db.session.commit()

    #Add notes to db
    if not note_contents:
        note_contents = ['']

    for note_content in note_contents:
        new_note = Note(content=note_content, attraction_id=attraction.attraction_id)
        db.session.add(new_note)
        db.session.commit()

    attraction_note_info = {
        'attraction_id': attraction.attraction_id,
        'name': attraction.name,
        'notes': [
            {
                'note_id': note.note_id,
                'content': note.content
            } for note in attraction.notes]
    }

    print "##### Developer msg #### Attraction added:", attraction

    return jsonify(attraction_note_info)


@app.route('/add-dest-coordinate', methods=['POST'])
def add_dest_coordinate():
    """Add the dest's coordinate to database"""

    dest_id = int(request.form.get('dest_id'))
    dest_lat = request.form.get('dest_lat')[:15]
    dest_lng = request.form.get('dest_lng')[:15]

    #Get the dest from db
    dest = Dest.query.get(dest_id)
    dest.dest_lat = dest_lat
    dest.dest_lng = dest_lng

    db.session.commit()

    print "##### Developer msg #### Coordinate added to: {}".format(dest)

    return "{} coordinate is successfully added to db.".format(dest.name)


@app.route('/add-attraction-coordinate', methods=['POST'])
def add_attraction_coordinate():
    """Add the attraction's coordinate to database"""

    attraction_id = int(request.form.get('attraction_id'))
    attraction_lat = request.form.get('attraction_lat')[:15]
    attraction_lng = request.form.get('attraction_lng')[:15]

    #Get the attraction from db
    attraction = Attraction.query.get(attraction_id)
    #Google place photo:
    # photo = get_place_photo_url(attraction.name, attraction_lat, attraction_lng)
    #Flickr photo:
    photo = get_flickr_photo_url(attraction.name, attraction_lat, attraction_lng)

    attraction.photo = photo
    attraction.attraction_lat = attraction_lat
    attraction.attraction_lng = attraction_lng

    db.session.commit()

    print "##### Developer msg #### Coordinate added to: {}".format(attraction)

    return "{} coordinate is successfully added to db.".format(attraction.name)


@app.route('/trips_dests.json', methods=['GET'])
def dest_info():
    """JSON information about all dests of all trips of the user."""

    all_dests = []

    user_id = session["user_id"]
    user = User.query.get(user_id)
    trips = user.trips

    for trip in trips:
        all_dests.extend(trip.dests)

    dests = {
        dest.dest_id: {
            "destName": dest.name,
            "destLat": dest.dest_lat,
            "destLng": dest.dest_lng,
        }
        for dest in all_dests
    }

    return jsonify(dests)


@app.route('/attractions.json', methods=['GET'])
def attraction_info():
    """JSON information about attractions."""

    #Get trip_id from ajax
    trip_id = request.args.get('trip_id')
    trip = Trip.query.get(trip_id)

    #Retrieve all dests from that trip
    dests = trip.dests

    #Make a dictionary of all attractions for all the dests of a trip
    #These will be used as markers in google map
    # dest_ids = [dest.dest_id for dest in dests]

    dests_attractions = {}
    for dest in dests:
        all_attractions = Attraction.query.filter(Attraction.dest_id == (dest.dest_id)).all()
        attractions = {
            attraction.attraction_id: {
                "attractionName": attraction.name,
                "attractionLat": attraction.attraction_lat,
                "attractionLng": attraction.attraction_lng,
            }
            for attraction in all_attractions
        }
        dests_attractions[dest.dest_id] = attractions

    return jsonify(dests_attractions)


@app.route("/update-trip.json", methods=['POST'])
def update_trip_detail():
    """Update details of a specific trip."""

    trip_id = request.form.get('trip_id')
    trip_name = request.form.get('trip_name').strip()

    trip = Trip.query.get(trip_id)
    trip.name = trip_name
    db.session.commit()

    return "Trip {} is updated successfully".format(trip_id)


@app.route("/update-dest.json", methods=['POST'])
def update_dest_detail():
    """Update details of a specific dest."""

    dest_id = request.form.get('dest_id')
    dest_name = request.form.get('dest_name').strip()

    dest = Dest.query.get(dest_id)
    dest.name = dest_name
    db.session.commit()

    return "Dest {} is updated successfully".format(dest_id)


@app.route("/update-attraction.json", methods=['POST'])
def update_attraction_detail():
    """Update details of a specific attraction."""

    attraction_id = request.form.get('attraction_id')
    attraction_name = request.form.get('attraction_name').strip()

    attraction = Attraction.query.get(attraction_id)
    attraction.name = attraction_name
    db.session.commit()

    return "Attraction {} is updated successfully".format(attraction_id)


@app.route("/update-note.json", methods=['POST'])
def update_note_detail():
    """Update details of a specific note."""

    note_id = request.form.get('note_id')
    note_content = request.form.get('note_content').strip()

    note = Note.query.get(note_id)
    note.content = note_content
    db.session.commit()

    return "note {} is updated successfully".format(note_id)


@app.route('/delete-trip', methods=['POST'])
def delete_trip():
    """delete a trip."""

    trip_id = request.form.get('trip_id')
    trip = Trip.query.get(trip_id)

    print "##### Developer msg #### Deleting:", trip

    #Store dests in a list
    dests = trip.dests

    #Delete the trip_dest_id in association table
    TripDest.query.filter_by(trip_id=trip_id).delete()

    #Destinations of the trip. Data type: List
    for dest in dests:
        for att in dest.attractions:
            for note in att.notes:
                db.session.delete(note)
                db.session.commit()
            db.session.delete(att)
            db.session.commit()
        db.session.delete(dest)
        db.session.commit()

    db.session.delete(trip)
    db.session.commit()

    return "Trip {} is deleted successfully".format(trip_id)


@app.route('/delete-dest', methods=['POST'])
def delete_dest():
    """delete a destination."""

    # need the dest's trip_id
    trip_id = request.form.get('trip_id')
    dest_id = request.form.get('dest_id')
    dest = Dest.query.get(dest_id)

    print "##### Developer msg #### Deleting:", dest

    #Delete the dest_dest_id in association table
    TripDest.query.filter_by(trip_id=trip_id, dest_id=dest_id).delete()

    #Attractions of the dest. Data type: List
    for att in dest.attractions:
        for note in att.notes:
            db.session.delete(note)
            db.session.commit()
        db.session.delete(att)
        db.session.commit()
    db.session.delete(dest)
    db.session.commit()

    return "Dest {} is deleted successfully".format(dest_id)


@app.route('/delete-attraction', methods=['POST'])
def delete_attraction():
    """delete a attraction."""

    attraction_id = request.form.get('attraction_id')
    attraction = Attraction.query.get(attraction_id)

    print "##### Developer msg #### Deleting:", attraction

    #Notes of the attraction. Data type: List
    for note in attraction.notes:
        db.session.delete(note)
        db.session.commit()
    db.session.delete(attraction)
    db.session.commit()

    return "Attraction {} is deleted successfully".format(attraction_id)


@app.route('/trip.json', methods=['GET'])
def trip_tree():
    """JSON information about attractions."""

    #Get trip_id from ajax
    trip_id = request.args.get('trip_id')
    trip = Trip.query.get(trip_id)

    trip_tree = {
        "trip_id": trip.trip_id,
        "name": trip.name,
        "created_at": trip.created_at,
        "dests": [
            {
                "dest_id": dest.dest_id,
                "name": dest.name,
                "created_at": dest.created_at,
                "attractions": [
                    {
                        "attraction_id": attraction.attraction_id,
                        "name": attraction.name,
                        "created_at": attraction.created_at,
                        "description": attraction.description,
                        "photo": attraction.photo,
                        "notes": [
                            {
                                'note_id': note.note_id,
                                'created_at': note.created_at,
                                'content': convert_url_to_html_link(note.content),
                            } for note in attraction.notes]
                    } for attraction in dest.attractions]
            } for dest in trip.dests]
    }

        # attractions = {
        # attraction.attraction_id: {
        #     "attractionName": attraction.name,
        #     "attractionLat": attraction.attraction_lat,
        #     "attractionLng": attraction.attraction_lng,
        # }
        # for attraction in all_attractions
        # }
    return jsonify(trip_tree)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    # app.debug = True
    # app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()
