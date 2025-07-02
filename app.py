import streamlit as st
import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import folium
import base64
from folium.plugins import Fullscreen, MiniMap
from folium.plugins import Draw
from streamlit_folium import st_folium
from datetime import datetime
import io
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Visualisasi Data Gempa Bumi",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS untuk memperbaiki layout
st.markdown("""
<style>
    /* Perbaiki tinggi dan margin peta */
    .folium-map {
        height: 400px !important;
        margin-bottom: 0 !important;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }

    /* Kurangi space antara komponen */
    .stFolium {
        margin-bottom: 0 !important;
    }
    
    .stDataFrame {
        margin-top: 10px !important;
    }
    
    /* Atur ulang padding container utama */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Background dan layout dasar */
    body, .stApp {
        min-height: 100vh !important;
        background-color: #f0f2f6 !important;
    }
    
    /* Header styling */
    .header {
        background-color: #2c3e50;
        color: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Efek hover untuk navigasi */
    .nav-link:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Perbaiki tampilan filter panel */
    .st-expander {
        background-color: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Hilangkan attribution Leaflet */
    .leaflet-control-attribution {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk load data
@st.cache_data
def load_data():
    gdf = gpd.read_file("./data/indo.geojson")
    gdf['mag'] = pd.to_numeric(gdf['mag'], errors='coerce')
    gdf['depth'] = pd.to_numeric(gdf['depth'], errors='coerce')
    gdf['time'] = gdf['time'].apply(str)
    gdf['time'] = pd.to_datetime(gdf['time'], utc=True)
    gdf['time_wib'] = gdf['time'].dt.tz_convert('Asia/Jakarta')
    gdf['time'] = gdf['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    gdf['time_wib'] = gdf['time_wib'].dt.strftime('%Y-%m-%d %H:%M:%S')
    gdf['year'] = pd.to_datetime(gdf['time_wib']).dt.year
    return gdf

gdf = load_data()

# Header dengan background image
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

image_path = "./image/peta.jpg"
image_base64 = get_image_as_base64(image_path)

st.markdown(f"""
<style>
.header {{
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpg;base64,{image_base64}");
    background-size: cover;
    background-position: center;
    padding: 50px 20px;
    margin-bottom: 1rem;
    text-align: center;
}}
</style>

<div class="header">
    <h1 style="color:white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Visualisasi Data Gempa Bumi</h1>
    <p style="color:rgba(255,255,255,0.9);">Data kejadian gempa bumi di wilayah Pulau Jawa dan Sumatera</p>
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px;">
        <a href="#peta" style="padding:8px 20px; background-color:rgba(255,255,255,0.2); color:white; border-radius:20px; text-decoration:none;">Peta</a>
        <a href="#statistik" style="padding:8px 20px; background-color:rgba(255,255,255,0.2); color:white; border-radius:20px; text-decoration:none;">Statistik</a>
        <a href="#tabel" style="padding:8px 20px; background-color:rgba(255,255,255,0.2); color:white; border-radius:20px; text-decoration:none;">Tabel</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Filter panel
with st.expander("🔍 Filter Data", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_filter = st.selectbox(
            "Tahun",
            options=sorted(gdf['year'].unique(), reverse=True),
            index=0
        )
    
    with col2:
        mag_range = st.slider(
            "Magnitudo",
            min_value=float(gdf['mag'].min()),
            max_value=float(gdf['mag'].max()),
            value=(float(gdf['mag'].min()), float(gdf['mag'].max())),
            step=0.1
        )
    
    with col3:
        depth_range = st.slider(
            "Kedalaman (km)",
            min_value=int(gdf['depth'].min()),
            max_value=int(gdf['depth'].max()),
            value=(int(gdf['depth'].min()), int(gdf['depth'].max()))
        )

    st.subheader("Filter Koordinat")
    col_lat, col_lon = st.columns(2)
    
    with col_lat:
        lat_range = st.slider(
            "Latitude (LS)",
            min_value=float(gdf['latitude'].min()),
            max_value=float(gdf['latitude'].max()),
            value=(float(gdf['latitude'].min()), float(gdf['latitude'].max())),
            step=0.1
        )
    
    with col_lon:
        lon_range = st.slider(
            "Longitude (BT)",
            min_value=float(gdf['longitude'].min()),
            max_value=float(gdf['longitude'].max()),
            value=(float(gdf['longitude'].min()), float(gdf['longitude'].max())),
            step=0.1
        )

# Apply filters
filtered_gdf = gdf[
    (gdf['year'] == year_filter) &
    (gdf['mag'] >= mag_range[0]) & 
    (gdf['mag'] <= mag_range[1]) &
    (gdf['depth'] >= depth_range[0]) & 
    (gdf['depth'] <= depth_range[1]) &
    (gdf['latitude'] >= lat_range[0]) & 
    (gdf['latitude'] <= lat_range[1]) &
    (gdf['longitude'] >= lon_range[0]) &  
    (gdf['longitude'] <= lon_range[1])
]

# Fungsi untuk membuat peta
def create_map(data):
    m = folium.Map(
        location=[-2.54, 110.7126],
        zoom_start=6,
        control_scale=True,
        attribution_control=False  # Nonaktifkan attribution default
    )

    # Tambahkan base maps
    tiles = {
        'Satelit': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'Topografi': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
    }
    
    for name, url in tiles.items():
        folium.TileLayer(url, attr=name, name=name).add_to(m)

    # Tambahkan layer megathrust
    try:
        megathrust = gpd.read_file("./data/megathrust/megathrust.shp")
        folium.GeoJson(
            megathrust.to_json(),
            name='Zona Megathrust',
            style_function=lambda x: {'color': 'red', 'weight': 3, 'fillOpacity': 0.1},
            tooltip=folium.GeoJsonTooltip(fields=['Name'], aliases=['Nama Zona: '])
        ).add_to(m)
    except Exception as e:
        st.warning(f"Tidak dapat memuat data megathrust: {e}")

    # Tambahkan layer patahan
    try:
        patahan = gpd.read_file("./data/patahan/patahan.shp")
        folium.GeoJson(
            patahan.to_json(),
            name='Zona Patahan',
            style_function=lambda x: {'color': 'blue', 'weight': 2, 'dashArray': '5, 5', 'fillOpacity': 0.1},
            tooltip=folium.GeoJsonTooltip(fields=['Name'], aliases=['Nama Patahan: '])
        ).add_to(m)
    except Exception as e:
        st.warning(f"Tidak dapat memuat data patahan: {e}")

    # Kontrol layer dan plugin
    folium.LayerControl().add_to(m)
    Fullscreen().add_to(m)
    MiniMap().add_to(m)
    
    # Tambahkan marker gempa
    cmap = plt.get_cmap('gist_rainbow')
    norm = plt.Normalize(20, 100)
    
    for _, eq in data.iterrows():
        rgba = cmap(norm(eq['depth']))
        color = f'#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}'
        
        size = int(5 + (15 * ((eq['mag'] - gdf['mag'].min()) / (gdf['mag'].max() - gdf['mag'].min())))
        
        popup_content = f"""
        <div style="font-family:Arial; font-size:13px; line-height:1.5;">
            <div style="background-color:#d4edda; color:#155724; padding:4px 8px; border-radius:6px; font-weight:bold;">
                Data Gempa
            </div>
            <div style="margin-top:8px; color:#6c757d;">{eq['time_wib']} WIB</div>
            <div style="margin-top:8px; font-size:15px; font-weight:bold;">
                Pusat gempa di {eq['place']}
            </div>
            <div style="margin-top:12px; padding:8px; background:#f8f9fa; border-radius:10px;">
                <div style="display:flex; justify-content:space-between;">
                    <div>🔴 <b>Magnitudo:</b></div>
                    <div><b>{eq['mag']}</b></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;">
                    <div>🟢 <b>Kedalaman:</b></div>
                    <div><b>{int(eq['depth'])} km</b></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;">
                    <div>📍 <b>Lokasi:</b></div>
                    <div><b>{round(eq['latitude'], 2)} LS - {round(eq['longitude'], 2)} BT</b></div>
                </div>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[eq['latitude'], eq['longitude']],
            radius=size,
            color='black',
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)
    
    return m

# Tampilkan peta
st.markdown("### 🌍 Peta Interaktif Kejadian Gempa Bumi")
map_obj = create_map(filtered_gdf)
st_folium(
    map_obj, 
    width=700,
    height=400,  # Tinggi peta yang optimal
    use_container_width=True
)

# Tampilkan tabel data
st.markdown("### 📊 Data Gempa")
st.dataframe(
    filtered_gdf[['time_wib', 'mag', 'depth', 'place', 'latitude', 'longitude']]
    .rename(columns={
        'time_wib': 'Waktu (WIB)',
        'mag': 'Magnitudo',
        'depth': 'Kedalaman (km)',
        'place': 'Lokasi',
        'latitude': 'Lintang',
        'longitude': 'Bujur'
    }),
    use_container_width=True,
    height=400  # Tinggi tabel yang optimal
)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; color: #6c757d; font-size: 12px; margin-top: 2rem;">
    <p>© 2024 Visualisasi Data Gempa Bumi | Sumber Data: BMKG</p>
</div>
""", unsafe_allow_html=True)