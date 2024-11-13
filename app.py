from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient(
    'mongodb+srv://theeye:test@eyecommunity.48uzc.mongodb.net/?retryWrites=true&w=majority&appName=eyeCommunity', 
    server_api=ServerApi('1')
)
db = client['eyeCommunity']
hiddenXregs = db['hiddenXregs-2']

# Define the schema validation
schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["roll_number", "phone", "stream", "experience"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is not required"
            },
            "roll_number": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is not required"
            },
            "experience": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "phone": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "stream": {
                "bsonType": "string",
                "description": "must be a string and is required"
            }
        }
    }
}

# Apply the schema validation to the collection
try:
    db.create_collection("hiddenXregs-2", validator=schema)
except errors.CollectionInvalid:
    db.command({
        "collMod": "hiddenXregs-2",
        "validator": schema,
        "validationLevel": "strict"
    })

# Create unique indexes for roll_number and phone
hiddenXregs.create_index("roll_number", unique=True)
hiddenXregs.create_index("phone", unique=True)

@app.route('/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Extract data from the form
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        email = request.form.get('email')
        experience = request.form.get('experience')
        phone = request.form.get('phone')
        stream = request.form.get('stream')
        
        # Check for required fields
        if not roll_number:
            return {"response": "Roll number is required."}
        if not phone:
            return {"response": "Phone number is required."}
        if not stream:
            return {"response": "Stream is required."}
        if not experience:
            return {"response": "Experience is required."}
        
        # Store the data in MongoDB
        try:
            hiddenXregs.insert_one({
                'name': name,
                'roll_number': roll_number,
                'email': email,
                'experience': experience,
                'phone': phone,
                'stream': stream
            })
            return {"response": "Done."}
        except errors.DuplicateKeyError:
            return {"response": "Duplicate roll number or phone number."}

    return render_template('regPage.html')

@app.route('/registrations')
def registrations():
    applicants = [i for i in list(hiddenXregs.find()) if i.get("name")]
    return render_template('registrations.html', applicants=applicants)

@app.route('/registrations/json', methods=['GET'])
def get_all_registrations_json():
    try:
        # Fetch all applicants and their showup status
        applicants = hiddenXregs.find()
        applicants_list = [
            {
                "id": str(applicant["_id"]),
                "name": applicant.get("name"),
                "roll_number": applicant.get("roll_number"),
                "showup": applicant.get("showup", False)
            }
            for applicant in applicants
        ]
        return jsonify(applicants_list)
    except Exception as e:
        return {"response": f"Error: {str(e)}"}, 500

@app.route('/showup/<_id>', methods=['POST', 'DELETE'])
def toggle_showup(_id):
    try:
        record_id = ObjectId(_id)
        
        if request.method == 'POST':
            result = hiddenXregs.update_one({'_id': record_id}, {'$set': {'showup': True}})
            if result.modified_count == 0:
                return {"response": "Already marked as showup."}, 200
            return {"response": "Showup marked successfully."}
        
        elif request.method == 'DELETE':
            result = hiddenXregs.update_one({'_id': record_id}, {'$set': {'showup': False}})
            if result.modified_count == 0:
                return {"response": "Already unmarked as showup."}, 200
            return {"response": "Showup unmarked successfully."}
        
    except Exception as e:
        return {"response": f"Error: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
