from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Owner, Console, TimeSlot, User
from datetime import datetime, timedelta
import logging


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        owner = Owner.query.filter_by(username=username).first()

        if owner and check_password_hash(owner.password_hash, password):
            session['user_id'] = owner.id
            session['username'] = owner.username
            session['user_type'] = 'owner'
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
            gaming_center_name = request.form['gaming_center_name']
            address = request.form['address']

            # Check if username or email already exists
            if Owner.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('register.html')

            if Owner.query.filter_by(email=email).first():
                flash('Email already exists', 'error')
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
            flash('Registration failed. Please try again.', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))

    owner = Owner.query.get(session['user_id'])
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
        'booking_rate': (booked_slots / total_slots * 100) if total_slots > 0 else 0
    }

    return render_template('dashboard.html', owner=owner, consoles=consoles, stats=stats)


@app.route('/add_console', methods=['GET', 'POST'])
def add_console():
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            console_type = request.form['console_type']
            hourly_rate = float(request.form['hourly_rate'])

            new_console = Console(
                name=name,
                console_type=console_type,
                hourly_rate=hourly_rate,
                owner_id=session['user_id']
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
def console_details(console_id):
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))

    console = Console.query.get_or_404(console_id)

    # Check if console belongs to current user
    if console.owner_id != session['user_id']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    slots = TimeSlot.query.filter_by(console_id=console_id).order_by(TimeSlot.start_time).all()

    return render_template('console_details.html', console=console, slots=slots, now=datetime.now())


@app.route('/add_slot/<int:console_id>', methods=['GET', 'POST'])
def add_slot(console_id):
    if 'user_id' not in session or session.get('user_type') != 'owner':
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))

    console = Console.query.get_or_404(console_id)

    if console.owner_id != session['user_id']:
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
                flash('End time must be after start time', 'error')
                return render_template('add_slot.html', console=console)

            if start_datetime < datetime.now():
                flash('Cannot create slots in the past', 'error')
                return render_template('add_slot.html', console=console)

            # Check for overlapping slots
            overlapping = TimeSlot.query.filter_by(console_id=console_id).filter(
                TimeSlot.start_time < end_datetime,
                TimeSlot.end_time > start_datetime
            ).first()

            if overlapping:
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

            flash('Time slot added successfully!', 'success')
            return redirect(url_for('console_details', console_id=console_id))

        except Exception as e:
            logging.error(f"Error adding slot: {e}")
            flash('Failed to add time slot. Please try again.', 'error')

    return render_template('add_slot.html', console=console)


@app.route('/available_slots')
def available_slots():
    # Get filter parameters
    console_type = request.args.get('console_type', '')
    date_filter = request.args.get('date', '')
    location = request.args.get('location', '')

    # Base query for available slots
    query = db.session.query(TimeSlot).join(Console).join(Owner).filter(
        TimeSlot.is_booked == False,
        TimeSlot.start_time > datetime.now(),
        Console.is_available == True
    )

    # Apply filters
    if console_type:
        query = query.filter(Console.console_type == console_type)

    if date_filter:
        filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        query = query.filter(db.func.date(TimeSlot.start_time) == filter_date)

    if location:
        query = query.filter(Owner.address.contains(location))

    slots = query.order_by(TimeSlot.start_time).all()

    # Get unique console types for filter
    console_types = db.session.query(Console.console_type).distinct().all()
    console_types = [ct[0] for ct in console_types]

    return render_template('available_slots.html', slots=slots, console_types=console_types,
                           current_filters={'console_type': console_type, 'date': date_filter, 'location': location})


@app.route('/book_slot/<int:slot_id>', methods=['GET', 'POST'])
def book_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)

    if slot.is_booked:
        flash('This slot is already booked', 'error')
        return redirect(url_for('available_slots'))

    if request.method == 'POST':
        try:
            customer_name = request.form['customer_name']
            customer_phone = request.form['customer_phone']
            customer_email = request.form.get('customer_email', '')
            customer_age = request.form.get('customer_age')
            special_requests = request.form.get('special_requests', '')

            # Contact preferences
            contact_sms = 'contact_sms' in request.form
            contact_whatsapp = 'contact_whatsapp' in request.form
            contact_email = 'contact_email' in request.form

            # Generate booking ID
            booking_id = slot.generate_booking_id()

            # Update slot with booking details
            slot.is_booked = True
            slot.booking_id = booking_id
            slot.customer_name = customer_name
            slot.customer_phone = customer_phone
            slot.customer_email = customer_email
            slot.customer_age = int(customer_age) if customer_age else None
            slot.special_requests = special_requests
            slot.contact_sms = contact_sms
            slot.contact_whatsapp = contact_whatsapp
            slot.contact_email = contact_email
            slot.booking_time = datetime.now()

            db.session.commit()

            # Redirect to payment
            return redirect(url_for('payment', booking_id=booking_id))

        except Exception as e:
            logging.error(f"Error booking slot: {e}")
            flash('Booking failed. Please try again.', 'error')

    # Check if user is logged in
    user = None
    if 'user_id' in session and session.get('user_type') == 'user':
        user = User.query.get(session['user_id'])

    return render_template('book_slot.html', slot=slot, user=user)


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
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('user_login.html')


@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('user_login'))

    user = User.query.get(session['user_id'])
    # Get user's bookings (you might need to add user_id to TimeSlot model for this)
    bookings = []  # Placeholder

    return render_template('user_dashboard.html', user=user, bookings=bookings)


@app.route('/toggle_console_status/<int:console_id>')
def toggle_console_status(console_id):
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 401

    console = Console.query.get_or_404(console_id)

    if console.owner_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403

    console.is_available = not console.is_available
    db.session.commit()

    return jsonify({'success': True, 'new_status': console.is_available})


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
