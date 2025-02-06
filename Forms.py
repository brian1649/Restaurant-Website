from tokenize import String
from datetime import datetime
from wtforms import Form, StringField, PasswordField, validators, EmailField, SelectMultipleField, DecimalField, SelectField, DateField, TimeField, IntegerField, TextAreaField, SubmitField
from flask_wtf import FlaskForm
class CreateUserForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone = StringField('Phone', [validators.Length(min=8, max=8), validators.DataRequired()])
    username = StringField("Username", [validators.Length(min=4, max=16), validators.DataRequired()])
    userpassword = PasswordField("Password", [validators.Length(min=8, max=16), validators.DataRequired()])
    userprivilege = SelectField(
        'User Privilege',
        choices=[
            ('client', 'Client'),
            ('admin', 'Admin')
        ],
        default='client'
    )

class CreateMenuItemForm(Form):
    name = StringField('Item Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = StringField('Description', [validators.Length(max=500), validators.Optional()])
    price = StringField('Price', [validators.DataRequired()])
    category = SelectField(
        'Category',
        choices=[
            ('Appetizers', 'Appetizers'),
            ('Main Courses', 'Main Courses'),
            ('Desserts', 'Desserts'),
        ],
        default='client'
    )
class CreateOrderForm(Form):
    customer_name = StringField('Customer Name', [
        validators.Length(min=1, max=150),
        validators.DataRequired()
    ])
    table_number = StringField('Table Number', [
        validators.Length(min=1, max=10),
        validators.DataRequired()
    ])
    menu_items = SelectMultipleField('Menu Items', choices=[], coerce=str)
    status = SelectField('Order Status', [validators.DataRequired()],
                        choices=[('Pending', 'Pending'),
                                ('In Progress', 'In Progress'),
                                ('Completed', 'Completed'),
                                ('Cancelled', 'Cancelled')],
                        default='Pending')

class CreateReservationForm(Form):
    customer_name = StringField('Customer Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    dining_date = StringField('Dining Date', [validators.DataRequired()])
    time = SelectField('Time', choices=[('12:00 PM', '12:00 PM'), ('1:00 PM', '1:00 PM'), ('2:00 PM', '2:00 PM')])
    party_size = StringField('Party Size', [validators.DataRequired()])
    remarks = StringField('Remarks', [validators.Optional()])

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    loginpassword = PasswordField('Password', [validators.Length(min=8, max=25), validators.DataRequired()])

class PaymentForm(FlaskForm):
    card_name = StringField('Cardholder Name', [
        validators.DataRequired(),
        validators.Length(min=1, max=150)
    ])

    card_no = StringField('Card Number', [
        validators.DataRequired(),
        validators.Length(min=16, max=16, message="Card number must be 16 digits.")
    ])

    expiration_month = SelectField('Expiration Month', validators=[validators.DataRequired()])

    year = SelectField('Expiration Year', validators=[validators.DataRequired()])

    cvv = StringField('CVV', [
        validators.DataRequired(),
        validators.Length(min=3, max=3, message="CVV must be 3 digits.")
    ])

    delivery_add = StringField('Delivery Address', [
        validators.DataRequired(),
        validators.Length(min=1, max=200)
    ])

    def _init_(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the expiration_month dropdown with months 1-12
        self.expiration_month.choices = [(str(i), datetime(2021, i, 1).strftime('%B')) for i in range(1, 13)]

        # Populate the year dropdown with current year and the next 10 years
        current_year = datetime.now().year
        self.year.choices = [(str(i), str(i)) for i in range(current_year, current_year + 11)]