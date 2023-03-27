from flask import Flask, flash, request, jsonify
import psycopg2

app = Flask(__name__)


def set_connection():
    try:
        conn = psycopg2.connect(
            host="172.16.1.236",
            port="5432",
            database="bctst",
            user="akshith",
            password="akshith"
        )
        cur = conn.cursor()
        print("database connected")
        return cur, conn
    except (Exception, psycopg2.Error) as error:
        print("Failed connected due to: ", error)
        return None, None


@app.route("/insert", methods=["POST"])
def create_student():
    cur, conn = set_connection()
    if not cur:
        return "Failed to connect to database", 500

    # extract data from the JSON payload
    data = request.json
    holder_name = data.get('holder_name')
    account_type = data.get('account_type')
    balance = data.get('balance')

    if not holder_name or not account_type or not balance:
        return "Missing required field(s)", 400

    cur.execute(
        'INSERT INTO bank1(holder_name, account_type, balance)'
        ' VALUES (%s, %s, %s);',
        (holder_name, account_type, balance)
    )
    conn.commit()
    cur.close()
    conn.close()

    return "Account created successfully", 201


# READ the details
@app.route("/", methods=["GET"])
def show_list():
    cur, conn = set_connection()
    if not cur:
        return "Failed to connect to database", 500

    cur.execute("SELECT * FROM bank1")
    data = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return str(data), 200


@app.route("/withdraw", methods=["PUT"])
def withdrawal():
    cur, conn = set_connection()
    if not cur:
        return "Failed to connect to database", 500

    srno = request.json.get("srno")
    amount = request.json.get("withdraw_amount")

    if not srno or not amount:
        return "Missing required field(s)", 400

    cur.execute("SELECT balance FROM bank1 WHERE srno = %s", (srno,))
    result = cur.fetchone()

    if not result:
        return "Account not found", 404

    balance = result[0]

    if int(balance) < int(amount):
        return "Insufficient balance", 400

    updated_amt = int(balance) - int(amount)

    cur.execute("""UPDATE bank1
                    SET balance = %s
                    WHERE srno = %s
                """, (updated_amt, srno))
    conn.commit()
    cur.close()
    conn.close()

    response = {
        "withdraw_amount": amount,
        "new_balance": updated_amt
    }

    return jsonify(response), 200


# UPDATE (Amount Deposit)
@app.route("/deposit", methods=["PUT"])
def deposit():
    cur, conn = set_connection()
    if not cur:
        return "Failed to connect to database", 500

    srno = request.json.get("srno")
    amount = request.json.get("deposit_amount")

    if not srno or not amount:
        return "Missing required field(s)", 400

    cur.execute("SELECT balance FROM bank1 WHERE srno = %s", (srno,))
    result = cur.fetchone()

    if not result:
        return "Account not found", 404

    balance = result[0]

    # if int(balance) < int(amount):
    #     return "Insufficient balance", 400

    updated_amt = int(balance) + int(amount)

    cur.execute("""UPDATE bank1
                      SET balance = %s
                      WHERE srno = %s
                  """, (updated_amt, srno))
    conn.commit()
    cur.close()
    conn.close()

    response = {
        "deposited_amount": amount,
        "new_balance": updated_amt
    }

    return jsonify(response), 200


# DELETE account
@app.route("/delete/<int:srno>", methods=["DELETE"])
def delete_account(srno):
    cur, conn = set_connection()

    cur.execute("DELETE FROM bank1 WHERE srno = %s", (srno,))

    conn.commit()
    cur.close()
    conn.close()

    return "Record deleted successfully"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
