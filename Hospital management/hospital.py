from flask import Flask, request, jsonify
from con import set_connection
from datetime import datetime
import psycopg2
from psycopg2 import errors

app = Flask(__name__)


# CREATE TABLE patients (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     dob DATE NOT NULL,
#     gender VARCHAR(10) NOT NULL,
#     admit_date DATE NOT NULL,
#     discharge_date DATE
# );
#
# CREATE TABLE treatments (
#     id SERIAL PRIMARY KEY,
#     patient_id INTEGER NOT NULL REFERENCES patients(id),
#     treatment_name VARCHAR(255) NOT NULL,
#     treatment_date DATE NOT NULL
# );
#
# CREATE TABLE admissions (
#     id SERIAL PRIMARY KEY,
#     patient_id INTEGER NOT NULL REFERENCES patients(id),
#     admission_date DATE NOT NULL,
#     discharge_date DATE,
#     diagnosis VARCHAR(255)
# );
#


# Define the routes for patient management
# {
#     "patient_name": "John",
#     "dob": "1990-01-01",
#     "gender": "M",
#     "admit_date": "2023-03-26"
# }

@app.route('/admit', methods=['POST'])
def admit_patient():
    try:
        data = request.get_json()
        patient_name = data['patient_name']
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        gender = data['gender']
        admit_date = datetime.strptime(data['admit_date'], '%Y-%m-%d').date()
        discharge_date = None
        cur, conn = set_connection()
        cur.execute(
            "INSERT INTO patients (name, dob, gender, admit_date, discharge_date) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (patient_name, dob, gender, admit_date, discharge_date)
        )

        patient_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"patient_id": patient_id, "message": "Patient admitted successfully"})
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({"error": str(e)})


@app.route('/admissions', methods=['GET'])
def get_admissions():
    try:
        cur, conn = set_connection()
        cur.execute("SELECT * FROM patients WHERE discharge_date IS NULL")
        patients = cur.fetchall()
        admissions = []
        for patient in patients:
            admission = {
                "patient_id": patient[0],
                "patient_name": patient[1],
                "dob": str(patient[2]),
                "gender": patient[3],
                "admit_date": str(patient[4])
            }

            admissions.append(admission)
        return jsonify(admissions)
    except (psycopg2.Error, Exception) as e:
        return jsonify({"error": str(e)})


# {
#     "patient_id": 1,
#     "treatment_name": "X-ray",
#     "treatment_date": "2023-03-27"
# }


@app.route('/treatments', methods=['POST'])
def add_treatment():
    try:
        data = request.get_json()
        patient_id = data['patient_id']
        treatment_name = data['treatment_name']
        treatment_date = datetime.strptime(data['treatment_date'], '%Y-%m-%d').date()
        cur, conn = set_connection()
        cur.execute("SELECT * FROM patients WHERE id = %s AND discharge_date IS NULL", (patient_id,))
        patient = cur.fetchone()
        if patient:
            cur.execute(
                "INSERT INTO treatments "
                "(patient_id, treatment_name, treatment_date) "
                "VALUES (%s, %s, %s)",
                (patient_id, treatment_name, treatment_date)
            )

            conn.commit()
            return jsonify({"message": "Treatment added successfully"})
        else:
            raise RecordNotFound("Patient record not found")
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# {
#     "patient_id": 1,
#     "discharge_date": "2023-03-28",
#     "diagnosis": "Fractured leg"
# }

@app.route('/patients/discharge', methods=['PUT'])
def discharge_patient():
    try:
        data = request.get_json()
        patient_id = data['patient_id']
        discharge_date = data['discharge_date']
        diagnosis = data['diagnosis']
        cur, conn = set_connection()
        cur.execute("SELECT * FROM admissions WHERE patient_id = %s AND discharge_date IS NULL", (patient_id,))
        admission = cur.fetchone()
        if admission:
            cur.execute("UPDATE admissions SET discharge_date = %s, diagnosis = %s WHERE id = %s",
                        (discharge_date, diagnosis, admission[0]))
            conn.commit()
            return jsonify({"message": "Patient discharged successfully"})
        else:
            raise AdmissionNotFound("Patient not currently admitted")
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({"error": str(e)})


@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient_by_id(patient_id):
    try:
        cur, conn = set_connection()
        cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cur.fetchone()
        if patient:
            cur.execute("SELECT * FROM admissions WHERE patient_id = %s ORDER BY admission_date DESC", (patient_id,))
            admissions = cur.fetchall()
            patient_record = {"id": patient[0], "name": patient[1], "dob": patient[2], "admissions": []}
            for admission in admissions:
                admission_record = {"id": admission[0], "admission_date": admission[2], "discharge_date": admission[3],
                                    "diagnosis": admission[4]}
                patient_record["admissions"].append(admission_record)
            return jsonify(patient_record)
        else:
            raise PatientNotFound("Patient not found")
    except (psycopg2.Error, Exception) as e:
        return jsonify({"error": str(e)})
if __name__ == "__main__":
    app.run(debug=True, port=5000)
