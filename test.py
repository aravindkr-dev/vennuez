from app import db , app
from sqlalchemy import text
from models import Subscription, Owner

with app.app_context():
    subscription = Subscription.query.filter_by(user_id = 1).all()
    for x in subscription:
        venue = Owner.query.get_or_404(x.owner_id)
        print(venue.gaming_center_name , x.amount , x.user_id , x.owner_id , x.created_at)