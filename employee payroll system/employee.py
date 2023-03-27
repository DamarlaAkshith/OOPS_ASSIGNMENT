from flask import Flask, jsonify, request
from con import set_connection

app = Flask(__name__)



#
# CREATE TABLE roles (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     base_salary NUMERIC(10, 2) NOT NULL,
#     tax_rate NUMERIC(4, 2) NOT NULL,
#     benefits NUMERIC(10, 2) NOT NULL
# );
#
# CREATE TABLE employees (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     email VARCHAR(50) NOT NULL,
#     role_id INTEGER REFERENCES roles(id) NOT NULL
# );



# Endpoint to calculate the salary for an employee
@app.route('/employees/salary', methods=['POST'])
def calculate_salary():
    try:
        # Get the employee data from the request body
        employee_data = request.get_json()
        cur, conn = set_connection()
        # Retrieve the salary data for the employee's role
        cur.execute('SELECT base_salary, tax_rate, benefits FROM roles WHERE id = %s', (employee_data['role_id'],))
        row = cur.fetchone()
        base_salary = row[0]
        tax_rate = row[1]
        benefits = row[2]

        # Calculate the salary and taxes for the employee
        salary = base_salary - (base_salary * tax_rate)
        taxes = base_salary * tax_rate

        # Add the employee's benefits to the salary
        salary += benefits

        return jsonify({'salary': salary, 'taxes': taxes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to add a new employee
@app.route('/employees/add', methods=['POST'])
def add_employee():
    try:
        # Get the employee data from the request body
        # {
        #     "name": "John Smith",
        #     "email": "john.smith@example.com",
        #     "role_id": 2
        # }

        employee_data = request.get_json()
        cur, conn = set_connection()
        # Insert the employee into the database
        cur.execute(
            'INSERT INTO employees (name, email, role_id) VALUES (%s, %s, %s)',
            (employee_data['name'], employee_data['email'], employee_data['role_id'])
        )
        conn.commit()

        return jsonify({'message': 'Employee added successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/employees', methods=['GET'])
def get_all_employees():
    try:
        cur, conn = set_connection()
        cur.execute('SELECT id, name, email, role_id FROM employees')
        rows = cur.fetchall()
        employees = []
        for row in rows:
            employee = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'role_id': row[3]
            }
            employees.append(employee)
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/roles/add', methods=['POST'])
def add_role():
    try:
        # {
        #     "name": "Manager",
        #     "base_salary": 75000.00,
        #     "tax_rate": 0.30,
        #     "benefits": 10000.00
        # }

        data = request.get_json()
        name = data['name']
        base_salary = data['base_salary']
        tax_rate = data['tax_rate']
        benefits = data['benefits']

        cur, conn = set_connection()
        cur.execute('INSERT INTO roles (name, base_salary, tax_rate, benefits) VALUES (%s, %s, %s, %s)',
                    (name, base_salary, tax_rate, benefits))
        conn.commit()

        return jsonify({'message': 'Role added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/roles', methods=['GET'])
def get_all_roles():
    try:
        cur, conn = set_connection()
        cur.execute('SELECT id, name, base_salary, tax_rate, benefits FROM roles')
        rows = cur.fetchall()
        roles = []
        for row in rows:
            role = {
                'id': row[0],
                'name': row[1],
                'base_salary': float(row[2]),
                'tax_rate': float(row[3]),
                'benefits': float(row[4])
            }
            roles.append(role)
        return jsonify(roles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
