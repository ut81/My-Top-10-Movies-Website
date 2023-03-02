from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOURSECRETKEY'
Bootstrap(app)


## API REQUIREDMENTS
APIKEY="YOUR API KEY"
APIURL="https://api.themoviedb.org/3/search/movie"

###FIND MOVIES REQUIREMENT
movie_find_url="https://api.themoviedb.org/3/movie"
movie_img_url="https://image.tmdb.org/t/p/original"





app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float,nullable=True)
    ranking=db.Column(db.Integer,nullable=True)
    review=db.Column(db.String(250),nullable=True)
    img_url=db.Column(db.String(250),nullable=False)
    #Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'
    
with app.app_context():

    db.create_all()


class Ratemovie(FlaskForm):
    rating=StringField(label="Your rating out of 10 e.g. 7",validators=[DataRequired()])
    review=StringField(label="Your review",validators=[DataRequired()])
    submit = SubmitField("Done")

class Addmovie(FlaskForm):
    title=StringField(label="Movie Title",validators=[DataRequired()])

    submit=SubmitField(label="Add")




@app.route("/")
def home():
    all_movies=Movie.query.order_by(Movie.rating).all()
    #This line loops through all the movies
    for i in range(len(all_movies)):
        #This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()



    return render_template("index.html",movies=all_movies)


@app.route('/edit',methods=['GET','POST'])
def edit():
    form=Ratemovie()
    movie_id=request.args.get('id')
    movie=Movie.query.get(movie_id)
    if request.method=='POST':

        if form.validate_on_submit:
            movie.rating=float(form.rating.data)
            movie.review=form.review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("edit.html",movie=movie,form=form)

@app.route('/delete')
def delete_movie():
    movie_id=request.args.get("id")
    movie=Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))
    

@app.route('/add',methods=['GET','POST'])
def add_movie():
    form =Addmovie()
    
    if request.method=='POST':
        if form.validate_on_submit:
            movie_title=form.title.data
            params={
                "api_key":APIKEY,
                "query":movie_title
            }
            response=requests.get(url=APIURL,params=params)
            data=response.json()['results']
            return render_template("select.html",options=data)

    return render_template("add.html",form=form)


@app.route('/find')
def find():
    movie_id=request.args.get('id')
    response=requests.get(url=f"{movie_find_url}/{movie_id}",params={"api_key":APIKEY})
    data=response.json()
    movie_title=data['title']
    movie_year=data['release_date'].split("-")[0]
    movie_description=data['overview']
    movie_img=f"{movie_img_url}/{data['poster_path']}"
    with app.app_context():
        
        new_movie=Movie(
            title=movie_title,
            year=movie_year,
            description=movie_description,
            img_url=movie_img
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit',id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
