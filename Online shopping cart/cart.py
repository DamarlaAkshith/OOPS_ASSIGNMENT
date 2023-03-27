from flask import Flask, flash, request, jsonify
from con import set_connection

app = Flask(__name__)

cart = {}


@app.route('/insert', methods=['POST'])
def add_to_cart():
    # {
    #     "item": "string",
    #     "price": float,
    #     "quantity": int
    # }
    data = request.get_json()
    item = data.get('item')
    price = data.get('price')
    quantity = data.get('quantity')
    if not item or not price or not quantity:
        return jsonify({'error': 'Invalid payload.'}), 400

    cur, conn = set_connection()
    try:
        cur.execute(
            "INSERT INTO cart (item, price, quantity) VALUES (%s, %s, %s)",
            (item, price, quantity)
        )
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert data due to: ", error)
        return jsonify({'error': 'Failed to add item to cart.'}), 500

    if item in cart:
        cart[item]['quantity'] += quantity
        cart[item]['price'] += price
    else:
        cart[item] = {'quantity': quantity, 'price': price}

    cur.close()
    conn.close()
    added_item = {item: {'quantity': quantity, 'price': price}}
    return jsonify(added_item)


@app.route('/', methods=['GET'])
def get_cart():
    cur, conn = set_connection()

    try:
        cur.execute("SELECT item, price, quantity FROM cart")
        rows = cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Failed to fetch data due to: ", error)
        return jsonify({'error': 'Failed to get cart contents.'}), 500

    temp_cart = {}
    for row in rows:
        item = row[0]
        price = row[1]
        quantity = row[2]
        if item in temp_cart:
            temp_cart[item]['quantity'] += quantity
            temp_cart[item]['price'] += price
        else:
            temp_cart[item] = {'quantity': quantity, 'price': price}

    cur.close()
    conn.close()

    return jsonify(temp_cart)


@app.route('/remove', methods=['DELETE'])
def remove_from_cart():
    {
        "item": "string",
        "quantity": int
    }
    data = request.get_json()
    item = data.get('item')
    quantity = data.get('quantity')
    if not item or not quantity:
        return jsonify({'error': 'Invalid payload.'}), 400

    cur, conn = set_connection()
    try:
        cur.execute(
            "UPDATE cart SET quantity = quantity - %s WHERE item = %s AND quantity >= %s",
            (quantity, item, quantity)
        )
        conn.commit()  # Commit the changes to the database
    except (Exception, psycopg2.Error) as error:
        print("Failed to delete data due to: ", error)
        return jsonify({'error': 'Failed to remove item from cart.'}), 500

    if cur.rowcount == 0:
        return jsonify({'error': f'{item} not found in cart or not enough quantity.'}), 400

    # Update the cart dictionary
    if item in cart:
        cart_quantity = cart[item]['quantity']
        if cart_quantity <= quantity:
            del cart[item]
        else:
            cart[item]['quantity'] -= quantity

    cur.close()
    conn.close()
    message = f"{quantity} {item} deleted successfully."
    return jsonify({'message': message}), 200


@app.route('/total', methods=['GET'])
def get_total_cart():
    cur, conn = set_connection()

    try:
        cur.execute("SELECT SUM(price * quantity) FROM cart")
        total_price = cur.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        print("Failed to fetch data due to: ", error)
        return jsonify({'error': 'Failed to get cart total.'}), 500

    cur.close()
    conn.close()

    return jsonify({'total_price': total_price})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
