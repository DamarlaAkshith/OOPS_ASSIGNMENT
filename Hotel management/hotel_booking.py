from flask import Flask, request, jsonify
import psycopg2
from con import set_connection
from psycopg2 import errors

app = Flask(__name__)

# CREATE TABLE rooms (
#     id SERIAL PRIMARY KEY,
#     room_type TEXT NOT NULL,
#     is_available BOOLEAN NOT NULL,
#     CONSTRAINT unique_room_type UNIQUE (room_type)
# );
#
# CREATE TABLE bookings (
#     id SERIAL PRIMARY KEY,
#     room_type TEXT NOT NULL,
#     guest_name TEXT NOT NULL,
#     checkin_date DATE NOT NULL,
#     checkout_date DATE NOT NULL,
#     CONSTRAINT valid_booking_dates CHECK (checkin_date < checkout_date),
#     CONSTRAINT fk_rooms FOREIGN KEY (room_type) REFERENCES rooms(room_type) ON DELETE RESTRICT
# );


# {
#     "room_type": "AC"
# }


@app.route('/room_availability', methods=['POST'])
def get_room_availability():
    try:
        data = request.get_json()
        room_type = data['room_type']
        cur, conn = set_connection()
        cur.execute("SELECT COUNT(*) FROM rooms WHERE room_type = %s AND is_available = true", (room_type,))
        count = cur.fetchone()[0]
        return jsonify({"room_type": room_type, "availability": count})
    except (psycopg2.Error, Exception) as e:
        return jsonify({"error": str(e)})


# {
#     "room_type": "AC",
#     "guest_name": "Akshith",
#     "checkin_date": "2023-04-01",
#     "checkout_date": "2023-04-03"
# }

@app.route('/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()
        room_type = data['room_type']
        guest_name = data['guest_name']
        checkin_date = data['checkin_date']
        checkout_date = data['checkout_date']
        cur, conn = set_connection()
        cur.execute("INSERT INTO bookings (room_type, guest_name, checkin_date, checkout_date) VALUES (%s, %s, %s, %s)",
                    (room_type, guest_name, checkin_date, checkout_date))
        conn.commit()
        return jsonify({"message": "Booking created successfully"})
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({"error": str(e)})


@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    try:
        cur, conn = set_connection()
        cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cur.fetchone()
        if booking:
            cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
            conn.commit()
            return jsonify({"message": "Booking canceled successfully"})
        else:
            raise BookingNotFound("Booking not found")
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
