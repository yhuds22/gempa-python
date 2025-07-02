import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import base64
from folium.plugins import Fullscreen, MiniMap
from streamlit_folium import st_folium

# ==============================================================================
# KONFIGURASI HALAMAN & GAYA (CSS)
# ==============================================================================

# Atur konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Dasbor Gempa Bumi | Jawa & Sumatera",
    page_icon="🌍",
    layout="wide"
)

# Fungsi untuk memuat gambar sebagai base64
def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.warning(f"File gambar tidak ditemukan di: {path}")
        return None

# Muat gambar latar header
image_base64 = get_image_as_base64("./image/peta.JPG")

# CSS Kustom untuk tampilan modern
st.markdown(f"""
<style>
    /* --- FONT & WARNA DASAR --- */
    :root {{
        --primary-color: #1f77b4; /* Biru modern */
        --secondary-color: #2c3e50; /* Abu-abu gelap */
        --background-color: #f0f2f6;
        --card-bg-color: #ffffff;
        --text-color: #333333;
        --light-text-color: #6c757d;
        --border-radius: 12px;
        --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }}

    /* --- BODY & LAYOUT UTAMA --- */
    body {{
        font-family: 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        background-color: var(--background-color);
        color: var(--text-color);
    }}

    .stApp {{
        background-color: var(--background-color);
    }}

    .main .block-container {{
        padding: 1.5rem 2rem;
    }}

    /* --- KARTU (CARD) --- */
    .card {{
        background-color: var(--card-bg-color);
        border-radius: var(--border-radius);
        padding: 25px;
        box-shadow: var(--box-shadow);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }}
    .card:hover {{
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-3px);
    }}

    /* --- HEADER --- */
    .header-container {{
        background-image: linear-gradient(to right, rgba(25, 31, 38, 0.85), rgba(44, 62, 80, 0.85)), url("data:image/jpg;base64,{image_base64 if image_base64 else ''}");
        background-size: cover;
        background-position: center;
        padding: 40px;
        border-radius: var(--border-radius);
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }}
    .header-title {{
        font-size: 3em;
        font-weight: 700;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }}
    .header-subtitle {{
        font-size: 1.2em;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.9);
    }}

    /* --- METRIK & STATISTIK --- */
    .metric-card {{
        text-align: center;
        padding: 20px;
    }}
    .metric-value {{
        font-size: 2.5em;
        font-weight: 700;
        color: var(--primary-color);
    }}
    .metric-label {{
        font-size: 1em;
        color: var(--light-text-color);
        margin-top: -5px;
    }}

    /* --- JUDUL BAGIAN --- */
    .section-header {{
        font-size: 1.8em;
        font-weight: 600;
        color: var(--secondary-color);
        margin-bottom: 15px;
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 8px;
    }}

    /* --- FILTER PANEL --- */
    .st-expander, .st-expander > div {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* --- STYLING TABEL DATA --- */
    .stDataFrame {{
        border: none;
    }}
    .stDataFrame thead th {{
        background-color: var(--primary-color);
        color: white;
        font-size: 16px;
        font-weight: 600;
    }}
    .stDataFrame tbody tr:nth-child(even) {{
        background-color: #f8f9fa;
    }}
    .stDataFrame tbody tr:hover {{
        background-color: #e9ecef;
    }}

    /* --- FOOTER --- */
    .footer {{
        text-align: center;
        padding: 20px;
        color: var(--light-text-color);
        font-size: 0.9em;
        margin-top: 30px;
    }}

</style>
""", unsafe_allow_html=True)


# ==============================================================================
# PEMUATAN DATA (DATA LOADING)
# ==============================================================================

@st.cache_data
def load_data():
    """Memuat dan memproses data gempa dari file GeoJSON."""
    try:
        gdf = gpd.read_file("./data/indo.geojson")
        gdf['mag'] = pd.to_numeric(gdf['mag'], errors='coerce')
        gdf['depth'] = pd.to_numeric(gdf['depth'], errors='coerce')
        gdf['time'] = pd.to_datetime(gdf['time'], utc=True)
        gdf['time_wib'] = gdf['time'].dt.tz_convert('Asia/Jakarta')
        gdf['year'] = gdf['time_wib'].dt.year
        # Hapus baris dengan nilai NaN setelah konversi
        gdf.dropna(subset=['mag', 'depth', 'time_wib'], inplace=True)
        return gdf
    except Exception as e:
        st.error(f"Gagal memuat data: {e}. Pastikan file './data/indo.geojson' ada dan valid.")
        return gpd.GeoDataFrame()

gdf = load_data()

