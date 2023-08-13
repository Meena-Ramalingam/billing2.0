import sqlite3
from flask import Flask,json, render_template, request, jsonify, redirect, url_for

import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'meenaramalingamspr@gmail.com'
EMAIL_PASSWORD = 'harishankar826'

def fetch_product_data(product_code):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, price_per_piece FROM products WHERE product_code = ?
    ''', (product_code,))
    row = cursor.fetchone()
    conn.close()
    return row

def send_email(subject, message, recipient):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = recipient

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, recipient, msg.as_string())

        print("Email sent successfully")
    except Exception as e:
        print("Error sending email:", str(e))


@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    data = request.json.get('product_data')  # Retrieve JSON data from the request
    
    # Process and update the database based on the JSON data
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()

    for product in data:
        product_code = product['product_code']
        quantity = product['quantity']

        # Fetch the current present_stock for the product
        cursor.execute('SELECT minimum_stock,present_stock FROM products WHERE product_code = ?', (product_code,))
        row = cursor.fetchone()

        if row is not None:
            current_stock, minimum_stock = row
            new_stock = current_stock - int(quantity)
            cursor.execute('UPDATE products SET present_stock = ? WHERE product_code = ?', (new_stock, product_code))
        if new_stock <= minimum_stock:
            dealer_email = 'dealer@example.com'  # Replace with the actual dealer's email
            product_name = fetch_product_data(product_code)[0]
            subject = f'Product Reorder: {product_name}'
            message = f"Please place an order for {quantity} units of {product_name} within 2 days."
            send_email(subject, message, dealer_email)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Redirect to the "Thank You" page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/')
def index():
    return render_template('billing.html')

@app.route('/get_product_data', methods=['POST'])
def get_product_data():
    product_code = request.json.get('product_code')
    product_data = fetch_product_data(product_code)
    return jsonify({'product_name': product_data[0], 'price': product_data[1]})

if __name__ == '__main__':
    app.run(debug=True)
