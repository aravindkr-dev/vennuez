from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from config import Config
from models import db
from schemas import ma
#from resources.bookings import CreateBooking, VerifyBooking , BookingStatus , CancelBooking , ShowSlots
#from friends_finder import MarkAvailable, FindFriends
from signup import CreateNewUser , CreateNewTurfOwner
from login import LoginUser
#from Admin.user_functions import FindUser , DeleteUsers

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
ma.init_app(app)
CORS(app)
api = Api(app)


#Users
"""api.add_resource(CreateBooking, '/api/bookings')
api.add_resource(VerifyBooking, '/api/bookings/verify')
api.add_resource(BookingStatus, '/api/bookings/booking_status')
api.add_resource(CancelBooking , '/api/bookings/Cancel_booking')"""

"""api.add_resource(MarkAvailable, '/api/mark_available')
api.add_resource(FindFriends, '/api/find_friends')"""

api.add_resource(CreateNewUser , '/api/create_new_user')
api.add_resource(LoginUser , '/api/login_user')



#venue owners
"""api.add_resource(ShowSlots , '/api/bookings/show_slots')

api.add_resource(ShowSlots , '/api/Create_turf_owner')"""
api.add_resource(CreateNewTurfOwner , '/api/create_turf_owner')


#Admin
"""api.add_resource(FindUser , '/api/find_user')
api.add_resource(DeleteUsers , '/api/delete_user')"""


@app.route('/')
def home():
    return {"status": "Turf Booking REST API Running"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)