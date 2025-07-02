import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Konfigurasi Halaman
st.set_page_config(
    page_title="Peta Gempa Interaktif",
    page_icon="🌍",
    layout="wide"
)

# Judul Aplikasi
st.title("🌋 Peta Gempa Indonesia")
st.markdown("Visualisasi interaktif gempa bumi berdasarkan magnitudo, kedalaman, dan lokasi.")

# Sidebar untuk Filter
with st.sidebar:
    st.header("⚙️ Filter Data")
    tahun = st.selectbox("Tahun", options=[2020, 2021, 2022, 2023, 2024])
    min_mag = st.slider("Magnitudo Minimum", 3.0, 9.0, 4.0)
    min_depth, max_depth = st.slider("Kedalaman (Km)", 0, 100, (10, 50))

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    gdf = gpd.read_file("./data/gempa.geojson")
    gdf['mag'] = pd.to_numeric(gdf['mag'], errors='coerce')
    gdf['depth'] = pd.to_numeric(gdf['depth'], errors='coerce')
    gdf['time'] = pd.to_datetime(gdf['time'])
    gdf['year'] = gdf['time'].dt.year
    return gdf

# Memuat data
gdf = load_data()

# Filter data berdasarkan input pengguna
filtered_gdf = gdf[
    (gdf['mag'] >= min_mag) &
    (gdf['depth'].between(min_depth, max_depth)) &
    (gdf['year'] == tahun)
]

# Fungsi untuk membuat peta
start_location = (-6.9147, 107.6098)
m = Map(center=start_location, 
        basemap=basemap_to_tiles(basemaps.Esri.WorldImagery),
        zoom=8)
    
    for _, row in data.iterrows():
        popup_text = f"""
        <b>Waktu:</b> {row['time']}<br>
        <b>Magnitudo:</b> {row['mag']}<br>
        <b>Kedalaman:</b> {row['depth']} km<br>
        <b>Lokasi:</b> {row['place']}
        """
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['mag'] * 2,
            color='red',
            fill=True,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)
    return m

# Menampilkan peta
st.subheader("🗺️ Peta Sebaran Gempa")
peta = create_map(filtered_gdf)
folium_static(peta, width=1200, height=600)

# Menampilkan tabel data
st.subheader("📊 Data Gempa Terfilter")
st.dataframe(filtered_gdf[['time', 'mag', 'depth', 'place']])