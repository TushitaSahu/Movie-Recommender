import pickle
import streamlit as st
import requests
import pandas as pd
import os
import zipfile
import os

if not os.path.exists("movies_dict.pkl") or not os.path.exists("similarity.pkl"):
    with zipfile.ZipFile("data.zip", 'r') as zip_ref:
        zip_ref.extractall()
import requests

def download_file(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

if not os.path.exists("movies_dict.pkl"):
    download_file("https://your_link/movies_dict.pkl", "movies_dict.pkl")

if not os.path.exists("similarity.pkl"):
    download_file("https://your_link/similarity.pkl", "similarity.pkl")


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

st.header('🎬 Movie Recommender System')

# ✅ Load models safely
if os.path.exists('movies_dict.pkl') and os.path.exists('similarity.pkl'):
    with open('movies_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)

    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
else:
    st.error("❌ Required files not found: 'movies_dict.pkl' or 'similarity.pkl'. Please upload them or add them to your repo.")
    st.stop()

# UI
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

if st.button('🔍 Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])
