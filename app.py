import pickle
import streamlit as st
import requests
import pandas as pd
import os

# ----------- CONFIG -------------
MOVIES_DICT_URL = "https://drive.google.com/file/d/1-76kvs2fIBv32kiwy6uxZMxH2gOiqNav/view?usp=sharing"
SIMILARITY_URL = "https://drive.google.com/file/d/1EpniYnuErwxDUeLFj2e5nmqGKjJ5Kq49/view?usp=sharing"

# ----------- UTILITIES -------------
@st.cache_resource
def download_file(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)

@st.cache_resource
def load_data():
    # Download only if not already downloaded
    download_file(MOVIES_DICT_URL, "movies_dict.pkl")
    download_file(SIMILARITY_URL, "similarity.pkl")

    # Load files
    with open("movies_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)

    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)

    return pd.DataFrame(movies_dict), similarity

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""

def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

# ----------- STREAMLIT UI -------------
st.header('🎬 Movie Recommender System')

try:
    movies, similarity = load_data()

    movie_list = movies['title'].values
    selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

    if st.button('🔍 Show Recommendation'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])

except Exception as e:
    st.error(f"Failed to load data: {e}")
