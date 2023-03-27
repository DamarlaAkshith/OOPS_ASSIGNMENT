# tables

# CREATE TABLE stocks (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     quantity INTEGER NOT NULL,
#     price_per_unit FLOAT NOT NULL
# );
#
# CREATE TABLE transactions (
#     id SERIAL PRIMARY KEY,
#     stock_name VARCHAR(50) NOT NULL,
#     quantity INTEGER NOT NULL,
#     price_per_unit FLOAT NOT NULL,
#     transaction_type VARCHAR(10) NOT NULL,
#     transaction_date TIMESTAMP DEFAULT NOW()
# );


from flask import Flask, jsonify, request
import psycopg2
from con import set_connection

app = Flask(__name__)


# Routes
@app.route('/v1/stock/buy', methods=['POST'])
def buy_stock():
    # {
    #     "stock_name": "Airtel",
    #     "quantity": 3,
    #     "price_per_unit": 2000.00
    # }
    try:
        # Extract data from request
        data = request.get_json()
        stock_name = data.get('stock_name')
        quantity = data.get('quantity')
        price_per_unit = data.get('price_per_unit')

        # Validate input data
        if not stock_name or not quantity or not price_per_unit:
            return jsonify({'message': 'Invalid input data'}), 400

        cur, conn = set_connection()
        # Insert data into database
        cur.execute("INSERT INTO stocks (name, quantity, price_per_unit) VALUES (%s, %s, %s);",
                    (stock_name, quantity, price_per_unit))

        # Insert transaction data into database
        cur.execute("INSERT INTO transactions (stock_name, transaction_type, quantity, price_per_unit) "
                    "VALUES (%s, 'buy', %s, %s);", (stock_name, quantity, price_per_unit))
        conn.commit()

        return jsonify({'message': 'Stock bought successfully'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Error buying stock', 'error': str(e)}), 500


@app.route('/v1/stock/sell', methods=['POST'])
def sell_stock():
    # {
    #     "stock_name": "BSNL",
    #     "quantity": 10,
    #     "price_per_unit": 100.00
    # }
    try:
        # Extract data from request
        data = request.get_json()
        stock_name = data.get('stock_name')
        quantity = data.get('quantity')
        price_per_unit = data.get('price_per_unit')

        # Validate input data
        if not stock_name or not quantity or not price_per_unit:
            return jsonify({'message': 'Invalid input data'}), 400
        cur, conn = set_connection()
        # Retrieve data from database
        cur.execute("SELECT quantity, price_per_unit FROM stocks WHERE name=%s;", (stock_name,))
        stock_data = cur.fetchone()

        # Check if stock exists in the database
        if not stock_data:
            return jsonify({'message': 'Stock not found in the database'}), 404

        # Check if the quantity is less than or equal to the available quantity
        if quantity > stock_data[0]:
            return jsonify({'message': 'Insufficient quantity'}), 400

        # Calculate profit or loss
        profit_or_loss = (price_per_unit - stock_data[1]) * quantity

        # Insert transaction data into database
        cur.execute("INSERT INTO transactions (stock_name, transaction_type, quantity, price_per_unit) "
                    "VALUES (%s, 'sell', %s, %s);", (stock_name, quantity, price_per_unit))

        # Update data in database
        if quantity == stock_data[0]:
            cur.execute("DELETE FROM stocks WHERE name=%s;", (stock_name,))
        else:
            cur.execute("UPDATE stocks SET quantity=%s, price_per_unit=%s WHERE name=%s;",
                        (stock_data[0] - quantity, stock_data[1], stock_name))
        conn.commit()

        return jsonify({'message': 'Stock sold successfully', 'profit_or_loss': profit_or_loss}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Error selling stock', 'error': str(e)}), 500


@app.route('/v1/stock/profit_loss', methods=['GET'])
def calculate_profit_loss():
    try:
        cur, conn = set_connection()
        # Retrieve data from database
        cur.execute("SELECT SUM(price_per_unit * quantity) FROM stocks;")
        total_value = cur.fetchone()[0]
        cur.execute("SELECT SUM(price_per_unit * quantity) FROM transactions WHERE transaction_type='sell';")
        total_sell_cost = cur.fetchone()[0]
        cur.execute("SELECT SUM(price_per_unit * quantity) FROM transactions WHERE transaction_type='buy';")
        total_buy_cost = cur.fetchone()[0]

        # Calculate profit or loss
        if total_sell_cost is None:
            total_sell_cost = 0
        if total_buy_cost is None:
            total_buy_cost = 0
        profit_or_loss = total_value - total_sell_cost + total_buy_cost

        # Close the cursor and connection
        cur.close()
        conn.close()

        return jsonify({'profit_or_loss': profit_or_loss}), 200

    except Exception as e:
        # If any error occurs, rollback and close the cursor and connection
        conn.rollback()
        cur.close()
        conn.close()

        # Return error message
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
