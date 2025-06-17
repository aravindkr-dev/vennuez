from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Owner, Console, TimeSlot, User, UserCoinBalance, CoinTransaction, Snack, ConsolePricingTier
from datetime import datetime, timedelta
from functools import wraps
from flask_login import login_user, logout_user, login_required, current_user
import logging
import pandas as pd
import io
import cloudinary
import cloudinary.uploader
import os
import json

def venue_details_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or session.get('user_type') != 'owner':
            flash('You must be logged in as a venue owner to access this page.', 'error')
            return redirect(url_for('login'))
        
        if not isinstance(current_user, Owner):
            flash('You must be logged in as a venue owner to access this page.', 'error')
            return redirect(url_for('login'))
        
        # Allow access to dashboard even if venue details are not complete
        if request.endpoint != 'dashboard' and not current_user.google_maps_link:
            flash('Please complete your venue details before accessing other features.', 'warning')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from flask_login import login_user
        username = request.form['username']
        password = request.form['password']

        owner = Owner.query.filter_by(username=username).first()

        if owner and check_password_hash(owner.password_hash, password):
            login_user(owner)
            session['user_type'] = 'owner'  # Keep this for role-based checks
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            phone = request.form['phone']
            gaming_center_name = request.form['center_name']
            address = request.form['address']

            # Check if username or email already exists
            if Owner.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('register.html')

            if Owner.query.filter_by(email=email).first():
                flash('Email already exists', 'error')
                return render_template('register.html')

            # Check if gaming center name already exists
            if Owner.query.filter_by(gaming_center_name=gaming_center_name).first():
                flash('Gaming center name already exists', 'error')
                return render_template('register.html')

            # Create new owner
            new_owner = Owner(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                phone=phone,
                gaming_center_name=gaming_center_name,
                address=address
            )

            db.session.add(new_owner)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash(f'Registration failed. {str(e)}', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/walkin_book_slot', methods=['POST'])
@login_required
def walkin_book_slot():
    data = request.get_json()
    print(f"Received walk-in booking data: {data}") # Debugging line
    console_id = data.get('consoleId')
    username = data.get('username')
    phone = data.get('phone')
    start_time_str = data.get('slotStartTime')
    end_time_str = data.get('slotEndTime')

    if not all([console_id, start_time_str, end_time_str, username, phone]):
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date/time format.'}), 400

    slot = TimeSlot.query.filter_by(console_id=console_id, start_time=start_time, end_time=end_time, is_booked=False).first()

    if slot:
        slot.is_booked = True
        slot.booking_type = 'walk-in'
        slot.customer_name = username
        slot.customer_phone = phone
        slot.booking_time = datetime.now()
        db.session.flush()
        slot.booking_id = slot.generate_booking_id() if hasattr(slot, 'generate_booking_id') else f"WK{slot.id}{int(datetime.now().timestamp())}"
        db.session.commit()

        return jsonify({'success': True, 'message': 'Walk-in booking successful!', 'booking_id': slot.booking_id}), 200
    else:
        return jsonify({'success': False, 'message': 'Slot not available or already booked.'}), 404


@app.route('/dashboard')
@login_required
@venue_details_required
def dashboard():
    # The login_required decorator handles authentication, and venue_details_required handles user type and venue details.
    # No need for explicit session checks here.

    owner = Owner.query.get(current_user.id)
    consoles = Console.query.filter_by(owner_id=owner.id).all()

    # Calculate statistics
    total_slots = 0
    booked_slots = 0
    total_revenue = 0

    for console in consoles:
        slots = TimeSlot.query.filter_by(console_id=console.id).all()
        total_slots += len(slots)
        for slot in slots:
            if slot.is_booked:
                booked_slots += 1
                total_revenue += slot.total_amount

    stats = {
        'total_consoles': len(consoles),
        'total_slots': total_slots,
        'booked_slots': booked_slots,
        'total_revenue': total_revenue,
        'booking_rate': (booked_slots / total_slots * 100) if total_slots > 0 else 0,
        'advance_collected': sum(slot.advance_paid for console in consoles for slot in console.slots if slot.is_booked)
    }

    # Check if all essential venue details are submitted
    venue_details_complete = (owner.images_uploaded and 
                              owner.google_maps_link and 
                              owner.amenities)

    return render_template('dashboard.html', owner=owner, consoles=consoles, stats=stats, venue_details_complete=venue_details_complete)

@app.route('/export_bookings')
@venue_details_required
def export_bookings():

    owner = Owner.query.get(current_user.id)
    bookings = []

    for console in owner.consoles:
        for slot in console.slots:
            if slot.is_booked:
                booking_data = {
                    'Booking ID': slot.booking_id,
                    'Customer Name': slot.customer_name,
                    'Phone Number': slot.customer_phone,
                    'Number of People': slot.number_of_people,
                    'Booking Date': slot.start_time.strftime('%Y-%m-%d'),
                    'Booking Time': slot.start_time.strftime('%Y-%m-%d %H:%M'),
                    'Duration': f"{(slot.end_time - slot.start_time).total_seconds() / 3600:.1f} hours",
                    'Console': console.name,
                    'Snacks Amount': slot.snacks_amount,
                    'Total Amount': slot.total_amount,
                    'Advance Paid': slot.advance_paid,
                    'Payment Status': slot.payment_status
                }
                bookings.append(booking_data)

    if not bookings:
        flash('No bookings found to export', 'info')
        return redirect(url_for('dashboard'))

    df = pd.DataFrame(bookings)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bookings')

    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'bookings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


@app.route('/upload_venue_details', methods=['POST'])
@login_required
def upload_venue_details():
    if not current_user.is_authenticated or not isinstance(current_user, Owner):
        flash('You must be logged in as a venue owner to access this page.', 'danger')
        return redirect(url_for('login'))
    
    owner = Owner.query.get(current_user.id)
    if not owner:
        flash('Owner not found.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
    
        # Handle image uploads
        image_urls = []
        for i in range(1, 5):
            image = request.files.get(f'image{i}')
            if image:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(image,
                    folder=f'venue_images/{owner.id}',
                    unique_filename=True,
                    overwrite=True)
                image_urls.append(result['secure_url'])
    
        
        # Update owner's image URLs
        # Initialize all venue_image fields to None
        owner.venue_image1 = None
        owner.venue_image2 = None
        owner.venue_image3 = None
        owner.venue_image4 = None

        # Assign uploaded image URLs to respective fields
        if len(image_urls) > 0:
            owner.venue_image1 = image_urls[0] if len(image_urls) > 0 else None
            owner.venue_image2 = image_urls[1] if len(image_urls) > 1 else None
            owner.venue_image3 = image_urls[2] if len(image_urls) > 2 else None
            owner.venue_image4 = image_urls[3] if len(image_urls) > 3 else None
            owner.images_uploaded = True
        else:
            owner.images_uploaded = False
        
        # Update other venue details
        google_maps_link = request.form.get('google_maps_link')
        amenities = request.form.get('amenities')
        
        if google_maps_link:
            owner.google_maps_link = google_maps_link
        if amenities:
            owner.amenities = json.dumps(amenities.split(','))
        
        db.session.commit()
        flash('Venue details updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating venue details: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))


@app.route('/add_console', methods=['GET', 'POST'])
@venue_details_required
def add_console():

    if request.method == 'POST':
        try:
            name = request.form['name']
            console_type = request.form['console_type']
            hourly_rate = float(request.form['hourly_rate'])

            new_console = Console(
                name=name,
                console_type=console_type,
                hourly_rate=hourly_rate,
                owner_id=current_user.id
            )

            db.session.add(new_console)
            db.session.commit()

            flash('Console added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            logging.error(f"Error adding console: {e}")
            flash('Failed to add console. Please try again.', 'error')

    return render_template('add_console.html')


@app.route('/console/<int:console_id>')
@venue_details_required
def console_details(console_id):

    console = Console.query.get_or_404(console_id)

    # Check if console belongs to current user
    if console.owner_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    slots = TimeSlot.query.filter_by(console_id=console_id).order_by(TimeSlot.start_time).all()

    return render_template('console_details.html', console=console, slots=slots, now=datetime.now())


@app.route('/add_slot/<int:console_id>', methods=['GET', 'POST'])
@venue_details_required
def add_slot(console_id):

    console = Console.query.get_or_404(console_id)

    if console.owner_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            # Parse datetime
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            # Validate times
            if start_datetime >= end_datetime:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': 'End time must be after start time'})
                flash('End time must be after start time', 'error')
                return render_template('add_slot.html', console=console)

            if start_datetime < datetime.now():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': 'Cannot create slots in the past'})
                flash('Cannot create slots in the past', 'error')
                return render_template('add_slot.html', console=console)

            # Check for overlapping slots
            overlapping = TimeSlot.query.filter_by(console_id=console_id).filter(
                TimeSlot.start_time < end_datetime,
                TimeSlot.end_time > start_datetime
            ).first()

            if overlapping:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': 'Time slot overlaps with existing slot'})
                flash('Time slot overlaps with existing slot', 'error')
                return render_template('add_slot.html', console=console)

            # Calculate total amount
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            total_amount = duration_hours * console.hourly_rate

            new_slot = TimeSlot(
                start_time=start_datetime,
                end_time=end_datetime,
                total_amount=total_amount,
                console_id=console_id
            )

            db.session.add(new_slot)
            db.session.commit()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Time slot added successfully'})
            
            flash('Time slot added successfully!', 'success')
            return redirect(url_for('console_details', console_id=console_id))

        except Exception as e:
            logging.error(f"Error adding slot: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)})
            flash('Failed to add time slot. Please try again.', 'error')

    return render_template('add_slot.html', console=console)


@app.route('/available_slots')
def available_slots():
    # Get filter parameters
    console_type = request.args.get('console_type', '')
    location = request.args.get('location', '')

    # Query unique owners/centers with at least one available slot
    query = Owner.query.join(Console).join(TimeSlot).filter(
        TimeSlot.is_booked == False,
        TimeSlot.start_time > datetime.now(),
        Console.is_available == True
    )
    if console_type:
        query = query.filter(Console.console_type == console_type)
    if location:
        query = query.filter(Owner.address.contains(location))
    query = query.distinct()
    owners = query.all()

    # Get unique console types for filter
    console_types = db.session.query(Console.console_type).distinct().all()
    console_types = [ct[0] for ct in console_types]

    return render_template('available_slots.html', 
                         owners=owners, 
                         console_types=console_types,
                         current_filters={
                             'console_type': console_type, 
                             'location': location
                         })


@app.route('/book_slot/<int:slot_id>', methods=['GET', 'POST'])
def book_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)

    if slot.is_booked:
        flash('This slot is already booked', 'error')
        return redirect(url_for('available_slots'))

    # Existing user logic
    user = None
    if current_user.is_authenticated and isinstance(current_user, User):
        user = User.query.get(current_user.id)

    if request.method == 'POST':
        # Get booking details from form
        number_of_people = request.form.get('number_of_people', type=int, default=1)
        special_requests = request.form.get('special_requests', '')
        customer_name = user.full_name if user else request.form.get('customer_name', '')
        customer_phone = user.phone if user else request.form.get('customer_phone', '')
        customer_email = user.email if user else request.form.get('customer_email', '')
        customer_age = user.age if user else request.form.get('customer_age', type=int)

        # Mark slot as booked and save details
        slot.is_booked = True
        slot.user_id = user.id if user else None
        slot.customer_name = customer_name
        slot.customer_phone = customer_phone
        slot.customer_email = customer_email
        slot.customer_age = customer_age
        slot.special_requests = special_requests
        slot.number_of_people = number_of_people
        slot.booking_time = datetime.now()
        slot.booking_id = slot.generate_booking_id() if hasattr(slot, 'generate_booking_id') else f"BK{slot.id}{int(datetime.now().timestamp())}"
        db.session.commit()

        flash('Booking successful!', 'success')
        return redirect(url_for('booking_confirmation', booking_id=slot.booking_id))

    # Get all unique future dates for this console
    available_dates = (
        db.session.query(db.func.date(TimeSlot.start_time))
        .filter(
            TimeSlot.console_id == slot.console_id,
            TimeSlot.is_booked == False,
            TimeSlot.start_time > datetime.now()
        )
        .distinct()
        .order_by(db.func.date(TimeSlot.start_time))
        .all()
    )
    available_dates = [d[0].strftime("%Y-%m-%d") if hasattr(d[0], 'strftime') else str(d[0]) for d in available_dates]

    return render_template('book_slot.html', slot=slot, user=user, available_dates=available_dates)


@app.route('/payment/<booking_id>')
def payment(booking_id):
    slot = TimeSlot.query.filter_by(booking_id=booking_id).first_or_404()
    return render_template('payment.html', slot=slot)


@app.route('/process_payment', methods=['POST'])
def process_payment():
    booking_id = request.form['booking_id']
    payment_method = request.form['payment_method']

    slot = TimeSlot.query.filter_by(booking_id=booking_id).first_or_404()

    # Simulate payment processing
    try:
        slot.payment_status = 'paid'
        slot.payment_id = f"PAY_{booking_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.session.commit()

        flash('Payment successful!', 'success')
        return redirect(url_for('booking_confirmation', booking_id=booking_id))

    except Exception as e:
        logging.error(f"Payment processing error: {e}")
        flash('Payment failed. Please try again.', 'error')
        return redirect(url_for('payment', booking_id=booking_id))


@app.route('/booking_confirmation/<booking_id>')
def booking_confirmation(booking_id):
    slot = TimeSlot.query.filter_by(booking_id=booking_id).first_or_404()
    return render_template('booking_confirmation.html', slot=slot)


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # Use Flask-Login's login_user function
            session['user_type'] = 'user'
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('user_login.html')


@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email', '')
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        age = request.form.get('age', type=int)

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('user_register.html')

        # Check if phone already exists
        if User.query.filter_by(phone=phone).first():
            flash('Phone number already registered', 'error')
            return render_template('user_register.html')

        try:
            # Create new user
            user = User(
                username=username,
                email=email if email else None,
                password_hash=generate_password_hash(password),
                full_name=full_name,
                phone=phone,
                age=age
            )
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user_login'))

        except Exception as e:
            logging.error(f"User registration error: {e}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')

    return render_template('user_register.html')


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    # The login_required decorator handles authentication.
    # No need for explicit session checks here.

    user = User.query.get(session['user_id'])
    bookings = TimeSlot.query.filter_by(user_id=user.id).order_by(TimeSlot.start_time.desc()).all()

    # Get coin balances for all gaming centers
    coin_balances = UserCoinBalance.query.filter_by(user_id=user.id).all()

    return render_template('user_dashboard.html', user=user, bookings=bookings, coin_balances=coin_balances , now=datetime.now())


@app.route('/manage_coins/<int:user_id>', methods=['GET', 'POST'])
def manage_coins(user_id):
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    owner = Owner.query.get(session['user_id'])
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        coins_to_add = request.form.get('coins', type=int)
        action = request.form.get('action')

        if coins_to_add and coins_to_add > 0:
            # Get or create user's coin balance for this gaming center
            balance = UserCoinBalance.query.filter_by(
                user_id=user.id,
                gaming_center_name=owner.gaming_center_name
            ).first()

            if not balance:
                balance = UserCoinBalance(
                    user_id=user.id,
                    gaming_center_name=owner.gaming_center_name,
                    coins=0
                )
                db.session.add(balance)

            if action == 'add':
                balance.coins += coins_to_add
                transaction_type = 'purchase'
                amount = coins_to_add
            elif action == 'deduct' and balance.coins >= coins_to_add:
                balance.coins -= coins_to_add
                transaction_type = 'deduction'
                amount = -coins_to_add
            else:
                flash('Insufficient coins for deduction', 'error')
                return redirect(url_for('manage_coins', user_id=user_id))

            # Record the transaction
            transaction = CoinTransaction(
                user_id=user.id,
                owner_id=owner.id,
                gaming_center_name=owner.gaming_center_name,
                amount=amount,
                transaction_type=transaction_type,
                description=f"Manual {action} by owner"
            )
            db.session.add(transaction)
            db.session.commit()

            flash(f'Successfully {action}ed {coins_to_add} coins', 'success')
            return redirect(url_for('manage_coins', user_id=user_id))

    # Get current balance and recent transactions
    balance = UserCoinBalance.query.filter_by(
        user_id=user.id,
        gaming_center_name=owner.gaming_center_name
    ).first()

    transactions = CoinTransaction.query.filter_by(
        user_id=user.id,
        gaming_center_name=owner.gaming_center_name
    ).order_by(CoinTransaction.created_at.desc()).limit(10).all()

    current_coins = balance.coins if balance else 0

    return render_template('manage_coins.html', user=user, current_coins=current_coins,
                           transactions=transactions, owner=owner)


@app.route('/search_users')
def search_users():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    query = request.args.get('q', '')
    users = []

    if query:
        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{query}%'),
                User.full_name.ilike(f'%{query}%'),
                User.phone.ilike(f'%{query}%')
            )
        ).limit(20).all()

    return render_template('search_users.html', users=users, query=query)


@app.route('/toggle_console_status/<int:console_id>')
def toggle_console_status(console_id):
    if not current_user.is_authenticated or current_user.user_type != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401

    console = Console.query.get_or_404(console_id)

    if console.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    console.is_available = not console.is_available
    db.session.commit()

    return jsonify({'success': True, 'new_status': console.is_available})


@app.route('/edit_slot/<int:slot_id>', methods=['GET', 'POST'])
@login_required
def edit_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)
    console = Console.query.get_or_404(slot.console_id)

    # Ensure only the owner of the console can edit the slot
    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to edit this slot.', 'danger')
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        try:
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            price = request.form['price']

            # Parse datetime
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            # Validate times
            if start_datetime >= end_datetime:
                flash('End time must be after start time', 'error')
                return render_template('edit_slot.html', slot=slot)

            # Update slot
            slot.start_time = start_datetime
            slot.end_time = end_datetime
            slot.total_amount = float(price)
            db.session.commit()
            flash('Slot updated successfully!', 'success')
            return redirect(url_for('console_details', console_id=slot.console_id))
        except Exception as e:
            logging.error(f"Edit slot error: {e}")
            flash('Failed to update slot. Please try again.', 'error')

    # Pre-fill form values
    return render_template('edit_slot.html', slot=slot)


@app.route('/delete_slot/<int:slot_id>', methods=['POST'])
@login_required
def delete_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)
    console = Console.query.get_or_404(slot.console_id)

    # Ensure only the owner of the console can delete the slot
    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to delete this slot.', 'danger')
        return redirect(url_for('owner_dashboard'))

    try:
        db.session.delete(slot)
        db.session.commit()
        flash('Slot deleted successfully!', 'success')
    except Exception as e:
        logging.error(f"Delete slot error: {e}")
        flash('Failed to delete slot. Please try again.', 'error')
    return redirect(url_for('console_details', console_id=slot.console_id))


@app.route('/api/available-slots')
def api_available_slots():
    date_str = request.args.get('date')
    console_id = request.args.get('console_id', type=int)
    slots_query = TimeSlot.query.join(Console).filter(
        TimeSlot.is_booked == False,
        Console.is_available == True,
        TimeSlot.start_time > datetime.now()
    )
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slots_query = slots_query.filter(db.func.date(TimeSlot.start_time) == filter_date)
        except Exception:
            return jsonify([])
    if console_id:
        slots_query = slots_query.filter(TimeSlot.console_id == console_id)

    slots = slots_query.order_by(TimeSlot.start_time).all()
    slot_list = []
    for slot in slots:
        slot_list.append({
            "id": slot.id,
            "time": f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
            "isBooked": slot.is_booked,
            "consoleId": slot.console_id,
            "consoleType": slot.console.console_type if slot.console else "",
            "consoleName": slot.console.name if slot.console else "",
            "price": slot.total_amount,
        })
    return jsonify(slot_list)


@app.route('/settle_slot/<int:slot_id>', methods=['POST'])
@login_required
def settle_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)
    console = Console.query.get_or_404(slot.console_id)

    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to settle this slot.', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    now = datetime.now()
    ten_minutes_before_end = slot.end_time - timedelta(minutes=10)
    logging.info(f"[CHECKOUT] Server time: {now}, Slot end time: {slot.end_time}, 10 min before: {ten_minutes_before_end}")
    
    if now < ten_minutes_before_end:
        flash(f'You can only checkout within 10 minutes before the slot ends or after it ends. (Server time: {now}, Slot end: {slot.end_time})', 'error')
        return redirect(url_for('console_details', console_id=slot.console_id))
    
    try:
        snacks_amount_raw = request.form.get('snacks_amount')
        final_amount_raw = request.form.get('final_amount')
        logging.info(f"[CHECKOUT] Form data: snacks_amount={snacks_amount_raw}, final_amount={final_amount_raw}")
        if snacks_amount_raw is None or final_amount_raw is None:
            flash('Missing snacks or final amount in form data.', 'error')
            return redirect(url_for('console_details', console_id=slot.console_id))
        snacks_amount = float(snacks_amount_raw)
        final_amount = float(final_amount_raw)
        
        # Update slot details
        slot.snacks_amount = snacks_amount
        slot.final_amount = final_amount
        slot.completed = True
        
        # Update user's spending if the slot is booked
        if slot.is_booked and slot.user_id:
            user = User.query.get(slot.user_id)
            if user:
                # Add the amount to user's total spending
                user.total_spent = (user.total_spent or 0) + final_amount
                
                # Create a transaction record
                transaction = CoinTransaction(
                    user_id=user.id,
                    owner_id=console.owner_id,
                    gaming_center_name=console.owner.gaming_center_name if console.owner else "",
                    amount=final_amount,
                    transaction_type='spending',
                    description=f'Payment for slot {slot.id} at {console.name}'
                )
                db.session.add(transaction)
        
        db.session.commit()
        flash('Checkout completed successfully!', 'success')
        return redirect(url_for('console_details', console_id=slot.console_id))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Checkout error: {str(e)} | Server time: {now}, Slot end: {slot.end_time}, Form: snacks={request.form.get('snacks_amount')}, final={request.form.get('final_amount')}")
        flash(f'Checkout failed: {str(e)}', 'error')
        return redirect(url_for('console_details', console_id=slot.console_id))


