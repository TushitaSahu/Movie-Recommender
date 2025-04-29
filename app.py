import pickle
import streamlit as st
import requests
import pandas as pd
import gzip
import os

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

# Upload files (pickle files)
movies_dict_file = st.file_uploader("Upload movies_dict.pkl", type="pkl")
similarity_file = st.file_uploader("Upload similarity.pkl", type="pkl")

# Check if both files are uploaded
if movies_dict_file is not None and similarity_file is not None:
    # Load movies_dict
    movies_dict = pickle.load(movies_dict_file)
    movies = pd.DataFrame(movies_dict)

    # Load similarity matrix
    similarity = pickle.load(similarity_file)
    
    st.success("Files successfully uploaded and loaded!")

    # UI for movie recommendation
    movie_list = movies['title'].values
    selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movie_list)

    if st.button('🔍 Show Recommendation'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
else:
    st.warning("Please upload the required files: 'movies_dict.pkl' and 'similarity.pkl'.")
