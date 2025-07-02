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

# Set page
st.set_page_config(
    page_title="Visualisasi Data Gempa Bumi",
    page_icon="🌍",
    layout="wide"
)

# CSS untuk display
st.markdown("""
<style>
    /* Background utama */
    body {
        background-color: #f0f2f6 !important;
    }
    
    /* Aplikasi Streamlit */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Container utama */
    .main .block-container {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Header */
    .header {
        background-color: #2c3e50;
        color: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    
    /* Navbar */
    .navbar {
        background-color: #34495e !important;
    }
    
    /* Filter panel */
    .st-expander {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Tabel data */
    .stDataFrame {
        background-color: white;
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        background-color: #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Data
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

# Header
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

image_path = "./image/peta.JPG"
image_base64 = get_image_as_base64(image_path)

st.markdown(f"""
<style>
.header {{
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpg;base64,{image_base64}");
    background-size: cover;
    background-position: center;
    padding: 50px 20px;
    margin-bottom: 10px;  /* Mengurangi margin bawah */
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}}
.header-title {{
    color: white !important;
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
.header-subtitle {{
    color: rgba(255,255,255,0.9);
    font-size: 1.1em;
    margin-bottom: 5px;
}}
.nav-menu {{
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-top: 20px;
    margin-bottom: 20px;
}}
.nav-link {{
    padding: 8px 20px;
    background-color: rgba(255,255,255,0.2);
    color: white;
    border-radius: 20px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.3);
}}
.nav-link:hover {{
    background-color: rgba(255,255,255,0.3);
    transform: translateY(-2px);
}}
</style>

<div class="header">
    <h1 class="header-title">Visualisasi Data Gempa Bumi</h1>
    <p class="header-subtitle">
        Data kejadian gempa bumi di wilayah Pulau Jawa dan Sumatera
    </p>
    <div class="nav-menu">
        <a href="#peta" class="nav-link">Peta</a>
        <a href="#statistik" class="nav-link">Statistik</a>
        <a href="#tabel" class="nav-link">Tabel</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Tambahkan anchor points di setiap bagian
st.markdown('<div id="peta"></div>', unsafe_allow_html=True)
# Konten peta di sini...

st.markdown('<div id="statistik"></div>', unsafe_allow_html=True) 
# Konten statistik di sini...

st.markdown('<div id="tabel"></div>', unsafe_allow_html=True)
# Konten tabel di sini...


# Deskripsi 
col_desc, col_stats = st.columns([2, 1])

with col_desc:
    st.markdown("""
    <div style="
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: justify;
    ">
    <p>
    Indonesia merupakan negara yang berada di kawasan <strong>Cincin Api Pasifik
                </strong>, yang juga dikenal sebagai salah satu zona tektonik paling aktif di dunia. Di wilayah ini, tiga lempeng utama dunia yaitu 
                <em>Lempeng Indo Australia</em>, <em>Lempeng Eurasia</em>, dan 
                <em>Lempeng Pasifik</em> yang saling bertemu dan berinteraksi. Pertemuan dan pergeseran antar lempeng ini memicu terjadinya aktivitas geologi yang sangat intens, terutama gempa bumi dan pergerakan sesar.
    </p>
    <p>
    Dari sekian banyak wilayah di Indonesia, 
                <strong>Pulau Jawa</strong> dan 
                <strong>Pulau Sumatera</strong> merupakan dua kawasan yang secara geologis paling rawan terhadap bencana gempa bumi. 
                Hal ini disebabkan oleh letaknya yang berdekatan langsung dengan zona subduksi (<em>megathrust</em>) yang memanjang dari barat Sumatera hingga ke selatan Jawa. 
                Zona ini merupakan batas tumbukan antara Lempeng Indo-Australia yang menyusup ke bawah Lempeng Eurasia, 
                menghasilkan akumulasi energi tektonik yang sewaktu-waktu dapat dilepaskan dalam bentuk gempa bumi besar.
    </p>
    <p>
    Tak hanya zona megathrust, kedua pulau ini juga dipotong oleh berbagai <strong>sesar aktif</strong>, 
                seperti <em>Sesar Sumatera</em> yang memanjang dari utara ke selatan Pulau Sumatera, 
                serta berbagai sesar lokal di Pulau Jawa bagian barat, tengah, dan timur. 
                Aktivitas sesar ini berkontribusi besar terhadap frekuensi dan intensitas gempa yang terjadi di daratan. 
                Gempa-gempa yang bersumber dari sesar aktif cenderung terjadi di kedalaman yang dangkal, 
                sehingga memiliki daya rusak tinggi terhadap permukiman dan infrastruktur.
    </p>
    <p>
    Kondisi tersebut semakin kompleks karena 
                <strong>Jawa</strong> dan 
                <strong>Sumatera</strong> merupakan pusat populasi dan ekonomi nasional. 
                Pulau Jawa merupakan pulau terpadat di Indonesia, dengan konsentrasi pemukiman, infrastruktur, kawasan industri, pendidikan, dan pemerintahan. 
                Sementara itu, Pulau Sumatera memiliki peran penting dalam sektor pertanian, perkebunan, logistik, dan energi. 
                Kepadatan penduduk dan nilai aset yang tinggi di kedua pulau ini menyebabkan risiko bencana menjadi sangat besar, 
                karena gempa bumi yang terjadi dapat menimbulkan kerugian material, korban jiwa, dan disrupsi sosial dalam skala luas.
    </p>
    </div>
    """, unsafe_allow_html=True)


with col_stats:
    # Barchart
    st.markdown("""
    <div style="
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    ">
        <h5 style="
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1rem;
            color: #2c3e50;
        ">Jumlah Gempa per Tahun</h5>
    """, unsafe_allow_html=True)
    
    # Hitung statistik
    gempa_per_tahun = gdf['year'].value_counts().sort_index()
    
    # Buat barchart dengan tinggi yang disesuaikan
    chart_data = gempa_per_tahun.reset_index()
    chart_data.columns = ['Tahun', 'Jumlah']
    
    # Atur tinggi chart agar sejajar dengan teks
    st.bar_chart(
        chart_data.set_index('Tahun'), 
        height=290,
        use_container_width=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Metric box
    st.markdown(f"""
    <style>
        .side-metric {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #e74c3c;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .side-title {{
            font-size: 0.8rem;
            color: #7f8c8d;
            margin-bottom: 4px;
        }}
        .side-value {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #2c3e50;
        }}
        .side-subtext {{
            font-size: 0.75rem;
            color: #e74c3c;
        }}
    </style>
    
    <div class="side-metric">
        <div class="side-title">Total Kejadian</div>
        <div class="side-value">{len(gdf):,}</div>
        <div class="side-subtext">5 tahun terakhir</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Filter panel
with st.expander("Filter Data", expanded=False):
    col1, col2, col3, = st.columns(3)
    
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
#Filter Latitude dan Longitude
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

# Membuat Peta
def create_map(data):
    m = folium.Map(
        location=[-2.54, 110.7126], 
        zoom_start=6) 

    # Tambahkan beberapa base map
    tiles = {
        'Satelit (Esri World Imagery)': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'Topografi (Esri World Topo)': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
    }
    
    for name, url in tiles.items():
        folium.TileLayer(url, attr=name, name=name).add_to(m)

# Tambahkan layer megathrust dari shapefile
    try:
        megathrust = gpd.read_file("./data/megathrust/megathrust.shp")
        folium.GeoJson(
        megathrust.to_json(),
        name='Zona Megathrust',
        style_function=lambda x: {
        'color': 'red',
        'weight': 3,
        'fillOpacity': 0.1
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['Name'],
        aliases=['Nama Zona: '],
        localize=True
    )
).add_to(m)
    except Exception as e:
        st.warning(f"Tidak dapat memuat data megathrust: {e}")

    # Tambahkan layer patahan
    try:
        patahan = gpd.read_file("./data/patahan/patahan.shp")
        folium.GeoJson(
        patahan.to_json(),
        name='Zona Patahan',
        style_function=lambda x: {
        'color': 'blue',
        'weight': 2,
        'dashArray': '5, 5',
        'fillOpacity': 0.1
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['Name'],
        aliases=['Nama Patahan: '],
        localize=True
    )
).add_to(m)
    except Exception as e:
        st.warning(f"Tidak dapat memuat data patahan: {e}")

    # Layer Control
    folium.LayerControl().add_to(m)

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
        
        # Popup
        popup_content = f"""
        <div style="font-family:Arial, sans-serif; font-size:13px; line-height:1.5;">
            <div style="background-color:#d4edda; color:#155724; padding:4px 8px; border-radius:6px; display:inline-block; font-weight:bold;">
                Data Gempa
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
    return m

# Display the map
st.markdown("### Peta Interaktif Kejadian Gempa Bumi", unsafe_allow_html=True)
map_obj = create_map(filtered_gdf)
st_folium(
    map_obj, 
    width=400,
    height=600,  
    use_container_width=True
)

# Menampilkan tabel data
st.markdown("""
<style>
    /* Styling header tabel */
    .data-table-container .stDataFrame thead tr th {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    
    /* Styling baris tabel */
    .data-table-container .stDataFrame tbody tr {
        background-color: #f8f9fa;
    }
    
    /* Efek hover pada baris */
    .data-table-container .stDataFrame tbody tr:hover {
        background-color: #e9ecef !important;
    }
</style>
""", unsafe_allow_html=True)

# Menampilkan tabel data dengan container
with st.container():
    st.markdown('<div class="data-table-container">', unsafe_allow_html=True)
    
    st.subheader("Data Gempa")
    st.dataframe(
        filtered_gdf[['time', 'mag', 'depth', 'place']].rename(columns={
            'time': 'Waktu',
            'mag': 'Magnitudo',
            'depth': 'Kedalaman (km)',
            'place': 'Lokasi'
        }),
        use_container_width=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px;">
    <p>Data gempa bumi wilayah Pulau Jawa dan Sumatera</p>
    <p>© 2025 Visualisasi Data Gempa Bumi</p>
</div>
""", unsafe_allow_html=True)