@app.route('/auto_slots/<int:console_id>')
@login_required
def auto_slots(console_id):
    console = Console.query.get_or_404(console_id)

    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to manage auto slots for this console.', 'danger')
        return redirect(url_for('owner_dashboard'))

    return render_template('auto_slots.html', console=console)


@app.route('/center_slots/<int:owner_id>')
def center_slots(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    slots = TimeSlot.query.join(Console).filter(
        Console.owner_id == owner_id,
        TimeSlot.is_booked == False,
        TimeSlot.start_time > datetime.now(),
        Console.is_available == True
    ).order_by(TimeSlot.start_time).all()
    return render_template('center_slots.html', owner=owner, slots=slots)


@app.route('/owner/snacks', methods=['GET', 'POST'])
@login_required
def manage_snacks():
    if not current_user.is_authenticated or not isinstance(current_user, Owner):
        flash('You are not authorized to manage snacks.', 'danger')
        return redirect(url_for('owner_dashboard'))
    owner_id = current_user.id
    if request.method == 'POST':
        name = request.form.get('name')
        rate = request.form.get('rate', type=float)
        if name and rate is not None:
            snack = Snack(owner_id=owner_id, name=name, rate=rate)
            db.session.add(snack)
            db.session.commit()
            flash('Snack added!', 'success')
        return redirect(url_for('manage_snacks'))
    snacks = Snack.query.filter_by(owner_id=owner_id).all()
    return render_template('manage_snacks.html', snacks=snacks)


@app.route('/owner/snacks/delete/<int:snack_id>', methods=['POST'])
@login_required
def delete_snack(snack_id):
    if not current_user.is_authenticated or not isinstance(current_user, Owner):
        flash('You are not authorized to delete snacks.', 'danger')
        return redirect(url_for('owner_dashboard'))
    snack = Snack.query.get_or_404(snack_id)
    if snack.owner_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('manage_snacks'))
    db.session.delete(snack)
    db.session.commit()
    flash('Snack deleted!', 'success')
    return redirect(url_for('manage_snacks'))


