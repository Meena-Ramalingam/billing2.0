import sqlite3
from flask import Flask,json, render_template, request, jsonify, redirect, url_for

import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
# Email configuration


def fetch_product_data(product_code):
    conn = sqlite3.connect('product_database.db')
    print("connected")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, price_per_piece FROM products WHERE product_code = ?
    ''', (product_code,))    
    row = cursor.fetchone()
    print("fetched")
    conn.close()
    return row

import ssl

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'techness2023@gmail.com'
EMAIL_PASSWORD = 'skkjjtiztkgksibe'

def send_email(subject, message, recipient):
    simple_email_context = ssl.create_default_context()
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = recipient

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls(context=simple_email_context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            print("Connected to server :-)")
            print()
            print(f"Sending email to - {recipient}")
            server.sendmail(EMAIL_USER, recipient, msg.as_string())
            print(f"Email successfully sent to - {recipient}")

    except smtplib.SMTPAuthenticationError as e:
        print("Authentication error:", e)
    
    except Exception as e:
        print("Error sending email:", str(e))


@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    data = request.json.get('product_data')  # Retrieve JSON data from the request
    
    # Process and update the database based on the JSON data
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    print("connected 1")

    for product in data:
        product_code = product['product_code']
        quantity = product['quantity']

        # Fetch the current present_stock for the product
        cursor.execute('SELECT minimum_stock,present_stock,dealer_order_count, dealer_email FROM products WHERE product_code = ?', (product_code,))
        row = cursor.fetchone()
        print(row)
        print("fetched 1")

        if row is not None:
            minimum_stock, present_stock, dealer_order_count, dealer_email  = row
            if quantity > present_stock:
                conn.close()
                return jsonify({'error': 'Order quantity exceeds available stock. '}), 400
            new_stock = present_stock - int(quantity)
            cursor.execute('UPDATE products SET present_stock = ? WHERE product_code = ?', (new_stock, product_code))
            print("updated 1 ", new_stock)
        if new_stock <= minimum_stock:
            # dealer_email = '211501051@rajalakshmi.edu.in'  # Replace with the actual dealer's email
            product_name = fetch_product_data(product_code)[0]
            subject = f'Product Reorder: {product_name}'
            message = f"Please place an order for {dealer_order_count} units of {product_name} within 2 days."
            send_email(subject, message, dealer_email)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Redirect to the "Thank You" page
    return jsonify({'message': 'Bill submitted successfully'})

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

    if product_data is None:
        return jsonify({'error': 'Product not found'})
    return jsonify({'product_name': product_data[0], 'price': product_data[1]})

if __name__ == '__main__':
    app.run(debug=True)
