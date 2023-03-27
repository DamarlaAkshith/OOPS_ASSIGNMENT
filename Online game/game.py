from flask import Flask, jsonify, request
from con import set_connection
import psycopg2
from psycopg2 import Error

app = Flask(__name__)


# CREATE TABLE characters (
#     name VARCHAR(50) PRIMARY KEY,
#     strength INTEGER NOT NULL,
#     agility INTEGER NOT NULL,
#     intelligence INTEGER NOT NULL
# );


@app.route('/api/character', methods=['POST'])
def create_character():
    """
    {
        "name": "Akshith",
        "strength": 10,
        "agility": 8,
        "intelligence": 6
    }
    """
    try:
        # Extract data from request
        data = request.get_json()
        name = data.get('name')
        strength = data.get('strength')
        agility = data.get('agility')
        intelligence = data.get('intelligence')

        # Validate input data
        if not name or not strength or not agility or not intelligence:
            return jsonify({'message': 'Invalid input data'}), 400

        # Create new character
        cur, conn = set_connection()

        cur.execute(
            f"INSERT INTO characters (name, strength, agility, intelligence) VALUES ('{name}', {strength}, {agility}, {intelligence})")
        conn.commit()
        cur.close()

        return jsonify({'message': 'Character created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Error creating character', 'error': str(e)}), 500


@app.route('/api/character/<string:name>', methods=['GET'])
def get_character(name):
    """
    Returns the character with the given name.
    """
    try:
        # Retrieve character data from database
        cur, conn = set_connection()

        cur.execute(f"SELECT * FROM characters WHERE name = '{name}'")
        character = cur.fetchone()
        cur.close()

        if not character:
            return jsonify({'message': 'Character not found'}), 404

        return jsonify({
            'name': character[0],
            'strength': character[1],
            'agility': character[2],
            'intelligence': character[3]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Error getting character', 'error': str(e)}), 500


@app.route('/api/attack', methods=['POST'])
def attack():
    """
    Simulates an attack between two characters.
    Example request body:
    {
        "attacker": "Ragnar",
        "defender": "Lagertha"
    }
    """
    try:
        # Extract data from request
        data = request.get_json()
        attacker = data.get('attacker')
        defender = data.get('defender')

        # Validate input data
        if not attacker or not defender:
            return jsonify({'message': 'Invalid input data'}), 400

        cur, conn = set_connection()

        # Retrieve character information from the database
        cur.execute("SELECT * FROM characters WHERE name=%s;", (attacker,))
        attacker_data = cur.fetchone()
        cur.execute("SELECT * FROM characters WHERE name=%s;", (defender,))
        defender_data = cur.fetchone()

        # Check if characters exist in the database
        if not attacker_data:
            return jsonify({'message': 'Attacker not found in the database'}), 404
        if not defender_data:
            return jsonify({'message': 'Defender not found in the database'}), 404

        # Calculate damage
        damage = attacker_data[2] - defender_data[3]
        if damage < 0:
            damage = 0

        # Apply damage to defender in the database
        new_intelligence = defender_data[4] - damage
        if new_intelligence <= 0:
            cur.execute("DELETE FROM characters WHERE name=%s;", (defender,))
            conn.commit()
            return jsonify(
                {'message': 'Attack successful', 'damage': damage, 'defender': defender, 'status': 'dead'}), 200
        else:
            cur.execute("UPDATE characters SET intelligence=%s WHERE name=%s;", (new_intelligence, defender,))
            conn.commit()
            return jsonify(
                {'message': 'Attack successful', 'damage': damage, 'defender': defender, 'status': 'alive'}), 200

    except (psycopg2.Error, Exception) as e:
        return jsonify({'message': 'Error attacking', 'error': str(e)}), 500

    finally:
        # Close the database connection
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
