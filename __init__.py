from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, json
from Forms import CreateUserForm, CreateMenuItemForm, CreateOrderForm, CreateReservationForm, LoginForm, PaymentForm
from Order import Order
from Reservation import Reservation
from payment import Payment
import shelve, User
from functools import wraps
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = '!42325Sd'

UPLOAD_FOLDER = 'static/images'  # ✅ Use your existing folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if uploaded file is an image"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('homelogin.html')

@app.route('/admin')
def homeAdmin():
    return render_template('home.html')

@app.route('/welcome')
@login_required
def homeClient():
    return render_template('homeClient.html')

feedback_list = []

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')

        if feedback_text:
            feedback_list.append(feedback_text)  # Store feedback

        return redirect(url_for('contact'))  # Refresh the page to show new feedback

    return render_template('contactUs2.html', feedback_list=feedback_list)

@app.route('/contactUs2')
def contact_us2():
    return render_template('contactUs2.html')

@app.route('/contactUs3')
def contact_us3():
    return render_template('contactUs3.html')

@app.route('/menu')
def menu():
    menu_items = {}
    db = shelve.open('menu.db', 'r')
    menu_items = db['MenuItems']
    db.close()
    menu_list = [menu_items[key] for key in menu_items]
    return render_template('menu.html', menu_list=menu_list)

