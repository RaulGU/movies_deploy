import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

#Autenticación con Firebase
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project=key_dict["project_id"]) #Esta linea jala como tal el project id de secrets.toml, esto me funcionó más que poner el nombre textual, ya que me daba error y no alcanzaba a la colección de la db del ejercicio de práctica, evita estar copiando y pegando

st.title("Netflix App") #Nuestro título principal

#Leer datos de Firestore
def fetch_movies():
    movies_ref = db.collection(u'pelis')
    docs = movies_ref.stream()
    return [doc.to_dict() for doc in docs]

movies_data = fetch_movies()
df = pd.DataFrame(movies_data)

#Mostrar todos los filmes
if st.sidebar.checkbox("Mostrar todos los filmes"):
    st.header("Todos los filmes")
    st.dataframe(df)

#Buscar por título
st.sidebar.markdown("---")
st.sidebar.subheader("Buscar por título") #Agregamos un subtitulo para que se sepa cual es el filtro a usar, igual que con Filtrar por director.
title_search = st.sidebar.text_input("Título contiene:")
if st.sidebar.button("Buscar"):
    filtered = df[df["name"].str.lower().str.contains(title_search.lower())] #Usamos .lower() para pasar todo a minusculas y no importe como fue escrito
    st.subheader(f"{len(filtered)} filmes encontrados:")
    st.dataframe(filtered)

#Filtrar por director
st.sidebar.markdown("---")
st.sidebar.subheader("Filtrar por director")
directors = sorted(df["director"].dropna().unique())
selected_director = st.sidebar.selectbox("Selecciona un director", directors)
if st.sidebar.button("Filtrar por director"):
    directed_films = df[df["director"] == selected_director]
    st.subheader(f"{len(directed_films)} filmes dirigidos por {selected_director}")
    st.dataframe(directed_films)

#Formulario para insertar nuevo filme
#Todos los inputs que están dentro de with serán ejecutados y agregados cuando el form_submit_button "Insertar" sea presionado
#Algo interesante que se investigó es que se pueden poner steps de valores, o sea cada vez que se presiona el + o - se hacen en los saltos especificados en step=
st.sidebar.markdown("---")
st.sidebar.subheader("Agregar nuevo filme")
with st.sidebar.form("form_insertar"):
    name = st.text_input("Nombre")
    director = st.text_input("Director")
    genre = st.text_input("Género")
    year = st.text_input("Año")
    released = st.date_input("Fecha de lanzamiento")
    score = st.number_input("Puntuación", min_value=0.0, max_value=10.0, step=0.1) #Se agregan limites para no sobrepasar el 10.0
    budget = st.number_input("Presupuesto", step=100000)
    runtime = st.number_input("Duración (min)", step=1)
    star = st.text_input("Estrella")
    company = st.text_input("Compañía")
    country = st.text_input("País")
    rating = st.text_input("Clasificación")
    gross = st.number_input("Ganancia", step=100000)
    writer = st.text_input("Guionista")
    votes = st.number_input("Votos", step=100)
    submitted = st.form_submit_button("Insertar")

    if submitted and name: #Al hacer click, submitted es verdadero por lo que a db.collection('pelis') se agregará todo el "doc"
        doc = {
            "name": name,
            "director": director,
            "genre": genre,
            "year": str(year),
            "released": released.isoformat(),
            "score": score,
            "budget": budget,
            "runtime": runtime,
            "star": star,
            "company": company,
            "country": country,
            "rating": rating,
            "gross": gross,
            "writer": writer,
            "votes": votes
        }
        db.collection("pelis").add(doc)
        st.sidebar.success("Filme insertado correctamente")
