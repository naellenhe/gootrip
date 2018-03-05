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




if __name__ == "__main__":
    connect_to_db(app)
    # db.create_all()
