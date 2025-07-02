import streamlit as st
import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import folium
from folium.plugins import Fullscreen, MiniMap
from streamlit_folium import st_folium
from datetime import datetime
import io
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Visualisasi Data Gempa Bumi - Pulau Jawa",
    page_icon="🌍",
    layout="wide"
)

# Load data (you'll need to adjust the path)
@st.cache_data
def load_data():
    gdf = gpd.read_file("./data/gempa.geojson")
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

# Header section
st.markdown("""
<div class="header">
    <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">
        <span>Gempa Bumi</span>
    </div>
    <h1 class="header-title">Visualisasi Data Gempa Bumi</h1>
    <p class="header-subtitle">
        Informasi data gempa bumi di wilayah Pulau Jawa
    </p>
</div>
""", unsafe_allow_html=True)

# Description section
st.markdown("""
<p>
Pulau Jawa merupakan salah satu wilayah terpadat dan paling vital di Indonesia, baik dari segi ekonomi, pemerintahan, maupun budaya.
Namun, di balik kepadatan dan kemajuan tersebut, Pulau Jawa menyimpan potensi bencana alam yang besar, khususnya gempa bumi.
Secara geologis, Pulau Jawa terletak di zona tektonik aktif, tepatnya di jalur subduksi antara Lempeng Indo-Australia dan Lempeng Eurasia.
Interaksi antar lempeng ini menyebabkan terjadinya gempa bumi tektonik yang bisa berpusat di laut maupun di daratan.
</p>
<p>
Selain itu, Pulau Jawa juga memiliki sejumlah sesar aktif seperti Sesar Cimandiri dan Sesar Lembang, yang berpotensi memicu gempa di kawasan darat.
Aktivitas gunung berapi di sepanjang jalur Cincin Api Pasifik turut memperbesar kerentanan terhadap gempa vulkanik.
</p>
<p>
Ancaman gempa bumi di Pulau Jawa sangat serius karena bisa menyebabkan kerusakan besar pada infrastruktur, korban jiwa,
hingga potensi tsunami jika gempa terjadi di dasar laut.
Oleh karena itu, upaya mitigasi risiko, pembangunan infrastruktur tahan gempa,
serta peningkatan kesadaran dan kesiapsiagaan masyarakat menjadi hal yang sangat penting untuk meminimalkan dampak bencana ini.
</p>
""", unsafe_allow_html=True)

# Statistics section
st.markdown("### Statistik Gempa Bumi")

col1, = st.columns(1)

with col1:
    # Earthquakes per year
    st.markdown("#### Jumlah Gempa per Tahun")
    statistik_tahunan = gdf['year'].value_counts().sort_index().reset_index()
    statistik_tahunan.columns = ['Tahun', 'Jumlah']
    statistik_tahunan = statistik_tahunan.sort_values("Tahun")
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(statistik_tahunan['Tahun'].astype(str), statistik_tahunan['Jumlah'], color='steelblue')
    ax.set_title("Jumlah Gempa per Tahun", fontsize=12)
    ax.set_xlabel("Tahun", fontsize=10)
    ax.set_ylabel("Jumlah", fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig)

# Interactive map section
st.markdown("### Peta Interaktif Gempa Bumi")

# Filter panel
with st.expander("Filter Data", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        location_options = ['Semua Lokasi'] + sorted(gdf['place'].unique().tolist())
        location_filter = st.selectbox(
            "Lokasi",
            options=location_options,
            index=0
        )

# Apply filters
filtered_gdf = gdf[
    (gdf['year'] == year_filter) &
    (gdf['mag'] >= mag_range[0]) &
    (gdf['mag'] <= mag_range[1]) &
    (gdf['depth'] >= depth_range[0]) &
    (gdf['depth'] <= depth_range[1])
]

if location_filter != 'Semua Lokasi':
    filtered_gdf = filtered_gdf[filtered_gdf['place'] == location_filter]

# Create map
def create_map(data):
    # Center map on Java
    m = folium.Map(
        location=[-7.6145, 110.7126],
        zoom_start=7,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery'
    )
    
    # Add fullscreen control
    Fullscreen().add_to(m)
    
    # Add minimap
    MiniMap().add_to(m)
    
    # Create color gradient for depth
    cmap = plt.get_cmap('gist_rainbow')
    norm = plt.Normalize(20, 100)
    
    for _, eq in data.iterrows():
        # Determine marker color based on depth
        rgba = cmap(norm(eq['depth']))
        color = f'#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}'
        
        # Scale marker size based on magnitude
        min_size = 5
        max_size = 20
        scale = ((eq['mag'] - gdf['mag'].min()) / (gdf['mag'].max() - gdf['mag'].min()))
        size = int(min_size + (max_size - min_size) * scale)
        
        # Create popup content
        popup_content = f"""
        <div style="font-family:Arial, sans-serif; font-size:13px; line-height:1.5;">
            <div style="background-color:#d4edda; color:#155724; padding:4px 8px; border-radius:6px; display:inline-block; font-weight:bold;">
                Gempa Dirasakan
            </div>
            <div style="margin-top:8px; color:#6c757d;">{eq['time_wib']} WIB</div>
            <div style="margin-top:8px; font-size:15px; font-weight:bold; color:#000;">
                Pusat gempa berada di {eq['place']}
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
        
        # Add marker to map
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
    
    # Create legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 80px; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background:white; padding: 5px;
                border-radius:5px;">
        <div style="display: inline-block; 
                    width: 20px; height: 20px; 
                    background: linear-gradient(to right, #0000ff, #ff0000);"></div>
        <span style="vertical-align: top;">Kedalaman (km)</span><br>
        <span style="float: left;">20</span>
        <span style="float: right;">100</span>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# Display the map
st.markdown('<div class="map-container">', unsafe_allow_html=True)
map_obj = create_map(filtered_gdf)
st_folium(map_obj, width=1200, height=600)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px;">
    <p>Data gempa bumi wilayah Pulau Jawa</p>
    <p>© 2023 Visualisasi Data Gempa Bumi</p>
</div>
""", unsafe_allow_html=True)