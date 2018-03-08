import datetime
from sqlalchemy import func

from model import User, Trip, Dest, TripDest, Attraction, Note, connect_to_db, db
from model import set_val_user_id, set_val_trip_id, set_val_dest_id, set_val_trip_dest_id, set_val_attraction_id, set_val_note_id

from server import app

from passlib.hash import argon2
import numpy as np

def load_users():
    """Load users from faker into database."""

    print "Users"

    for i, row in enumerate(open("seed_data/user_seed.txt")):
        row = row.rstrip()
        user_id, name, email, password = row.split("|")
        hashed_password = argon2.hash(password)

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)

    db.session.commit()


def load_trips():
    """Load trips into database."""

    print "Trips"

    for i, row in enumerate(open("seed_data/trip_seed.txt")):
        row = row.rstrip()
        trip_id, name, user_id = row.split("|")

        trip = Trip(name=name, user_id=user_id)
        db.session.add(trip)

    db.session.commit()


def load_dests():
    """Create destination into database
    Here, only "San Francisco" for testing.

    """
    for i in range(1, 21):
        dest = Dest(name="San Francisco")
        db.session.add(dest)

    db.session.commit()


def load_trips_dests():
    """Link trip and dest together."""

    for i in range(1, 21):
        trip_dest = TripDest(trip_id=i, dest_id=i)
        db.session.add(trip_dest)

    db.session.commit()


def format_dest_seed():
    """Process the raw dest data."""

    for i, row in enumerate(open("seed_data/attraction_seed_before.txt")):
        row = row.rstrip()
        index, name, lat, lng = map(lambda item: item.strip(), row.split("|"))

        print "{}|{}|{}".format(name, lat, lng)


def make_attraction_list():
    """Set different numbers of attractions to the destination."""

    landmarks, outdoors, cultures, parks, shopping = [], [], [], [], []

    for i, row in enumerate(open("seed_data/attractions_seed.txt")):
        # index 1: Landmarks
        # index 2: Outdoors
        # index 3: Cultures
        # index 4: Parks
        # index 5: Shopping
        row = row.rstrip()
        category, name, lat, lng = row.split("|")
        if category == '1':
            landmarks.append([name, lat, lng])
        elif category == '2':
            outdoors.append([name, lat, lng])
        elif category == '3':
            cultures.append([name, lat, lng])
        elif category == '4':
            parks.append([name, lat, lng])
        else:
            shopping.append([name, lat, lng])

    return landmarks, outdoors, cultures, parks, shopping


all_lst = make_attraction_list()


