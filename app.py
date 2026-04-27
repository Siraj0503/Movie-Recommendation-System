import streamlit as st
import pickle
import requests

import os
import gdown

if not os.path.exists("similarity.pkl"):
    url = "https://drive.google.com/uc?id=19vPQWucD4Z9c0txH6rlS-LLCGDKV8Egh"
    gdown.download(url, "similarity.pkl", quiet=False)

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommendation System")
st.caption("Pick a movie and discover similar ones instantly.")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
    color: white;
}
h1, h2, h3, h4, h5 {
    color: white;
}
.poster-card {
    overflow: hidden;
    border-radius: 12px;
    background-color: rgba(255,255,255,0.05);
    padding: 5px;
    backdrop-filter: blur(10px);
}
.poster-card img {
    transition: transform 0.3s ease;
    border-radius: 10px;
}
.poster-card:hover img {
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    api_key = "2b053bed81a453a65143d91428ddd9f7"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except:
        return None


@st.cache_data(show_spinner=False)
def fetch_details(movie_id):
    api_key = "2b053bed81a453a65143d91428ddd9f7"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "overview": data.get("overview", "No description available"),
            "rating": data.get("vote_average", "N/A"),
            "release_date": data.get("release_date", "N/A")
        }
    except:
        return None


movies = pickle.load(open('movies.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_titles = movies['title'].values


@st.cache_data(show_spinner=False)
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


selected_movie = st.selectbox("Select a movie", movie_titles)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie)

    st.subheader("Top Picks For You")

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.markdown(f"**{names[i]}**")

            if posters[i]:
                st.markdown(f"""
                <div class="poster-card">
                    <img src="{posters[i]}" style="height:360px; width:100%; object-fit:cover;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(
                    """
                    <div style='
                        height:360px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        border-radius:10px;
                        background-color:#2c2c2c;
                        font-weight:bold;
                        color:#aaa;
                        text-align:center;
                    '>
                        Poster Not Available
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            movie_id = movies[movies['title'] == names[i]].iloc[0].movie_id

            with st.expander("More Info"):
                details = fetch_details(movie_id)

                if details:
                    st.write(f"⭐ {details['rating']}")
                    st.write(f"📅 {details['release_date']}")
                    st.write(details['overview'])
                else:
                    st.write("No details available")