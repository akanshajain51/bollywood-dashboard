import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bollywood Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    actor = pd.read_csv("BollywoodActorRanking.csv")
    director = pd.read_csv("BollywoodDirectorRanking.csv")
    movie = pd.read_csv("BollywoodMovieDetail.csv")
    return actor, director, movie

actor, director, movie = load_data()

st.title("🎬 Bollywood Analytics Dashboard")

# ---------------- Sidebar Filters ----------------
st.sidebar.header("🔍 Filters")

# Year filter
year_range = st.sidebar.slider(
    "Select Year Range",
    int(movie['releaseYear'].min()),
    int(movie['releaseYear'].max()),
    (2000, 2015)
)

# Genre filter
movie['genre_clean'] = movie['genre'].dropna().str.split('|')
all_genres = sorted(list(set([g.strip() for sublist in movie['genre_clean'].dropna() for g in sublist])))
selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + all_genres)

# Actor search
actor_search = st.sidebar.text_input("Search Actor")

# ---------------- Filter Data ----------------
filtered_movies = movie[
    (movie['releaseYear'] >= year_range[0]) &
    (movie['releaseYear'] <= year_range[1])
]

if selected_genre != "All":
    filtered_movies = filtered_movies[
        filtered_movies['genre'].str.contains(selected_genre, na=False)
    ]

# ---------------- KPIs ----------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎥 Movies", len(filtered_movies))
col2.metric("👤 Actors", len(actor))
col3.metric("🎬 Directors", len(director))
col4.metric("⭐ Avg Rating", round(actor['normalizedRating'].mean(), 2))

# ---------------- Charts Row 1 ----------------
colA, colB = st.columns(2)

# Top Actors
with colA:
    st.subheader("👤 Top Actors")
    top_actors = actor.sort_values(by="normalizedRating", ascending=False).head(10)

    if actor_search:
        top_actors = actor[actor['actorName'].str.contains(actor_search, case=False)]

    fig, ax = plt.subplots()
    ax.barh(top_actors['actorName'], top_actors['normalizedRating'])
    ax.invert_yaxis()
    st.pyplot(fig)

# Top Directors
with colB:
    st.subheader("🎬 Top Directors")
    top_directors = director.sort_values(by="normalizedRating", ascending=False).head(10)

    fig, ax = plt.subplots()
    ax.barh(top_directors['directorName'], top_directors['normalizedRating'])
    ax.invert_yaxis()
    st.pyplot(fig)

# ---------------- Charts Row 2 ----------------
colC, colD = st.columns(2)

# Movies by Year
with colC:
    st.subheader("📅 Movies by Year")
    movies_per_year = filtered_movies['releaseYear'].value_counts().sort_index()

    fig, ax = plt.subplots()
    ax.plot(movies_per_year.index, movies_per_year.values)
    st.pyplot(fig)

# Genre Breakdown
with colD:
    st.subheader("🎭 Genre Breakdown")
    genre_data = filtered_movies['genre'].dropna().str.split('|').explode()
    genre_count = genre_data.value_counts().head(10)

    fig, ax = plt.subplots()
    ax.pie(genre_count.values, labels=genre_count.index, autopct='%1.1f%%')
    st.pyplot(fig)

# ---------------- Hit vs Flop ----------------
st.subheader("🔥 Hit vs Flop")

hitflop_count = filtered_movies['hitFlop'].value_counts()

fig, ax = plt.subplots()
ax.bar(hitflop_count.index.astype(str), hitflop_count.values)
st.pyplot(fig)

# ---------------- Movie Explorer ----------------
st.subheader("📋 Movie Explorer")

st.dataframe(filtered_movies[['title', 'releaseYear', 'genre', 'hitFlop']])
