from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/contact'  # Replace with your database credentials
db = SQLAlchemy(app)

class YourData(db.Model):
    __tablename__ = 'feedback'  # Specify the correct table name
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    city = db.Column(db.String(255))
    feedback = db.Column(db.Text)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    if user_input in pt.index:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        print(data)
        return render_template('recommend.html',data=data)
    else:
        error_message = "Sorry, we couldn't find any books matching your input."
        return render_template('recommend.html', error_message=error_message)

@app.route('/contact')  # Define a new route for the "Contact" page
def contact():
    return render_template('contact.html')  # Render the "contact.html" template

@app.route('/contact_submit', methods=['post'])

def contact_submit():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        city = request.form.get('city')
        feedback = request.form.get('feedback')
        # Create a new instance of the YourData model and save it to the database
        new_feedback = YourData(first_name=first_name, last_name=last_name, city=city, feedback=feedback)
        db.session.add(new_feedback)
        db.session.commit()

        return "Thank you for your feedback! Your feedback has been saved."
    
if __name__ == '__main__':
    app.run(debug=True)