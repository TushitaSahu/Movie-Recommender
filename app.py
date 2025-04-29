import pickle
import streamlit as st
import requests
import pandas as pd
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

# Define a temporary directory to save files
temp_dir = "temp_files"
os.makedirs(temp_dir, exist_ok=True)

# Check if both files are uploaded
if movies_dict_file is not None and similarity_file is not None:
    # Save the uploaded files to the temporary directory
    movies_dict_path = os.path.join(temp_dir, "movies_dict.pkl")
    similarity_path = os.path.join(temp_dir, "similarity.pkl")

    # Save the movies_dict.pkl file
    with open(movies_dict_path, "wb") as f:
        f.write(movies_dict_file.getbuffer())

    # Save the similarity.pkl file
    with open(similarity_path, "wb") as f:
        f.write(similarity_file.getbuffer())

    st.success("Files successfully uploaded and saved!")

    # Load models (from the saved temporary files)
    with open(movies_dict_path, "rb") as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)

    with open(similarity_path, "rb") as f:
        similarity = pickle.load(f)

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
