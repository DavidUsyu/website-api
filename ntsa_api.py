from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS # Import CORS

app = Flask(__name__)
CORS(app) # Initialize CORS for your app. This will allow all origins by default.

# Connect to the NTSA MySQL database
# It's generally better to put database connection setup inside a try-except block
# or use an application context to handle connection pooling and errors gracefully.
# For simplicity, we'll keep it here for now, but be aware of potential issues.
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Severin.10",
        port=3306,
        database="ntsa"
    )
    cursor = db.cursor(dictionary=True)
    print("Successfully connected to the NTSA database.")
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    # You might want to exit or handle this more gracefully in a production app
    # For development, just printing is often enough to see the issue.
    db = None # Set db to None if connection fails
    cursor = None


# Endpoint to verify vehicle by VIN
@app.route('/api/verify_vehicle/<vin>', methods=['GET'])
def verify_vehicle(vin):
    if db is None: # Check if database connection was successful
        return jsonify({"status": "error", "message": "Database connection failed."}), 500

    vin = vin.strip()  # Remove accidental whitespace

    print(f"Received VIN: {vin}")  # Debug VIN received at the endpoint

    query = """
        SELECT
            vr.VIN, vr.make, vr.model, vr.year, vr.registeredOwner, vr.registrationStatus,
            il.inspectionDate, il.inspectorName, il.accidentHistory, il.mileageVerified, il.remarks,
            il.make AS inspectedMake, il.model AS inspectedModel, il.year AS inspectedYear,
            il.manufacturer, il.manufacturedYear, il.mileage, il.fuelType, il.engineSize,
            il.enginePower, il.gearbox, il.bodyType, il.color, il.country,
            il.tampering, il.stolen
        FROM VehicleRecords vr
        LEFT JOIN InspectionLogs il ON vr.VIN = il.VIN
        WHERE vr.VIN = %s
    """
    try:
        cursor.execute(query, (vin,))
        result = cursor.fetchone()

        print(f"Query result: {result}")  # Debug query result

        if result:
            # Format inspectionDate to a string if it's a datetime object
            if 'inspectionDate' in result and isinstance(result['inspectionDate'], (type(None), type(''))):
                # If it's None or already a string, keep as is
                pass
            elif 'inspectionDate' in result and result['inspectionDate'] is not None:
                result['inspectionDate'] = result['inspectionDate'].isoformat() # Convert datetime to ISO string

            return jsonify({"status": "found", "data": result})
        else:
            return jsonify({"status": "not found", "message": "Vehicle record not available in NTSA records."})
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return jsonify({"status": "error", "message": f"Database query error: {err}"}), 500


if __name__ == '__main__':
    app.run(debug=True) # Defaults to host='127.0.0.1' and port=5000