def load_attractions(all_lst):
    landmarks, outdoors, cultures, parks, shopping = map(lambda lst: np.array(lst), all_lst)

    for i in range(1, 11):
        #first 1-10 => family, friends
        attractions = []

        # landmark choice:
        num_landmarks = np.random.random_integers(10)
        landmarks_idx = np.random.choice(len(landmarks), num_landmarks, replace=False)
        landmarks_choices = landmarks[landmarks_idx]
        attractions.extend(landmarks_choices.tolist())

        # outdoor choice:
        num_outdoors = np.random.random_integers(0, 2)
        outdoors_idx = np.random.choice(len(outdoors), num_outdoors, replace=False)
        outdoors_choices = outdoors[outdoors_idx]
        attractions.extend(outdoors_choices.tolist())

        # culture choice:
        num_cultures = np.random.random_integers(5)
        cultures_idx = np.random.choice(len(cultures), num_cultures, replace=False)
        cultures_choices = cultures[cultures_idx]
        attractions.extend(cultures_choices.tolist())

        # park choice:
        num_parks = np.random.random_integers(0, 2)
        parks_idx = np.random.choice(len(parks), num_parks, replace=False)
        parks_choices = parks[parks_idx]
        attractions.extend(parks_choices.tolist())

        # shopping choice:
        num_shopping = np.random.random_integers(0, 2)
        shopping_idx = np.random.choice(len(shopping), num_shopping, replace=False)
        shopping_choices = shopping[shopping_idx]
        attractions.extend(shopping_choices.tolist())

        for attraction_info in attractions:
            name, attraction_lat, attraction_lng = attraction_info
            attraction = Attraction(name=name, attraction_lat=attraction_lat, attraction_lng=attraction_lng, dest_id=i)
            db.session.add(attraction)

        db.session.commit()

    for i in range(11, 16):
        #first 11-15 => culture-lover
        attractions = []

        # landmark choice:
        num_landmarks = np.random.random_integers(11)
        landmarks_idx = np.random.choice(len(landmarks), num_landmarks, replace=False)
        landmarks_choices = landmarks[landmarks_idx]
        attractions.extend(landmarks_choices.tolist())

        # culture choice:
        num_cultures = np.random.random_integers(6)
        cultures_idx = np.random.choice(len(cultures), num_cultures, replace=False)
        cultures_choices = cultures[cultures_idx]
        attractions.extend(cultures_choices.tolist())

        # park choice:
        num_parks = np.random.random_integers(0, 2)
        parks_idx = np.random.choice(len(parks), num_parks, replace=False)
        parks_choices = parks[parks_idx]
        attractions.extend(parks_choices.tolist())

        # shopping choice:
        num_shopping = np.random.random_integers(0, 2)
        shopping_idx = np.random.choice(len(shopping), num_shopping, replace=False)
        shopping_choices = shopping[shopping_idx]
        attractions.extend(shopping_choices.tolist())

        for attraction_info in attractions:
            name, attraction_lat, attraction_lng = attraction_info
            attraction = Attraction(name=name, attraction_lat=attraction_lat, attraction_lng=attraction_lng, dest_id=i)
            db.session.add(attraction)

        db.session.commit()

    for i in range(16, 21):
        #first 16-20 => sightseeing-only
        attractions = []

        # 1 landmark choice:
        num_landmarks = np.random.random_integers(12)
        landmarks_idx = np.random.choice(len(landmarks), num_landmarks, replace=False)
        landmarks_choices = landmarks[landmarks_idx]
        attractions.extend(landmarks_choices.tolist())

        # 2 outdoor choice:
        num_outdoors = np.random.random_integers(0, 1)
        outdoors_idx = np.random.choice(len(outdoors), num_outdoors, replace=False)
        outdoors_choices = outdoors[outdoors_idx]
        attractions.extend(outdoors_choices.tolist())

        # 3 culture choice:
        num_cultures = np.random.random_integers(5)
        cultures_idx = np.random.choice(len(cultures), num_cultures, replace=False)
        cultures_choices = cultures[cultures_idx]
        attractions.extend(cultures_choices.tolist())

        # 4 park choice:
        num_parks = np.random.random_integers(0, 1)
        parks_idx = np.random.choice(len(parks), num_parks, replace=False)
        parks_choices = parks[parks_idx]
        attractions.extend(parks_choices.tolist())

        # 5 shopping choice:
        num_shopping = np.random.random_integers(3)
        shopping_idx = np.random.choice(len(shopping), num_shopping, replace=False)
        shopping_choices = shopping[shopping_idx]
        attractions.extend(shopping_choices.tolist())

        for attraction_info in attractions:
            name, attraction_lat, attraction_lng = attraction_info
            attraction = Attraction(name=name, attraction_lat=attraction_lat, attraction_lng=attraction_lng, dest_id=i)
            db.session.add(attraction)

        db.session.commit()


