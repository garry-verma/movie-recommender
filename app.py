import streamlit as st
import pickle
import requests
import random
import gdown

# Google Drive File ID
file_id = "11ZFwKOoZ9Tvh3vHYcOJGjy3nm1Y8snpB"
url = f"https://drive.google.com/uc?id={file_id}"

# Download the file
output = "similarity2.pkl"
gdown.download(url, output, quiet=False)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return "https://via.placeholder.com/200x300?text=No+Image"
    data = response.json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/200x300?text=No+Image"

movies = pickle.load(open("movies_list2.pkl", 'rb'))
similarity = pickle.load(open("similarity2.pkl", 'rb'))
movies_list = movies['original_title'].values

# Display header and random movie posters
st.header("🎬 Movie Recommender System")
st.subheader("Discover movies similar to your favorites!")


sampled_movie_ids = random.sample(list(movies['id'].values), 10)
image_urls = [fetch_poster(movie_id) for movie_id in sampled_movie_ids]


cols = st.columns(10) 

image_width = 150  

for i, (image_url, movie_id) in enumerate(zip(image_urls, sampled_movie_ids)):
    movie_url = f"https://www.themoviedb.org/movie/{movie_id}"  
    
    with cols[i]:
        
        st.markdown(f'<a href="{movie_url}" target="_blank"><img src="{image_url}" width="{image_width}"></a>', unsafe_allow_html=True)
selected_movie = st.selectbox("Select a movie", movies_list)

def recommend(movie):
    try:
        index = movies[movies['original_title'] == movie].index[0]
    except IndexError:
        return [], [], []
    
    distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
    recommended_movies, recommended_posters, recommended_urls = [], [], []
    
    for i in distances[1:11]:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].original_title)
        
        # Construct the movie URL using the movie_id
        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
        recommended_urls.append(movie_url)
        
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters, recommended_urls


if st.button("Show Recommendations"):
    movie_names, movie_posters, movie_urls = recommend(selected_movie)
    
    if movie_names:
        cols = st.columns(5)
        for i, (name, poster, url) in enumerate(zip(movie_names, movie_posters, movie_urls)):
            with cols[i % 5]:
                st.markdown(f'<a href="{url}" target="_blank"><img src="{poster}" width="{250}"></a>', unsafe_allow_html=True)
                st.markdown(name)
    else:
        st.error("No recommendations found. Try another movie!")
