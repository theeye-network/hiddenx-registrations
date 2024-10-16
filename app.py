from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient(
    'mongodb+srv://theeye:test@eyecommunity.48uzc.mongodb.net/?retryWrites=true&w=majority&appName=eyeCommunity', 
    server_api=ServerApi('1')
)
db = client['eyeCommunity']
hiddenXregs = db['hiddenXregs']

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
        
        # Store the data in MongoDB
        hiddenXregs.insert_one({
            'name': name,
            'roll_number': roll_number,
            'email': email,
            'experience': experience,
            'phone': phone,
            'stream': stream
        })

        return {"response":"Done."}

    return render_template('regPage.html')

@app.route('/registrations')
def registrations():
    applicants = [i for i in list(hiddenXregs.find()) if i.get("name")]
    print(applicants)
    return render_template('registrations.html', applicants=applicants)

if __name__ == '__main__':
    app.run(debug=True)