def feed_seed_data():
    """Feed some data to db"""

    db.create_all()

    print '---------finished create_all()---------'
    to_continue = raw_input("to continue?")

    user = User(name='ellen', email='ellen30301@gmail.com', password='$argon2i$v=19$m=512,t=2,p=2$PSfkPMd4L0VorbUWAmDMmQ$lzKeHS+Mh9Mv9zwsty2dzQ')
    trip1 = Trip(name='First trip to Bay Area', user_id=1)
    trip2 = Trip(name='Backpacking in Mexico', user_id=1)
    dest1 = Dest(name='San Francisco', dest_lat='37.7749295', dest_lng='-122.4194155')
    dest2 = Dest(name='San Jose', dest_lat='37.3382082', dest_lng='-121.8863286')
    dest3 = Dest(name='Oaxaca', dest_lat='17.0731842', dest_lng='-96.7265889')
    dest4 = Dest(name='Mexico City', dest_lat='19.4326077', dest_lng='-99.133208')
    attraction1 = Attraction(name='Union Square', dest_id=1, attraction_lat='37.7879797', attraction_lng='-122.4075169')
    attraction2 = Attraction(name='Fishermans Warf', dest_id=1, attraction_lat='37.8079996', attraction_lng='-122.4177434')
    attraction3 = Attraction(name='Alcatraz Island', dest_id=1, attraction_lat='37.8269775', attraction_lng='-122.4229555')
    attraction4 = Attraction(name='Golden Gate Bridge', dest_id=1, attraction_lat='37.8199286', attraction_lng='-122.4782551')
    attraction5 = Attraction(name='Great Mall', dest_id=2, attraction_lat='37.415738', attraction_lng='-121.897412')
    attraction6 = Attraction(name='San Jose Musuem of Art', dest_id=2, attraction_lat='37.333675', attraction_lng='-121.890039')
    attraction7 = Attraction(name='Iglesia de Santo Domingo', dest_id=3, attraction_lat='17.0656987', attraction_lng='-96.7232421')
    attraction8 = Attraction(name='Monte Alban', dest_id=3, attraction_lat='17.0454573', attraction_lng='-96.76746730000')
    attraction9 = Attraction(name='Hierve el Agua', dest_id=3, attraction_lat='16.865738', attraction_lng='-96.27603579999')
    attraction10 = Attraction(name='National Museum of Anthropology', dest_id=4, attraction_lat='19.4260032', attraction_lng='-99.18627859999')
    attraction11 = Attraction(name='Frida Kahlo Museum', dest_id=4, attraction_lat='19.355143 ', attraction_lng='-99.1625249')
    attraction12 = Attraction(name='Palacio de Bellas Artes', dest_id=4, attraction_lat='19.4352', attraction_lng='-99.14120000000')
    note1 = Note(attraction_id=1, content='City tour bus')
    note2 = Note(attraction_id=1, content='Ice rink')
    note3 = Note(attraction_id=1, content='Try Andersen Bakery https://unionsquareshop.com/stores/andersen-bakery.html')
    note4 = Note(attraction_id=2, content='Eat clam chowder')
    note5 = Note(attraction_id=2, content='Buy socks in The SF Sock Market')
    note6 = Note(attraction_id=7, content='Dominican church founded in 1575')
    note7 = Note(attraction_id=8, content='The center of the ruins, rising on a man-made platform 400 meters above the Oaxaca Valley, is possibly Latin America\'s oldest and most impressive Pre-Columbian site.')
    note8 = Note(attraction_id=9, content='Small-group tour by minibus.One of the falls is 95 feet tall and the other one is 40 feet tall. They are made of carbonated water that falls from the top of the mountain.')
    note9 = Note(attraction_id=10, content='Considered one of the world\'s most comprehensive natural history museums, this famous institution houses four square kilometers of exhibits in 23 exhibition halls.')
    note10 = Note(attraction_id=11, content='The lifelong home of Frida Kahlo is now a museum dedicated to the work of this famous 20th-century artist.')
    note11 = Note(attraction_id=12, content='This historic white marble building serves as both the city\'s top performance hall and an art museum.')

    print '---------finished adding variable names---------'
    to_continue = raw_input("to continue?")

    db.session.add_all([user,
                        trip1, trip2,
                        dest1, dest2, dest3, dest4,
                        attraction1, attraction2, attraction3, attraction4, attraction5, attraction6,
                        attraction7, attraction8, attraction9, attraction10, attraction11, attraction12,
                        note1, note2, note3, note4, note5, note6, note7, note8, note9, note10, note11])
    db.session.commit()

    print "---------finished data except trips_dests---------"
    to_continue = raw_input("to continue?")

    td1 = TripDest(trip_id=1, dest_id=1)
    td2 = TripDest(trip_id=1, dest_id=2)
    td3 = TripDest(trip_id=2, dest_id=3)
    td4 = TripDest(trip_id=2, dest_id=4)
    db.session.add_all([td1, td2, td3, td4])
    db.session.commit()

    print "Seeds successfully added to db"


if __name__ == "__main__":
    connect_to_db(app)
    # db.create_all()
