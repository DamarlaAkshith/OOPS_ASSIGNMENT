from flask import Flask, flash, request, jsonify
from con import set_connection
import psycopg2
import json

app = Flask(__name__)


#
# CREATE TABLE students (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL
# );
#
# CREATE TABLE grades (
#     id SERIAL PRIMARY KEY,
#     student_id INTEGER REFERENCES students(id),
#     grade FLOAT(2) NOT NULL
# );


@app.route('/v1/add_student', methods=['POST'])
def add_student():
    # {
    #     "name": "Akshith",
    #     "grades": {
    #         "maths": 95,
    #         "physics": 99,
    #         "chemistry": 96
    #     }
    # }

    try:
        student_name = request.json['name']
        student_grades = request.json['grades']
        cur, conn = set_connection()

        # Convert grades to JSON string
        student_grades_str = json.dumps(student_grades)

        # Insert the new student into the database
        insert_query = "INSERT INTO students (name, grades) VALUES (%s, %s)"
        cur.execute(insert_query, (student_name, student_grades_str))
        conn.commit()

        return jsonify({'message': 'Student added successfully'})
    except (Exception, psycopg2.Error) as error:
        print("Error while adding student to the database", error)
        conn.rollback()
        return jsonify({'message': 'Error while adding student'})
    finally:
        cur.close()
        conn.close()


@app.route('/v1/calculate_average/<string:name>', methods=['GET'])
def calculate_average(name):
    try:
        cur, conn = set_connection()
        select_query = "SELECT grades FROM students WHERE name=%s"
        cur.execute(select_query, (name,))
        result = cur.fetchone()

        if result:
            grades_json = result[0]
            try:
                grades = json.loads(grades_json)
            except json.JSONDecodeError:
                return jsonify({'message': 'Error decoding grades JSON'}), 400

            if not isinstance(grades, list):
                return jsonify({'message': 'Grades field is not a list'}), 400

            if not grades:
                return jsonify({'message': 'No grades found for student'}), 404

            average = sum(grades) / len(grades)
            return jsonify({'average': average})
        else:
            return jsonify({'message': 'Student not found'}), 404
    except (Exception, psycopg2.Error) as error:
        error_message = 'Error while calculating average from the database: {}'.format(str(error))
        return jsonify({'message': error_message}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/v1/generate_report', methods=['GET'])
def generate_report():
    try:

        cur, conn = set_connection()
        # Retrieve all students from database
        cur.execute("SELECT id, name FROM students")
        students = cur.fetchall()
        if not students:
            return jsonify({'message': 'No students found'})

        # Iterate over students and retrieve grades from database
        report = []
        for student in students:
            student_id = student[0]
            student_name = student[1]
            cur.execute("SELECT grade FROM grades WHERE student_id=%s", (student_id,))
            grades = cur.fetchall()
            if not grades:
                continue
            grades = [grade[0] for grade in grades]
            average = sum(grades) / len(grades)
            report.append({'name': student_name, 'grades': grades, 'average': average})

        cur.close()
        return jsonify({'report': report})

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while generating report from the database", error)
        return jsonify({'message': 'Error while generating report'})
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
