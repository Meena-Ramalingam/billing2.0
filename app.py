import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

def fetch_product_data(product_code):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, price_per_piece FROM products WHERE product_code = ?
    ''', (product_code,))
    row = cursor.fetchone()
    conn.close()
    return row

@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    # Get the submitted form data
    product_codes = request.form.getlist('product_codes')
    quantities = request.form.getlist('quantities')
    
    # Process and update the database
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    
    for product_code, quantity in zip(product_codes, quantities):
        # Fetch the current present_stock for the product
        cursor.execute('SELECT present_stock FROM products WHERE product_code = ?', (product_code,))
        row = cursor.fetchone()
        
        if row is not None:
            current_stock = row[0]
            new_stock = current_stock - 60
            cursor.execute('UPDATE products SET present_stock = ? WHERE product_code = ?', (new_stock, product_code))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    # Redirect to the billing page (without data) for a new bill
    return redirect(url_for('index'))


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
