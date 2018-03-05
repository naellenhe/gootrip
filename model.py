"""Models and database functions for Ratings project."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime
from collections import defaultdict, OrderedDict
import numpy as np
import re

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions
class User(db.Model):
    """User of the web app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    birthyear = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={}>".format(self.user_id, self.email)


class Trip(db.Model):
    """User's trips"""

    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relationship between trips and users
    user = db.relationship('User', backref='trips')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Trip trip_id={} name={}>".format(self.trip_id, self.name)


class Dest(db.Model):
    """Destination of a trip'"""

    __tablename__ = "dests"

    dest_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    dest_lat = db.Column(db.String(15), nullable=True)
    dest_lng = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relationship between trips and dests using association table
    trips = db.relationship('Trip',
                            secondary='trips_dests',
                            backref='dests')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Dest dest_id={} name={}>".format(self.dest_id, self.name)


class TripDest(db.Model):
    """Association between trips and destinations"""

    __tablename__ = "trips_dests"

    trip_dest_id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer,
                        db.ForeignKey('trips.trip_id'),
                        nullable=False)
    dest_id = db.Column(db.Integer,
                        db.ForeignKey('dests.dest_id'),
                        nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<TripDest trip_id={} dest_id={}>".format(self.trip_id, self.dest_id)


class Attraction(db.Model):
    """Attraction of a trip'"""

    __tablename__ = "attractions"

    attraction_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    attraction_lat = db.Column(db.String(15), nullable=True)
    attraction_lng = db.Column(db.String(15), nullable=True)
    photo = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)
    dest_id = db.Column(db.Integer,
                        db.ForeignKey('dests.dest_id'),
                        nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relationship between destinations and attractions
    dest = db.relationship('Dest', backref='attractions')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Attraction attraction_id={} name={}>".format(self.attraction_id, self.name)


class Note(db.Model):
    """Note of a attraction'"""

    __tablename__ = "notes"

    note_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    attraction_id = db.Column(db.Integer,
                              db.ForeignKey('attractions.attraction_id'),
                              nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    #Relationship between destinations and attractions
    attraction = db.relationship('Attraction', backref='notes')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<note note_id={} content={}>".format(self.note_id, self.content)


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id})
    db.session.commit()


