from flask import Flask, render_template, request
import pickle
import numpy as np
import requests

# Load book data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# Load movie data
top_movies = pickle.load(open('top_movies.pkl', 'rb'))

# OMDB API key
omdb_api_key = 'cbdaf63f'

app = Flask(__name__)

def get_movie_poster(title):
    try:
        url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&t={title}"
        response = requests.get(url)
        data = response.json()
        if data['Response'] == 'True':
            return data['Poster']
        else:
            return None
    except Exception as e:
        print(f"Error fetching poster for {title}: {e}")
        return None

@app.route('/')
def index():
    # Fetch movie posters
    for movie in top_movies:
        movie['poster'] = get_movie_poster(movie['title'])
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           top_movies=top_movies
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
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

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
