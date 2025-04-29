import pickle
import streamlit as st
import requests
import pandas as pd
import os

# ----------------------------------
# Google Drive Download Fix
# ----------------------------------
def download_file_from_google_drive(file_id, destination):
    session = requests.Session()
    URL = "https://docs.google.com/uc?export=download"

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# ----------------------------------
# Load Data with Caching
# ----------------------------------
@st.cache_resource
def load_data():
    MOVIES_DICT_ID = "1-76kvs2fIBv32kiwy6uxZMxH2gOiqNav"      # Replace with your file ID
    SIMILARITY_ID = "eLFj2e5nmqGKjJ5Kq49"       # Replace with your file ID

    if not os.path.exists("movies_dict.pkl"):
        download_file_from_google_drive(MOVIES_DICT_ID, "movies_dict.pkl")
    if not os.path.exists("similarity.pkl"):
        download_file_from_google_drive(SIMILARITY_ID, "similarity.pkl")

    with open("movies_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)

    return pd.DataFrame(movies_dict), similarity

# ----------------------------------
# Recommender Functions
# ----------------------------------
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

# ----------------------------------
# Streamlit UI
# ----------------------------------
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
    st.error(f"❌ Failed to load data: {e}")