def set_val_trip_id():
    """Set value for the next trip_id after seeding database"""

    # Get the Max trip_id in the database
    result = db.session.query(func.max(Trip.trip_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

    # Set the value for the next trip_id to be max_id + 1
    query = "SELECT setval('trips_trip_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id})
    db.session.commit()


def set_val_dest_id():
    """Set value for the next dest_id after seeding database"""

    # Get the Max dest_id in the database
    result = db.session.query(func.max(Dest.dest_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

    # Set the value for the next dest_id to be max_id + 1
    query = "SELECT setval('dests_dest_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id})
    db.session.commit()


def set_val_trip_dest_id():
    """Set value for the next trip_dest_id after seeding database"""

    # Get the Max trip_id in the database
    result = db.session.query(func.max(TripDest.trip_dest_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

    # Set the value for the next trip_id to be max_id + 1
    query = "SELECT setval('trips_dests_trip_dest_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id})
    db.session.commit()


def set_val_attraction_id():
    """Set value for the next attraction_id after seeding database"""

    # Get the Max attraction_id in the database
    result = db.session.query(func.max(Attraction.attraction_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

    # Set the value for the next attraction_id to be max_id + 1
    query = "SELECT setval('attractions_attraction_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id})
    db.session.commit()


def set_val_note_id():
    """Set value for the next note_id after seeding database"""

    # Get the Max note_id in the database
    result = db.session.query(func.max(Note.note_id)).one()
    if result[0]:
        max_id = int(result[0])
    else:
        max_id = 1

        # Set the value for the next note_id to be max_id + 1
        query = "SELECT setval('notes_note_id_seq', :new_id)"
        db.session.execute(query, {'new_id': max_id})
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


#for testing the route
def delete_trip(trip_id):
    trip = Trip.query.get(trip_id)
    trip_id = trip.trip_id

    print "##### Developer msg #### Deleting:", trip
    #Store dests in a list
    dests = [dest for dest in trip.dests]

    #Delete the id in association table
    trip_dest_ids = TripDest.query.filter_by(trip_id=trip_id).all()
    for trip_dest_id in trip_dest_ids:
        db.session.delete(trip_dest_id)
        db.session.commit()

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


def convert_search_word(keyword):
    """Process user input keyword to the search key word
    for LIKE method in SQLAlchemy.

    input : string # 'san francisco'
    output : string # '%san%francisco%'
    """

    words = keyword.split()
    word = "%" + "%".join(words) + "%"

    return word


def search_attractions(keyword):
    """Take the destination search keyword and find its all attractions."""

    search_keyword = convert_search_word(keyword)
    atts_query = db.session.query(Dest.name, Attraction.name, Attraction.attraction_lat, Attraction.attraction_lng).join(Attraction)
    atts_result = atts_query.filter(func.lower(Dest.name).like(func.lower(search_keyword))).all()
    possible_atts = [(attraction_name.title(), attraction_lat, attracion_lng) for (dest_name, attraction_name, attraction_lat, attracion_lng) in atts_result]
    distinct_atts = list(set(possible_atts))

    return distinct_atts


def find_possible_attractions(keyword):
    """Take in a destination name and find all attraction names related to it.
    Output: a list contains lists of attractions of different dest_id but same dest_name.

    defaultdict: (dictionary-like object)
        {
            21:
                [
                    u'Elephant mountain',
                    u'Taipei Zoo',
                    u'Raohe Street Night Market',
                    u'Shilin Night Market',
                    u'Lungshan Temple of Manka',
                    u'Tamsui station',
                    u'taipei 101'
                ],

            23:
                [
                    u'Ximen',
                    u'Taipei 101',
                    u'Elephant Mountain',
                    u'Raohe Street Night Market',
                    u'Taipei Fine Arts Museum',
                    u'National Chiang Kai Shek Memorial Hall',
                    u'Shilin Night Market'
                ]
        }

    """

    search_keyword = convert_search_word(keyword)
    dest_atts = db.session.query(Dest.dest_id, Attraction.name).join(Attraction).filter(func.lower(Dest.name).like(func.lower(search_keyword))).all()

    att_candidates = defaultdict(list)

    for dest_id_as_key, att_name in dest_atts:
        att_name = att_name.title()
        att_candidates[dest_id_as_key].append(att_name)

    return att_candidates.values()


def recommend_attractions(destination_keyword, existing_atts):
    """Recommend attractions using high relevance concept."""

    all_att_candidates = find_possible_attractions(destination_keyword)
    # all the attractions that the user inputted so far
    target_atts_input = existing_atts
    target_atts = map(lambda name: name.title(), target_atts_input)

    print "target_atts:", target_atts

    #count how many match using numpy isin method
    atts_with_count = []
    for att_candidate in all_att_candidates:
        mask = np.isin(att_candidate, target_atts)
        count = sum(mask)
        atts_with_count.append((count, att_candidate))

    #mask returns:
    #array([False,  True,  True,  True, False, False, False])
    #sum(mask) means counting the number of True

    #atts_with_count returns:
    #[(2, [u'Elephant mountain', u'Taipei Zoo', u'Raohe Street Night Market', u'Shilin Night Market', u'Lungshan Temple of Manka', u'Tamsui station', u'taipei 101']),
    #(1, [u'Ximen', u'Taipei 101', u'Elephant Mountain', u'Raohe Street Night Market', u'Taipei Fine Arts Museum', u'National Chiang Kai Shek Memorial Hall', u'Shilin Night Market'])]

    atts_relevance = defaultdict(list)
    for count, att_list in atts_with_count:
        atts_relevance[count].append(att_list)

    atts_higher_relevance = OrderedDict(sorted(atts_relevance.items(), key=lambda x: x[0], reverse=True))
    atts_in_relevance_order = atts_higher_relevance.values()

    # print "atts_higher_relevance:", atts_higher_relevance

    final_union_atts = []
    recommended_level = 0
    for atts_same_relevance in atts_in_relevance_order:
        recommended_level += 1
        atts_set = map(set, atts_same_relevance)
        union_atts = list(set.union(*atts_set).difference(set(target_atts)))
        final_union_atts.extend(union_atts)
        print "union_atts of level:", recommended_level, union_atts
        if len(final_union_atts) >= 5:
            break

    #Remove the duplicates if any while preserving order of the list
    distinct_atts = set()
    final_union_atts = [att for att in final_union_atts if not (att in distinct_atts or distinct_atts.add(att))]

    return (recommended_level, final_union_atts[:5])


    # return union_atts

    # sorted_atts_with_count = sorted(atts_with_count, key=lambda x: x[0], reverse=True)
    # return sorted_atts_with_count


def convert_url_to_html_link(text):
    """Find any urls in the notes and convert them to html <a> syntax."""

    urls = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    return urls.sub(format_url_html_link, text)


def format_url_html_link(match):
    """Convert plain urls to urls with <a> HTML syntax."""

    return "<a href='{}'>{}</a>".format(match.group(), match.group())



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///gooplanner'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    print "Connected to DB."

    # feed_seed_data()