# ==============================================================================
# HEADER
# ==============================================================================

if not gdf.empty:
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">Dasbor Gempa Bumi</h1>
            <p class="header-subtitle">Analisis Interaktif Kejadian Gempa di Wilayah Jawa dan Sumatera</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("Data tidak tersedia untuk ditampilkan. Aplikasi tidak dapat dilanjutkan.")
    st.stop()


# ==============================================================================
# BAGIAN PENDAHULUAN & STATISTIK UTAMA
# ==============================================================================

st.markdown('<div class="card">', unsafe_allow_html=True)
col_desc, col_stats = st.columns([6, 4])

with col_desc:
    st.markdown("""
    <h3 class="section-header">Latar Belakang Geologis</h3>
    <p style="text-align: justify;">
        Indonesia, yang terletak di <strong>Cincin Api Pasifik</strong>, merupakan salah satu zona tektonik paling aktif di dunia. Pertemuan tiga lempeng besar—<em>Lempeng Indo-Australia</em>, <em>Eurasia</em>, dan <em>Pasifik</em>—memicu aktivitas seismik yang intens.
    </p>
    <p style="text-align: justify;">
        <strong>Pulau Jawa</strong> dan <strong>Sumatera</strong> sangat rentan karena berhadapan langsung dengan zona subduksi (<em>megathrust</em>) dan dipotong oleh berbagai sesar aktif seperti <em>Sesar Besar Sumatera</em>. Gempa dangkal yang berasal dari sesar ini berpotensi merusak, sementara gempa dalam di zona subduksi dapat memicu tsunami. Mengingat kedua pulau ini adalah pusat populasi dan ekonomi nasional, pemantauan dan analisis risiko gempa menjadi sangat krusial.
    </p>
    """, unsafe_allow_html=True)

with col_stats:
    # Metrik Utama
    total_gempa = len(gdf)
    mag_tertinggi = gdf['mag'].max()
    gempa_per_tahun = gdf['year'].value_counts().sort_index()

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{total_gempa:,}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Total Kejadian Tercatat</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="metric-card" style="margin-top: 15px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{mag_tertinggi:.1f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Magnitudo Tertinggi</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PANEL FILTER
# ==============================================================================