@app.route('/createUser', methods=['GET', 'POST'])
@login_required
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('user.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from user.db.")

        user = User.User(
            create_user_form.first_name.data,
            create_user_form.last_name.data,
            create_user_form.email.data,
            create_user_form.phone.data
        )
        users_dict[user.get_user_id()] = user
        db['Users'] = users_dict
        db.close()

        return redirect(url_for('retrieve_users'))
    return render_template('createUser.html', form=create_user_form)

@app.route('/updateUser/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST':
        db = shelve.open('user.db', 'w')
        users_dict = db['Users']
        user = users_dict.get(id)
        user.set_first_name(update_user_form.first_name.data)
        user.set_last_name(update_user_form.last_name.data)
        user.set_email(update_user_form.email.data)
        user.set_phone(update_user_form.phone.data)
        user.set_privilege(update_user_form.userprivilege.data)
        users_dict[id] = user
        db['Users'] = users_dict
        db.close()
        return redirect(url_for('retrieve_users'))
    else:
        db = shelve.open('user.db', 'r')
        users_dict = db['Users']
        user = users_dict.get(id)
        update_user_form.first_name.data = user.get_first_name()
        update_user_form.last_name.data = user.get_last_name()
        update_user_form.email.data = user.get_email()
        update_user_form.phone.data = user.get_phone()
        update_user_form.userprivilege.data = user.get_privilege()
        db.close()
        return render_template('updateUser.html', form=update_user_form)

@app.route('/deleteUser/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    db = shelve.open('user.db', 'w')
    users_dict = db['Users']
    users_dict.pop(id)
    db['Users'] = users_dict
    db.close()
    return redirect(url_for('retrieve_users'))

@app.route('/retrieveUsers')
@login_required
def retrieve_users():
    users_dict = {}
    db = shelve.open('user.db', 'r')
    users_dict = db['Users']
    db.close()
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)
    return render_template('retrieveUsers.html', count=len(users_list), users_list=users_list)

@app.route('/createMenuItem', methods=['GET', 'POST'])
@login_required
def create_menu_item():
    create_menu_item_form = CreateMenuItemForm(request.form)

    if request.method == 'POST' and create_menu_item_form.validate():
        db = shelve.open('menu.db', 'c')
        menu_items = db.get('MenuItems', {})

        new_id = max([0] + [item['id'] for item in menu_items.values()]) + 1

        # ✅ Image upload handling
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)  # ✅ Save image to static/images/
            image_url = f'images/{filename}'  # ✅ Store relative path
        else:
            image_url = 'images/placeholder.jpg'  # ✅ Default image if none uploaded

        menu_item = {
            'id': new_id,
            'name': create_menu_item_form.name.data,
            'description': create_menu_item_form.description.data,
            'price': create_menu_item_form.price.data,
            'category': create_menu_item_form.category.data,
            'image_url': image_url  # ✅ Store image path
        }

        menu_items[menu_item['id']] = menu_item
        db['MenuItems'] = menu_items
        db.close()

        return redirect(url_for('retrieve_menu_items'))

    return render_template('createMenuItem.html', form=create_menu_item_form)

@app.route('/retrieveMenuItems')
def retrieve_menu_items():
    menu_items = {}
    db = shelve.open('menu.db', 'r')
    menu_items = db['MenuItems']
    db.close()
    menu_list = [menu_items[key] for key in menu_items]
    return render_template('retrieveMenuItems.html', menu_list=menu_list)

@app.route('/updateMenuItem/<int:id>/', methods=['GET', 'POST'])
def update_menu_item(id):
    update_menu_item_form = CreateMenuItemForm(request.form)
    db = shelve.open('menu.db', 'w')
    menu_items = db['MenuItems']
    menu_item = menu_items.get(id)

    if request.method == 'POST' and update_menu_item_form.validate():
        # Update text fields
        menu_item['name'] = update_menu_item_form.name.data
        menu_item['description'] = update_menu_item_form.description.data
        menu_item['price'] = update_menu_item_form.price.data
        menu_item['category'] = update_menu_item_form.category.data

        # Handle Image Upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)  # Save the new image
                menu_item['image_url'] = f'images/{filename}'  # Update image URL in the database

        db['MenuItems'] = menu_items
        db.close()
        return redirect(url_for('retrieve_menu_items'))

    # Populate form fields with existing data
    update_menu_item_form.name.data = menu_item['name']
    update_menu_item_form.description.data = menu_item['description']
    update_menu_item_form.price.data = menu_item['price']
    update_menu_item_form.category.data = menu_item['category']

    db.close()
    return render_template('updateMenuItem.html', form=update_menu_item_form, menu_item=menu_item)

@app.route('/deleteMenuItem/<int:id>', methods=['POST'])
def delete_menu_item(id):
    db = shelve.open('menu.db', 'w')
    menu_items = db['MenuItems']
    menu_items.pop(id, None)
    db['MenuItems'] = menu_items
    db.close()
    return redirect(url_for('retrieve_menu_items'))

@app.route('/createOrder', methods=['GET', 'POST'])
def create_order():
    create_order_form = CreateOrderForm(request.form)

    db = shelve.open('menu.db', 'r')
    menu_items = db.get('MenuItems', {})
    db.close()

    create_order_form.menu_items.choices = [(key, menu_items[key]['name']) for key in menu_items]

    if request.method == 'POST':
        db = shelve.open('order.db', 'c')
        orders = db.get('Orders', {})

        selected_items = [menu_items[int(item_id)] for item_id in create_order_form.menu_items.data]
        total_price = sum(
            float(item['price'].replace('S$', '').strip()) for item in selected_items
        )

        new_order = Order(
            customer_name=create_order_form.customer_name.data,
            table_number=create_order_form.table_number.data,
            menu_items=selected_items,
            total_price=total_price,
            status=create_order_form.status.data
        )

        orders[new_order.get_order_id()] = {
            'id': new_order.get_order_id(),
            'customer_name': new_order.get_customer_name(),
            'table_number': new_order.get_table_number(),
            'menu_items': selected_items,
            'total_price': total_price,
            'status': new_order.get_status()
        }

        db['Orders'] = orders
        db.close()

        return redirect(url_for('retrieve_orders'))
    return render_template('createOrder.html', form=create_order_form)


@app.route('/retrieveOrders')
def retrieve_orders():
    db = shelve.open('order.db', 'r')
    orders = db.get('Orders', {})  # Fetch all orders as a dictionary
    db.close()

    # Convert the orders dictionary to a list of dictionaries
    orders_list = [{'id': order_id, **order_data} for order_id, order_data in orders.items()]

    return render_template('retrieveOrders.html', orders=orders_list)


@app.route('/updateOrder/<int:id>/', methods=['GET', 'POST'])
def update_order(id):
    form = CreateOrderForm()

    # Fetch menu items for the form
    db_menu = shelve.open('menu.db', 'r')
    menu_items = list(db_menu.get('MenuItems', {}).values())
    db_menu.close()

    # Fetch the existing order data
    db = shelve.open('order.db', 'r')
    orders = db.get('Orders', {})
    order = orders.get(id, {})
    db.close()

    if request.method == 'POST':
        # Debug: Print form data
        print("Form Data Received:")
        print(f"Customer Name: {form.customer_name.data}")
        print(f"Table Number: {form.table_number.data}")
        print(f"Status: {form.status.data}")

        # Parse the order items from the form
        order_items = json.loads(request.form.get('order_items', '[]'))
        print("Order Items:", order_items)

        # Calculate total price
        total_price = sum(item['price'] * item['quantity'] for item in order_items)
        print("Total Price:", total_price)

        # Update the order with the new data
        order.update({
            'customer_name': form.customer_name.data,
            'table_number': form.table_number.data,  # Ensure this is being updated
            'status': form.status.data,
            'menu_items': order_items,
            'total_price': total_price
        })

        # Save the updated order back to the database
        db = shelve.open('order.db', 'w')
        orders[id] = order
        db['Orders'] = orders
        db.close()

        print("Order Updated Successfully!")
        return redirect(url_for('retrieve_orders'))

    # Populate the form with existing order data
    if order:
        form.customer_name.data = order.get('customer_name', '')
        form.table_number.data = order.get('table_number', 'N/A')
        form.status.data = order.get('status', 'Pending')
        # Pre-select the menu items in the form
        form.menu_items.data = [str(item.get('id')) for item in order.get('menu_items', [])]

    return render_template('updateOrder.html',
                           form=form,
                           menu_items=menu_items,
                           order_data=order)

@app.route('/deleteOrder/<int:id>', methods=['POST'])
def delete_order(id):
    db = shelve.open('order.db', 'w')
    orders = db.get('Orders', {})
    orders.pop(id, None)
    db['Orders'] = orders
    db.close()
    return redirect(url_for('retrieve_orders'))


@app.route('/createReservation', methods=['GET', 'POST'])
def create_reservation():
    form = CreateReservationForm(request.form)
    if request.method == 'POST' and form.validate():
        db = shelve.open('reservation.db', 'c')
        try:
            reservations = db['Reservations']
        except:
            reservations = {}
        reservation = Reservation(
            customer_name=form.customer_name.data,
            dining_date=form.dining_date.data,
            time=form.time.data,
            party_size=form.party_size.data,
            remarks=form.remarks.data
        )
        reservations[reservation.get_reservation_id()] = reservation
        db['Reservations'] = reservations
        db.close()
        return redirect(url_for('retrieve_reservations'))
    return render_template('createReservation.html', form=form)

@app.route('/retrieveReservations')
def retrieve_reservations():
    db = shelve.open('reservation.db', 'r')
    reservations = db.get('Reservations', {})
    db.close()
    return render_template('retrieveReservation.html', reservations=reservations.values())


@app.route('/updateReservation/<int:id>/', methods=['GET', 'POST'])
def update_reservation(id):
    form = CreateReservationForm(request.form)
    today = date.today().strftime('%Y-%m-%d')
    db = shelve.open('reservation.db', 'w')
    reservations = db['Reservations']
    reservation = reservations.get(id)

    if request.method == 'POST' and form.validate():
        reservation.set_customer_name(form.customer_name.data)
        reservation.set_dining_date(form.dining_date.data)
        reservation.set_time(form.time.data)
        reservation.set_party_size(form.party_size.data)
        reservation.set_remarks(form.remarks.data)
        db['Reservations'] = reservations
        db.close()
        return redirect(url_for('retrieve_reservations'))

    form.customer_name.data = reservation.get_customer_name()
    form.dining_date.data = reservation.get_dining_date()
    form.time.data = reservation.get_time()
    form.party_size.data = reservation.get_party_size()
    form.remarks.data = reservation.get_remarks()
    db.close()

    return render_template('updateReservation.html', form=form, today=today)

@app.route('/deleteReservation/<int:id>', methods=['POST'])
def delete_reservation(id):
    db = shelve.open('reservation.db', 'w')
    reservations = db['Reservations']
    reservations.pop(id)
    db['Reservations'] = reservations
    db.close()
    return redirect(url_for('retrieve_reservations'))

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST':
        db = shelve.open('user.db', 'c')
        users_dict = db.get('Users', {})

        # Find the next available user ID
        if users_dict:
            new_user_id = max(users_dict.keys()) + 1
        else:
            new_user_id = 1  # First user

        # Create the user with an explicit ID
        user = User.User(
            new_user_id,
            create_user_form.first_name.data,
            create_user_form.last_name.data,
            create_user_form.email.data,
            create_user_form.phone.data,
            create_user_form.username.data,
            create_user_form.userpassword.data,
            "client"
        )

        users_dict[new_user_id] = user
        db['Users'] = users_dict
        db.close()

        return redirect(url_for('login'))
    return render_template('registerPage.html', form=create_user_form)



@app.route('/login', methods=('GET', 'POST'))
def login():
    login_form = LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        users_dict = {}
        db = shelve.open('user.db', 'c')

        try:
            users_dict = db['Users']
            db.close()
        except:
            print("Error in retrieving Users from user.db.")

    if request.method == 'POST' and login_form.validate():
        try:
            db = shelve.open('user.db', 'r')
            users_dict = db.get('Users', {})
            db.close()

            for user_id, user in users_dict.items():
                if (user.get_username() == login_form.username.data and user.get_password() == login_form.loginpassword.data):
                    session['user_id'] = user_id
                    if user.get_privilege() == 'admin':
                        return redirect(url_for('homeAdmin'))
                    elif user.get_privilege() == 'client':
                        return redirect(url_for('homeClient'))

            flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash(f'Error during login: {str(e)}', 'danger')
    return render_template('loginPage.html', form=login_form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        # Clear the session data
        session.clear()
        # Flash a success message
        return redirect(url_for('home'))
    except Exception as e:
        # Log the error (if you have logging set up)
        print(f"Error during logout: {str(e)}")
        flash('An error occurred during logout.', 'error')
        return redirect(url_for('homeClient'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    create_order_form = CreateOrderForm(request.form)
    db = shelve.open('menu.db', 'r')
    menu_items = db.get('MenuItems', {})
    db.close()

    create_order_form.menu_items.choices = [(str(key), menu_items[key]['name']) for key in menu_items]

    return render_template('order.html',
                           form=create_order_form,
                           menu_items=menu_items)


@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'User not logged in'}), 400

        order_data = request.get_json()
        if not order_data:
            return jsonify({'success': False, 'message': 'Invalid order data'}), 400

        print("Received order data:", order_data)  # Debug print

        # Open the orders database
        db = shelve.open('order.db', 'c')
        orders = db.get('Orders', {})

        # Generate a new order ID
        order_id = len(orders) + 1

        # Create new order with complete information
        new_order = {
            "user_id": user_id,
            'id': order_id,
            'menu_items': order_data['items'],  # Use 'menu_items' instead of 'items'
            'total_price': order_data['total'],  # Use 'total_price' instead of 'total'
            'status': 'Pending',
            'order_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'table_number': 'N/A'  # Add default or make it part of the order_data
        }

        # Add to orders database
        orders[order_id] = new_order
        db['Orders'] = orders
        db.close()

        # ✅ Store the order data in session
        session['order_data'] = new_order

        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order_id
        })

    except Exception as e:
        print(f"Error processing checkout: {str(e)}")  # Debugging
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation():
    form = CreateReservationForm(request.form)
    today = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST' and form.validate():
        user_id = session['user_id']
        db = shelve.open('reservation.db', 'c')
        try:
            reservations = db['Reservations']
        except:
            reservations = {}

        reservation = Reservation(
            user_id=user_id,
            customer_name=form.customer_name.data,
            dining_date=form.dining_date.data,
            time=form.time.data,
            party_size=form.party_size.data,
            remarks=form.remarks.data
        )
        reservations[reservation.get_reservation_id()] = reservation
        db['Reservations'] = reservations
        db.close()
        return redirect(url_for('homeClient'))

    return render_template('reservationClient.html', form=form, today=today)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    order_id = request.args.get('order_id')
    order_data = session.get('order_data')

    if not order_id or not order_data:
        flash("No order data found. Please go back and place an order first.", "danger")
        return redirect(url_for('order'))

    total_amount = order_data.get('total_price', 0)

    form = PaymentForm(request.form)

    if request.method == 'POST' and form.validate():
        card_name = form.card_name.data
        card_no = form.card_no.data
        expiration_month = form.expiration_month.data
        expiration_year = form.year.data
        cvv = form.cvv.data
        delivery_add = form.delivery_add.data

        # ✅ Simulate successful payment processing
        payment_status = 'Success'

        # ✅ Update order status in the database
        db = shelve.open('order.db', 'w')
        orders = db.get('Orders', {})

        if order_id in orders:
            orders[int(order_id)]['status'] = 'Paid'
            orders[int(order_id)]['delivery_address'] = delivery_add
            db['Orders'] = orders
        db.close()

        flash("Payment Successful!", "success")
        return redirect(url_for('payment_confirmation', order_id=order_id))

    return render_template('payment.html', form=form, total_amount=total_amount)

@app.route('/payment_confirmation')
def payment_confirmation():
    order_id = request.args.get('order_id')
    return f"Payment confirmed! Your order ID is {order_id}"

if __name__ == '__main__':
    app.run(debug=True)

