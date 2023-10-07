from flask import Flask , jsonify ,request
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db=SQLAlchemy(app)

class details(db.Model): 
    __tablename__ = 'details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    at=db.Column(db.DateTime, default=db.func.now())
    author=db.Column(db.String(100)) 
    like=db.Column(db.Integer)
    reply=db.Column(db.Integer)
    text=db.Column(db.String(3000))

@app.route('/fetch_data')
def fetch_data():
    api_url = 'https://app.ylytic.com/ylytic/test'
    try:
        response = requests.get(api_url)
        date_format = '%a, %d %b %Y %H:%M:%S %Z'
        if response.status_code == 200:
            data = response.json()
            for row in data["comments"]:       
                at_date = datetime.strptime(row["at"], date_format)
                new_data=details(at=at_date,author=row["author"],like=int(row["like"]),reply=int(row["reply"]),text=row["text"])
                print(new_data)
                db.create_all()
                db.session.add(new_data)
            db.session.commit()
            return jsonify(data)
        else:
            return jsonify({'error': 'Failed to fetch data from the API'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/")
def show():
    data=details.query.all()
    return jsonify({'data': "data Fetched"})
    

@app.route('/search', methods=['GET'])
def search_comments():

    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_from=datetime.strptime(at_from, '%d-%m-%Y')
    at_to = request.args.get('at_to')
    at_to=datetime.strptime(at_to, '%d-%m-%Y')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    query = details.query

    if search_author:
        query = query.filter(details.author.contains(search_author))

    if at_from:
        query = query.filter(details.at >= at_from)

    if at_to:
        query = query.filter(details.at <= at_to)

    if like_from:
        query = query.filter(details.like >= like_from)

    if like_to:
        query = query.filter(details.like <= like_to)

    if reply_from:
        query = query.filter(details.reply >= reply_from)

    if reply_to:
        query = query.filter(details.reply <= reply_to)

    if search_text:
        query = query.filter(details.text.contains(search_text))

    results = query.all()
    comments = []
    print(results)
    for comment in results:
        comments.append({
            'id': comment.id,
            'author': comment.author,
            'at': comment.at,
            'like': comment.like,
            'reply': comment.reply,
            'text': comment.text
        })

    return jsonify({'comments': comments})

if __name__ == '__main__':
    app.run(debug=True)