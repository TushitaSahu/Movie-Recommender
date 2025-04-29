import pickle
import streamlit as st
import requests
import pandas as pd
import os

# ----------------------------------
# Hugging Face Download Helper
# ----------------------------------
def download_file(url, destination):
    response = requests.get(url)
    response.raise_for_status()  # Raise error if download fails
    with open(destination, "wb") as f:
        f.write(response.content)

# ----------------------------------
# Load Data with Caching
# ----------------------------------
@st.cache_resource
def load_data():
    # Correct Hugging Face URLs (use 'resolve/main' to get raw file URL)
    MOVIES_DICT_URL = "https://huggingface.co/datasets/tushitasahu/movies_dict.pkl/resolve/main/movies_dict.pkl"
    SIMILARITY_URL = "https://huggingface.co/datasets/tushitasahu/movies_dict.pkl/resolve/main/similarity.pkl"

    # Download files if they do not exist
    if not os.path.exists("movies_dict.pkl"):
        download_file(MOVIES_DICT_URL, "movies_dict.pkl")
    if not os.path.exists("similarity.pkl"):
        download_file(SIMILARITY_URL, "similarity.pkl")

    # Load the .pkl files into memory
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
    # Load the movie data and similarity matrix
    movies, similarity = load_data()

    # Create a dropdown list for movie selection
    movie_list = movies['title'].values
    selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

    # Show recommendations when the button is pressed
    if st.button('🔍 Show Recommendation'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])

except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