st.markdown('<div class="card">', unsafe_allow_html=True)
with st.expander("🔍 Buka Panel Filter Data", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter Tahun
        sorted_years = sorted(gdf['year'].unique(), reverse=True)
        year_filter = st.selectbox(
            "Pilih Tahun",
            options=["Semua Tahun"] + sorted_years,
            index=1 # Default ke tahun terbaru
        )

    with col2:
        # Filter Magnitudo
        mag_range = st.slider(
            "Rentang Magnitudo",
            min_value=float(gdf['mag'].min()),
            max_value=float(gdf['mag'].max()),
            value=(float(gdf['mag'].min()), float(gdf['mag'].max())),
            step=0.1
        )

    with col3:
        # Filter Kedalaman
        depth_range = st.slider(
            "Rentang Kedalaman (km)",
            min_value=int(gdf['depth'].min()),
            max_value=int(gdf['depth'].max()),
            value=(int(gdf['depth'].min()), int(gdf['depth'].max()))
        )

# Terapkan filter ke data
if year_filter == "Semua Tahun":
    filtered_gdf = gdf[
        (gdf['mag'] >= mag_range[0]) & (gdf['mag'] <= mag_range[1]) &
        (gdf['depth'] >= depth_range[0]) & (gdf['depth'] <= depth_range[1])
    ]
else:
    filtered_gdf = gdf[
        (gdf['year'] == year_filter) &
        (gdf['mag'] >= mag_range[0]) & (gdf['mag'] <= mag_range[1]) &
        (gdf['depth'] >= depth_range[0]) & (gdf['depth'] <= depth_range[1])
    ]
st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PETA INTERAKTIF
# ==============================================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h3 class="section-header">Peta Sebaran Gempa Bumi</h3>', unsafe_allow_html=True)

def create_map(data):
    """Membuat peta Folium dengan data gempa."""
    m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="CartoDB Positron")

    # Tambahkan base map alternatif
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satelit Esri').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Topografi Esri').add_to(m)

    # Fungsi untuk menambahkan GeoJSON dengan penanganan error
    def add_geojson_layer(file_path, name, style):
        try:
            gdf_layer = gpd.read_file(file_path)
            folium.GeoJson(
                gdf_layer.to_json(),
                name=name,
                style_function=lambda x: style,
                tooltip=folium.GeoJsonTooltip(fields=['Name'], aliases=['Nama:'], localize=True)
            ).add_to(m)
        except Exception as e:
            st.warning(f"Tidak dapat memuat layer '{name}': {e}")
            
    # Tambahkan layer Megathrust dan Patahan
    add_geojson_layer("./data/megathrust/megathrust.shp", 'Zona Megathrust', {'color': '#e74c3c', 'weight': 2.5, 'fillOpacity': 0.1})
    add_geojson_layer("./data/patahan/patahan.shp", 'Sesar Aktif', {'color': '#3498db', 'weight': 1.5, 'dashArray': '5, 5'})
    
    # Colormap untuk kedalaman
    cmap = plt.get_cmap('viridis_r')
    norm = plt.Normalize(vmin=data['depth'].min(), vmax=data['depth'].max())
    
    for _, eq in data.iterrows():
        rgba = cmap(norm(eq['depth']))
        color = f'#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}'
        
        size = 3 + (eq['mag'] ** 2) / 5

        # Popup dengan desain modern
        popup_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; width: 280px;">
            <div style="background-color: {color}; color: white; padding: 10px; border-radius: 8px 8px 0 0;">
                <h4 style="margin:0; font-size: 16px;">
                    <i class="fa fa-info-circle"></i> Detail Gempa
                </h4>
            </div>
            <div style="padding: 12px; background-color: #fff;">
                <p style="margin:0; color:#555;">
                    <i class="fa fa-map-marker"></i> <b>Lokasi:</b> {eq['place']}
                </p>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #eee;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><i class="fa fa-bolt"></i> <b>Magnitudo:</b></span>
                    <span style="font-size: 1.2em; font-weight: bold; color: #d35400;">{eq['mag']:.1f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <span><i class="fa fa-arrow-down"></i> <b>Kedalaman:</b></span>
                    <span style="font-weight: bold;">{int(eq['depth'])} km</span>
                </div>
                <div style="font-size: 0.85em; color: #777; margin-top: 12px; text-align: right;">
                    <i class="fa fa-calendar"></i> {eq['time_wib'].strftime('%d %b %Y, %H:%M WIB')}
                </div>
            </div>
        </div>
        """
        # Ikon Font Awesome (perlu koneksi internet untuk render)
        folium.Marker(
            location=[eq['latitude'], eq['longitude']],
            popup=folium.Popup(folium.Html(popup_html, script=True)),
            icon=folium.Icon(color="black", icon="info-sign"),
        ).add_to(m)

        folium.CircleMarker(
            location=[eq['latitude'], eq['longitude']],
            radius=size,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            weight=1
        ).add_to(m)

    # Tambahkan kontrol
    folium.LayerControl().add_to(m)
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    
    return m

# Tampilkan peta jika ada data yang difilter
if not filtered_gdf.empty:
    # Tambahkan link ke Font Awesome untuk ikon popup
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)
    map_obj = create_map(filtered_gdf)
    st_folium(map_obj, height=500, use_container_width=True)
else:
    st.info("Tidak ada data gempa yang sesuai dengan filter yang Anda pilih.")

st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# GRAFIK DAN TABEL DATA
# ==============================================================================
col_chart, col_table = st.columns(2)

with col_chart:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Tren Gempa Tahunan</h3>', unsafe_allow_html=True)
    if not filtered_gdf.empty:
        gempa_per_bulan = filtered_gdf.copy()
        gempa_per_bulan['bulan'] = gempa_per_bulan['time_wib'].dt.to_period('M')
        monthly_counts = gempa_per_bulan['bulan'].value_counts().sort_index()
        monthly_counts.index = monthly_counts.index.to_timestamp()
        
        st.area_chart(monthly_counts, use_container_width=True)
    else:
        st.info("Data tidak tersedia untuk menampilkan grafik.")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col_table:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Tabel Data Gempa</h3>', unsafe_allow_html=True)
    
    # Tampilkan tabel data
    display_df = filtered_gdf[['time_wib', 'mag', 'depth', 'place']].copy()
    display_df.rename(columns={
        'time_wib': 'Waktu (WIB)',
        'mag': 'Magnitudo',
        'depth': 'Kedalaman (km)',
        'place': 'Lokasi'
    }, inplace=True)
    display_df['Waktu (WIB)'] = display_df['Waktu (WIB)'].dt.strftime('%Y-%m-%d %H:%M')

    st.dataframe(display_df.head(10), use_container_width=True, height=330)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
    <div class="footer">
        <p>Dasbor Analisis Gempa Bumi di Jawa & Sumatera</p>
        <p>&copy; 2025 | Dibuat dengan Streamlit</p>
    </div>
""", unsafe_allow_html=True)