@app.route('/owner/snacks/json')
@login_required
def snacks_json():
    if not current_user.is_authenticated or not isinstance(current_user, Owner):
        return jsonify([])
    owner_id = current_user.id
    snacks = Snack.query.filter_by(owner_id=owner_id).all()
    return jsonify([{ 'name': s.name, 'rate': s.rate } for s in snacks])


@app.route('/console/<int:console_id>/pricing', methods=['GET', 'POST'])
@login_required
def manage_pricing(console_id):
    console = Console.query.get_or_404(console_id)

    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to manage pricing for this console.', 'danger')
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        max_people = request.form.get('max_people', type=int)
        rate_per_person = request.form.get('rate_per_person', type=float)
        if max_people and rate_per_person:
            tier = ConsolePricingTier(console_id=console_id, max_people=max_people, rate_per_person=rate_per_person)
            db.session.add(tier)
            db.session.commit()
            flash('Pricing tier added!', 'success')
            return redirect(url_for('manage_pricing', console_id=console_id))
    pricing_tiers = ConsolePricingTier.query.filter_by(console_id=console_id).all()
    return render_template('manage_pricing.html', console=console, pricing_tiers=pricing_tiers)


@app.route('/console/<int:console_id>/pricing/delete/<int:tier_id>', methods=['POST'])
@login_required
def delete_pricing_tier(console_id, tier_id):
    console = Console.query.get_or_404(console_id)

    if not current_user.is_authenticated or (isinstance(current_user, Owner) and console.owner_id != current_user.id):
        flash('You are not authorized to delete pricing tiers for this console.', 'danger')
        return redirect(url_for('owner_dashboard'))

    tier = ConsolePricingTier.query.get_or_404(tier_id)
    if tier.console_id != console_id:
        flash('Access denied', 'error')
        return redirect(url_for('manage_pricing', console_id=console_id))
    db.session.delete(tier)
    db.session.commit()
    flash('Pricing tier deleted!', 'success')
    return redirect(url_for('manage_pricing', console_id=console_id))


@app.route('/console/<int:console_id>/pricing/json')
def pricing_json(console_id):
    tiers = ConsolePricingTier.query.filter_by(console_id=console_id).order_by(ConsolePricingTier.max_people).all()
    return jsonify([
        { 'max_people': t.max_people, 'rate_per_person': t.rate_per_person }
        for t in tiers
    ])


@app.route('/set_owner_location', methods=['POST'])
def set_owner_location():
    if not current_user.is_authenticated or current_user.user_type != 'owner':
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')
    owner = Owner.query.get(current_user.id)
    if owner and lat and lon:
        owner.latitude = lat
        owner.longitude = lon
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid data'})





# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
