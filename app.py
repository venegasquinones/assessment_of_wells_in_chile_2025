# ============================================================
# CHILE GROUNDWATER ASSESSMENT - INTERACTIVE DASHBOARD
# Streamlit Application for Data Visualization and Analysis
# ============================================================
# 
# FILE STRUCTURE FOR GITHUB:
# ├── app.py (this file)
# ├── requirements.txt
# ├── .streamlit/
# │   └── config.toml
# ├── data/
# │   ├── Groundwater_Trend_Analysis_Complete.xlsx
# │   ├── Comparacion_Censo2017_vs_Censo2024.xlsx
# │   ├── Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx
# │   ├── niveles_estaticos_pozos_historico.xlsx
# │   ├── FINAL_VALIDOS_En_Chile_ultimo.xlsx
# │   ├── Censo_2017_pozos_5_meters.xlsx
# │   ├── Censo_2024_pozos_5_meters.xlsx
# │   └── shapefiles/ (optional, can use online sources)
# └── README.md
#
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap
import json
import os
from datetime import datetime
from scipy import stats

# ============================================================
# TRANSLATION DICTIONARY
# ============================================================
TRANS = {
    'page_title': {
        'es': 'Evaluación de Aguas Subterráneas de Chile',
        'en': 'Chile Groundwater Assessment'
    },
    'sub_header': {
        'es': 'Análisis Integral de Extracción, Agotamiento y Proyecciones',
        'en': 'Comprehensive Analysis of Extraction, Depletion, and Projections'
    },
    'sidebar_controls': {
        'es': '🔧 Controles',
        'en': '🔧 Controls'
    },
    'data_status': {
        'es': 'Estado de Datos:',
        'en': 'Data Status:'
    },
    'filters': {
        'es': '🔍 Filtros',
        'en': '🔍 Filters'
    },
    'region': {
        'es': 'Región',
        'en': 'Region'
    },
    'select_region': {
        'es': 'Seleccionar Región:',
        'en': 'Select Region:'
    },
    'select_shac': {
        'es': 'Seleccionar SHAC:',
        'en': 'Select SHAC:'
    },
    'trend_status': {
        'es': 'Estado de Tendencia:',
        'en': 'Trend Status:'
    },
    'filtered_wells': {
        'es': 'Pozos Filtrados',
        'en': 'Filtered Wells'
    },
    'last_updated': {
        'es': '📅 Última Actualización:',
        'en': '📅 Last Updated:'
    },
    # Tabs
    'tab_overview': {'es': '📊 Resumen', 'en': '📊 Overview'},
    'tab_census': {'es': '📊 Comparación Censo', 'en': '📊 Census Comparison'},
    'tab_analysis': {'es': '📈 Análisis de Pozo', 'en': '📈 Well Analysis'},
    'tab_spatial': {'es': '🏛️ Agregación Espacial', 'en': '🏛️ Spatial Aggregation'},
    'tab_tables': {'es': '📋 Tablas de Datos', 'en': '📋 Data Tables'},
    'tab_map': {'es': '🗺️ Mapa Interactivo', 'en': '🗺️ Interactive Map'},
    
    # Overview Metrics
    'registered_wells': {'es': 'Pozos Registrados (DGA)', 'en': 'Registered Wells (DGA)'},
    'unregistered_wells': {'es': 'Pozos No Registrados', 'en': 'Unregistered Wells'},
    'wells_declining': {'es': 'Pozos en Disminución', 'en': 'Wells Declining'},
    'gw_dependence': {'es': 'Cambio Dependencia AS', 'en': 'GW Dependence Change'},
    
    # Charts Titles
    'extraction_sources': {'es': 'Fuentes de Extracción', 'en': 'Extraction Sources'},
    'piezo_trends': {'es': 'Tendencias Piezométricas', 'en': 'Piezometric Trends'},
    'critical_regions': {'es': 'Regiones Críticas', 'en': 'Critical Regions'},
    'critical_basins': {'es': 'Cuencas Críticas', 'en': 'Critical Basins'},
    'critical_comunas': {'es': 'Comunas Críticas', 'en': 'Critical Comunas'},
    'critical_shacs': {'es': 'SHACs Críticos', 'en': 'Critical SHACs'},
    
    # Findings
    'key_findings': {'es': 'Hallazgos Clave', 'en': 'Key Findings'},
    'data_quality': {'es': '⚠️ Crisis de Calidad de Datos', 'en': '⚠️ Data Quality Crisis'},
    'data_quality_text': {'es': '10.4% de registros DGA con errores de geolocalización', 'en': '10.4% of DGA records contain geolocation errors'},
    'extraction_gap': {'es': '⚠️ Brecha Masiva de Extracción', 'en': '⚠️ Massive Extraction Gap'},
    'depletion': {'es': '⚠️ Agotamiento Generalizado', 'en': '⚠️ Widespread Aquifer Depletion'},
    'trajectory': {'es': '⚠️ Trayectoria Empeorando', 'en': '⚠️ Worsening Trajectory'},
    
    # Census
    'census_header': {'es': 'Comparación: DGA vs Censo 2017 vs Censo 2024', 'en': 'Comparison: DGA vs Census 2017 vs Census 2024'},
    'regional_overview': {'es': 'Panorama Regional', 'en': 'Regional Overview'},
    'comuna_analysis': {'es': 'Análisis Comunal', 'en': 'Comuna Analysis'},
    'census_change': {'es': 'Cambio Censo (2017→2024)', 'en': 'Census Change (2017→2024)'},
    'detailed_tables': {'es': 'Tablas Detalladas', 'en': 'Detailed Tables'},
    
    # Map
    'map_options': {'es': 'Opciones del Mapa', 'en': 'Map Options'},
    'color_by': {'es': 'Colorear pozos por:', 'en': 'Color wells by:'},
    'toggle_layers': {'es': 'Capas', 'en': 'Toggle Layers'},
    'export_coords': {'es': '📥 Exportar Coordenadas Visibles', 'en': '📥 Export Visible Well Coordinates'},
    'disclaimer': {'es': '⚠️ Aviso Importante', 'en': '⚠️ Important Disclaimers'}
}

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Chile Groundwater Assessment",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/chile-groundwater',
        'Report a bug': 'https://github.com/yourusername/chile-groundwater/issues',
        'About': """
        # Chile Groundwater Assessment Dashboard
        """
    }
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #2166ac;
        margin-bottom: 1rem;
    }
    
    /* Subheader styling */
    .sub-header {
        font-size: 1.2rem;
        color: #4a4a6a;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    
    /* Metric card styling */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2166ac;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2166ac;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Critical alert box */
    .critical-box {
        background-color: #ffebee;
        border-left: 4px solid #d32f2f;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    
    /* Success box */
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        font-size: 0.85rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING FUNCTIONS
# ============================================================

@st.cache_data(ttl=3600)
def load_piezometric_data(file_path=None):
    """Load piezometric analysis results from Excel"""
    
    # Try multiple potential paths
    potential_paths = [
        file_path,
        "data/Groundwater_Trend_Analysis_Complete.xlsx",
        "Groundwater_Trend_Analysis_Complete.xlsx",
        os.path.join(os.path.dirname(__file__), "data", "Groundwater_Trend_Analysis_Complete.xlsx")
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df_wells = pd.read_excel(path, sheet_name='All_Wells_Details')
                df_regions = pd.read_excel(path, sheet_name='Rankings_Region')
                df_comunas = pd.read_excel(path, sheet_name='Rankings_Comuna')
                df_shacs = pd.read_excel(path, sheet_name='Rankings_SHAC')
                df_cuencas = pd.read_excel(path, sheet_name='Rankings_Cuenca')
                
                return {
                    'wells': df_wells,
                    'regions': df_regions,
                    'comunas': df_comunas,
                    'shacs': df_shacs,
                    'cuencas': df_cuencas,
                    'loaded': True
                }
            except Exception as e:
                # Silent fail to fallback
                pass
    
    # If no file found, return demo data
    return generate_demo_data()


@st.cache_data(ttl=3600)
def load_triple_comparison_data(file_path=None):
    """Load triple comparison data (DGA vs Census 2017 vs Census 2024) from Excel"""
    
    potential_paths = [
        file_path,
        "data/Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx",
        "Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx",
        os.path.join(os.path.dirname(__file__), "data", "Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx")
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df_region = pd.read_excel(path, sheet_name='Por_Region')
                df_comuna = pd.read_excel(path, sheet_name='Por_Comuna')
                df_cambio_comuna = pd.read_excel(path, sheet_name='Cambio_Censos_Comuna')
                df_cambio_region = pd.read_excel(path, sheet_name='Cambio_Censos_Region')
                
                return {
                    'region': df_region,
                    'comuna': df_comuna,
                    'cambio_comuna': df_cambio_comuna,
                    'cambio_region': df_cambio_region,
                    'loaded': True
                }
            except Exception as e:
                # Silent fail
                pass
    
    return {'loaded': False}


@st.cache_data(ttl=3600)
def load_well_history_data(file_path=None):
    """Load well historical data from niveles_estaticos_pozos_historico.xlsx"""
    
    potential_paths = [
        file_path,
        "data/niveles_estaticos_pozos_historico.xlsx",
        "niveles_estaticos_pozos_historico.xlsx",
        os.path.join(os.path.dirname(__file__), "data", "niveles_estaticos_pozos_historico.xlsx")
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                
                # Parse date column (American format mm-dd-yyyy)
                df['Date'] = pd.to_datetime(df['Fecha_US'], format='%m-%d-%Y', errors='coerce')
                
                # Rename columns for easier access
                df = df.rename(columns={
                    'CODIGO ESTACION': 'Station_Code',
                    'NOMBRE ESTACION': 'Station_Name',
                    'Nivel': 'Water_Level',
                    'ALTITUD': 'Altitude',
                    'latitud_WGS84': 'Latitude',
                    'longitud_WGS84': 'Longitude',
                    'REGION': 'Region',
                    'COMUNA': 'Comuna'
                })
                
                # Ensure Station_Code is string
                df['Station_Code'] = df['Station_Code'].astype(str)
                
                return {
                    'data': df,
                    'loaded': True
                }
            except Exception as e:
                pass
    
    return {'loaded': False}


@st.cache_data(ttl=3600)
def load_dga_water_rights(file_path=None):
    """Load DGA water rights from FINAL_VALIDOS_En_Chile_ultimo.xlsx"""
    
    potential_paths = [
        file_path,
        "data/FINAL_VALIDOS_En_Chile_ultimo.xlsx",
        "FINAL_VALIDOS_En_Chile_ultimo.xlsx",
        os.path.join(os.path.dirname(__file__), "data", "FINAL_VALIDOS_En_Chile_ultimo.xlsx")
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                
                # Rename columns for easier access
                df = df.rename(columns={
                    'Código de Expediente': 'Expediente_Code',
                    'lat_wgs84_final': 'Latitude',
                    'lon_wgs84_final': 'Longitude',
                    'Caudal Anual Prom': 'Annual_Flow',
                    'Unidad de Caudal': 'Flow_Unit',
                    'Región': 'Region',
                    'Comuna': 'Comuna'
                })
                
                # Filter out invalid coordinates
                df = df.dropna(subset=['Latitude', 'Longitude'])
                df = df[(df['Latitude'] >= -56) & (df['Latitude'] <= -17)]
                df = df[(df['Longitude'] >= -76) & (df['Longitude'] <= -66)]
                
                return {
                    'data': df,
                    'loaded': True
                }
            except Exception as e:
                pass
    
    return {'loaded': False}


@st.cache_data(ttl=3600)
def load_census_points(year):
    """Load Census well points (2017 or 2024)"""
    
    if year == 2017:
        filename = "Censo_2017_pozos_5_meters.xlsx"
    else:
        filename = "Censo_2024_pozos_5_meters.xlsx"
    
    potential_paths = [
        f"data/{filename}",
        filename,
        os.path.join(os.path.dirname(__file__), "data", filename)
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                
                # Rename columns for consistency
                df = df.rename(columns={
                    'Long_WGS84': 'Longitude',
                    'Lat_WGS84': 'Latitude'
                })
                
                # Filter out invalid coordinates
                df = df.dropna(subset=['Latitude', 'Longitude'])
                df = df[(df['Latitude'] >= -56) & (df['Latitude'] <= -17)]
                df = df[(df['Longitude'] >= -76) & (df['Longitude'] <= -66)]
                
                return {
                    'data': df,
                    'loaded': True
                }
            except Exception as e:
                pass
    
    return {'loaded': False}


@st.cache_data(ttl=3600)
def load_census_data(file_path=None):
    """Load census comparison data from Excel"""
    
    potential_paths = [
        file_path,
        "data/Comparacion_Censo2017_vs_Censo2024.xlsx",
        "Comparacion_Censo2017_vs_Censo2024.xlsx"
    ]
    
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df_region = pd.read_excel(path, sheet_name='Por_Region')
                df_comuna = pd.read_excel(path, sheet_name='Por_Comuna')
                df_shac = pd.read_excel(path, sheet_name='Por_SHAC')
                
                return {
                    'region': df_region,
                    'comuna': df_comuna,
                    'shac': df_shac,
                    'loaded': True
                }
            except Exception as e:
                pass
    
    return {'loaded': False}


def generate_demo_data():
    """Generate demonstration data if files not available"""
    
    np.random.seed(42)
    n_wells = 474
    
    # Generate demo well data
    regions = ['Valparaíso', 'Metropolitana de Santiago', 'Coquimbo', 
               "O'Higgins", 'Tarapacá', 'Atacama', 'Biobío', 'Maule']
    
    df_wells = pd.DataFrame({
        'Station_Code': [f'{i:08d}' for i in range(n_wells)],
        'Station_Name': [f'Well_{i}' for i in range(n_wells)],
        'SHAC': np.random.choice(['Lampa', 'Chacabuco Polpaico', 'Colina', 'Popeta', 
                                   'Lo Barnechea', 'Santiago Norte', 'Maipo'], n_wells),
        'Region': np.random.choice(regions, n_wells),
        'Comuna': np.random.choice(['Santiago', 'Lampa', 'Colina', 'Quilicura', 
                                    'Pudahuel', 'Maipú', 'La Florida'], n_wells),
        'Latitude': np.random.uniform(-35, -30, n_wells),
        'Longitude': np.random.uniform(-71.5, -70, n_wells),
        'N_Records': np.random.randint(24, 500, n_wells),
        'Year_Start': np.random.randint(1980, 2010, n_wells),
        'Year_End': np.random.randint(2020, 2025, n_wells),
        'WL_Current': np.random.uniform(5, 80, n_wells),
        'Linear_Slope_m_yr': np.random.uniform(-0.5, 1.5, n_wells),
        'Linear_R2': np.random.uniform(0.1, 0.9, n_wells),
        'Consensus_Trend': np.random.choice(['Decreasing', 'Increasing', 'Stable'], 
                                            n_wells, p=[0.87, 0.08, 0.05]),
        'ARIMA_Pred_2030': None,
        'Prophet_Pred_2030': None,
        'LSTM_Pred_2030': None,
    })
    
    # Calculate predictions based on trend
    df_wells['ARIMA_Pred_2030'] = df_wells['WL_Current'] + df_wells['Linear_Slope_m_yr'] * 5
    df_wells['Prophet_Pred_2030'] = df_wells['ARIMA_Pred_2030'] * np.random.uniform(0.9, 1.1, n_wells)
    df_wells['LSTM_Pred_2030'] = df_wells['ARIMA_Pred_2030'] * np.random.uniform(0.85, 1.15, n_wells)
    
    # Generate aggregated data
    df_regions = df_wells.groupby('Region').agg({
        'Station_Code': 'count',
        'Linear_Slope_m_yr': 'mean',
        'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100
    }).reset_index()
    df_regions.columns = ['Region', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    
    df_shacs = df_wells.groupby('SHAC').agg({
        'Station_Code': 'count',
        'Linear_Slope_m_yr': 'mean',
        'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100
    }).reset_index()
    df_shacs.columns = ['SHAC', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    
    df_comunas = df_wells.groupby('Comuna').agg({
        'Station_Code': 'count',
        'Linear_Slope_m_yr': 'mean',
        'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100
    }).reset_index()
    df_comunas.columns = ['Comuna', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    
    return {
        'wells': df_wells,
        'regions': df_regions,
        'comunas': df_comunas,
        'shacs': df_shacs,
        'cuencas': pd.DataFrame(),
        'loaded': True,
        'demo': True
    }

# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================

def create_well_map(df_wells, selected_wells=None, color_by='Linear_Slope_m_yr',
                    show_dga_stations=False, dga_stations_data=None,
                    show_water_rights=False, water_rights_data=None,
                    show_census_2017=False, census_2017_data=None,
                    show_census_2024=False, census_2024_data=None,
                    lang='es'):
    """Create interactive Folium map with wells and additional layers"""
    
    # Center on Chile
    center_lat = df_wells['Latitude'].mean() if len(df_wells) > 0 else -33.45
    center_lon = df_wells['Longitude'].mean() if len(df_wells) > 0 else -70.65
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='cartodbpositron'
    )
    
    # Create feature groups for layer control
    layer_names = {
        'wells': '📍 Pozos Piezométricos' if lang == 'es' else '📍 Piezometric Wells',
        'dga': '🔵 Estaciones DGA' if lang == 'es' else '🔵 DGA Monitoring Stations',
        'rights': '💧 Derechos DGA' if lang == 'es' else '💧 DGA Water Rights',
        'c2017': '🏠 Censo 2017' if lang == 'es' else '🏠 Census 2017 Wells',
        'c2024': '🏘️ Censo 2024' if lang == 'es' else '🏘️ Census 2024 Wells'
    }

    wells_layer = folium.FeatureGroup(name=layer_names['wells'], show=True)
    dga_stations_layer = folium.FeatureGroup(name=layer_names['dga'], show=True)
    water_rights_layer = folium.FeatureGroup(name=layer_names['rights'], show=False)
    census_2017_layer = folium.FeatureGroup(name=layer_names['c2017'], show=False)
    census_2024_layer = folium.FeatureGroup(name=layer_names['c2024'], show=False)
    
    # Color scale based on trend for wells
    def get_color(value, min_val, max_val):
        if pd.isna(value):
            return 'gray'
        norm = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        if norm < 0.5:
            return 'blue'
        elif norm < 0.7:
            return 'orange'
        else:
            return 'red'
    
    if len(df_wells) > 0:
        min_val = df_wells[color_by].min()
        max_val = df_wells[color_by].max()
        
        # Add marker cluster for wells
        marker_cluster = MarkerCluster().add_to(wells_layer)
        
        for idx, row in df_wells.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                color = get_color(row[color_by], min_val, max_val)
                
                if selected_wells and row['Station_Code'] in selected_wells:
                    radius = 12
                    fill_opacity = 1.0
                else:
                    radius = 6
                    fill_opacity = 0.7
                
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin-bottom: 5px;">{row.get('Station_Name', row['Station_Code'])}</h4>
                    <hr style="margin: 5px 0;">
                    <b>SHAC:</b> {row.get('SHAC', 'N/A')}<br>
                    <b>Region:</b> {row.get('Region', 'N/A')}<br>
                    <b>Records:</b> {row.get('N_Records', 'N/A')}<br>
                    <b>Current Level:</b> {row.get('WL_Current', 'N/A'):.1f} m<br>
                    <b>Trend:</b> {row.get('Linear_Slope_m_yr', 'N/A'):.3f} m/yr<br>
                    <b>Status:</b> {row.get('Consensus_Trend', 'N/A')}
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=250),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=fill_opacity,
                    weight=1
                ).add_to(marker_cluster)
    
    # Add DGA Monitoring Stations layer
    if show_dga_stations and dga_stations_data is not None and dga_stations_data.get('loaded'):
        df_stations = dga_stations_data['data']
        # Get unique stations
        unique_stations = df_stations.drop_duplicates(subset=['Station_Code'])[['Station_Code', 'Station_Name', 'Latitude', 'Longitude', 'Altitude', 'Region', 'Comuna']].copy()
        
        station_cluster = MarkerCluster().add_to(dga_stations_layer)
        
        for idx, row in unique_stations.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                popup_html = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin-bottom: 5px; color: #1976d2;">🔵 DGA Station</h4>
                    <hr style="margin: 5px 0;">
                    <b>Name:</b> {row.get('Station_Name', 'N/A')}<br>
                    <b>Code:</b> {row.get('Station_Code', 'N/A')}<br>
                    <b>Region:</b> {row.get('Region', 'N/A')}<br>
                    <b>Comuna:</b> {row.get('Comuna', 'N/A')}<br>
                    <b>Altitude:</b> {row.get('Altitude', 'N/A')} m
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=250),
                    color='#1976d2',
                    fill=True,
                    fillColor='#1976d2',
                    fillOpacity=0.8,
                    weight=2
                ).add_to(station_cluster)
    
    # Add DGA Water Rights layer
    if show_water_rights and water_rights_data is not None and water_rights_data.get('loaded'):
        df_rights = water_rights_data['data']
        
        # Limit to first 5000 points for performance
        if len(df_rights) > 5000:
            df_rights_sample = df_rights.sample(n=5000, random_state=42)
        else:
            df_rights_sample = df_rights
        
        rights_cluster = MarkerCluster().add_to(water_rights_layer)
        
        for idx, row in df_rights_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                annual_flow = row.get('Annual_Flow', 'N/A')
                flow_unit = row.get('Flow_Unit', '')
                
                popup_html = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin-bottom: 5px; color: #7b1fa2;">💧 Water Right</h4>
                    <hr style="margin: 5px 0;">
                    <b>Expediente:</b> {row.get('Expediente_Code', 'N/A')}<br>
                    <b>Annual Flow:</b> {annual_flow} {flow_unit}<br>
                    <b>Region:</b> {row.get('Region', 'N/A')}<br>
                    <b>Comuna:</b> {row.get('Comuna', 'N/A')}
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,
                    popup=folium.Popup(popup_html, max_width=250),
                    color='#7b1fa2',
                    fill=True,
                    fillColor='#7b1fa2',
                    fillOpacity=0.6,
                    weight=1
                ).add_to(rights_cluster)
    
    # Add Census 2017 layer
    if show_census_2017 and census_2017_data is not None and census_2017_data.get('loaded'):
        df_census = census_2017_data['data']
        
        # Limit to first 5000 points for performance
        if len(df_census) > 5000:
            df_census_sample = df_census.sample(n=5000, random_state=42)
        else:
            df_census_sample = df_census
        
        census17_cluster = MarkerCluster().add_to(census_2017_layer)
        
        for idx, row in df_census_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=4,
                    popup=folium.Popup(f"Census 2017 Well<br>ID: {row.get('OID', 'N/A')}", max_width=150),
                    color='#4caf50',
                    fill=True,
                    fillColor='#4caf50',
                    fillOpacity=0.5,
                    weight=1
                ).add_to(census17_cluster)
    
    # Add Census 2024 layer
    if show_census_2024 and census_2024_data is not None and census_2024_data.get('loaded'):
        df_census = census_2024_data['data']
        
        # Limit to first 5000 points for performance
        if len(df_census) > 5000:
            df_census_sample = df_census.sample(n=5000, random_state=42)
        else:
            df_census_sample = df_census
        
        census24_cluster = MarkerCluster().add_to(census_2024_layer)
        
        for idx, row in df_census_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=4,
                    popup=folium.Popup(f"Census 2024 Well<br>ID: {row.get('OID', 'N/A')}", max_width=150),
                    color='#ff9800',
                    fill=True,
                    fillColor='#ff9800',
                    fillOpacity=0.5,
                    weight=1
                ).add_to(census24_cluster)
    
    # Add all layers to map
    wells_layer.add_to(m)
    dga_stations_layer.add_to(m)
    water_rights_layer.add_to(m)
    census_2017_layer.add_to(m)
    census_2024_layer.add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add legend
    legend_title = "Leyenda" if lang == 'es' else "Layer Legend"
    high_dec = "Alta Disminución" if lang == 'es' else "High Decline Wells"
    mod_dec = "Disminución Moderada" if lang == 'es' else "Moderate Decline"
    low_dec = "Baja/Recuperación" if lang == 'es' else "Low/Recovery"
    
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial; font-size: 11px;">
        <b>{legend_title}</b><br>
        <i style="background: red; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {high_dec}<br>
        <i style="background: orange; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {mod_dec}<br>
        <i style="background: blue; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {low_dec}<br>
        <i style="background: #1976d2; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> DGA Stations<br>
        <i style="background: #7b1fa2; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Water Rights<br>
        <i style="background: #4caf50; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Census 2017<br>
        <i style="background: #ff9800; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Census 2024
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def create_well_time_series_with_regression(df_well_data, well_id, well_name, lang='es'):
    """Create time series plot for a selected well with linear regression"""
    
    # Filter data for selected well
    df_well = df_well_data[df_well_data['Station_Code'] == well_id].copy()
    df_well = df_well.dropna(subset=['Date', 'Water_Level'])
    df_well = df_well.sort_values('Date')
    
    if len(df_well) < 2:
        return None, None, None, None
    
    # Convert dates to numeric for regression (days since first measurement)
    df_well['Days'] = (df_well['Date'] - df_well['Date'].min()).dt.days
    df_well['Years'] = df_well['Days'] / 365.25
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_well['Days'].values, 
        df_well['Water_Level'].values
    )
    
    # Convert slope to m/year
    slope_per_year = slope * 365.25
    r_squared = r_value ** 2
    
    # Create figure
    fig = make_subplots(rows=1, cols=1)
    
    # Texts
    txt_obs = 'Observaciones' if lang == 'es' else 'Observations'
    txt_date = 'Fecha' if lang == 'es' else 'Date'
    txt_depth = 'Profundidad' if lang == 'es' else 'Depth'
    txt_trend = 'Tendencia Lineal' if lang == 'es' else 'Linear Trend'
    txt_status_dec = "📈 Disminución (nivel baja)" if lang == 'es' else "📈 Declining (water level deepening)"
    txt_status_rec = "📉 Recuperación (nivel sube)" if lang == 'es' else "📉 Recovering (water level rising)"
    txt_status_stb = "➡️ Estable" if lang == 'es' else "➡️ Stable"
    
    # Historical data points
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=df_well['Water_Level'],
        mode='markers',
        name=txt_obs,
        marker=dict(color='#2166ac', size=8, opacity=0.7),
        hovertemplate=f'<b>{txt_date}:</b> %{{x|%Y-%m-%d}}<br><b>{txt_depth}:</b> %{{y:.2f}} m<extra></extra>'
    ))
    
    # Linear regression line
    x_reg = df_well['Date'].values
    y_reg = intercept + slope * df_well['Days'].values
    
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=y_reg,
        mode='lines',
        name=f'{txt_trend} ({slope_per_year:+.3f} m/yr)',
        line=dict(color='#d62728', width=3, dash='solid'),
        hovertemplate='<b>Trend:</b> %{y:.2f} m<extra></extra>'
    ))
    
    # Determine trend status
    if slope_per_year > 0.05:
        trend_status = txt_status_dec
        trend_color = "#d32f2f"
    elif slope_per_year < -0.05:
        trend_status = txt_status_rec
        trend_color = "#4caf50"
    else:
        trend_status = txt_status_stb
        trend_color = "#ff9800"
    
    # Add annotation for trend
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>Trend:</b> {slope_per_year:+.4f} m/year<br><b>R²:</b> {r_squared:.4f}<br><b>Status:</b> {trend_status}",
        showarrow=False,
        font=dict(size=12, color=trend_color),
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=trend_color,
        borderwidth=2,
        borderpad=4
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Well: {well_name} ({well_id})",
            font=dict(size=16)
        ),
        height=500,
        xaxis_title=txt_date,
        yaxis_title="Profundidad (m)" if lang == 'es' else "Depth to Water Level (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='closest'
    )
    
    # Invert y-axis (depth increases downward)
    fig.update_yaxes(autorange="reversed")
    
    return fig, slope_per_year, r_squared, len(df_well)


def create_regional_comparison_plot(df_regions, lang='es'):
    """Create bar chart comparing regions"""
    
    df_sorted = df_regions.sort_values('Avg_Linear_Slope_m_yr', ascending=True)
    
    colors = ['#d62728' if x > 0.3 else '#ff7f0e' if x > 0.1 else '#2ca02c' 
              for x in df_sorted['Avg_Linear_Slope_m_yr']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['Region'],
        x=df_sorted['Avg_Linear_Slope_m_yr'],
        orientation='h',
        marker_color=colors,
        text=[f"{x:.2f} m/yr" for x in df_sorted['Avg_Linear_Slope_m_yr']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Decline Rate: %{x:.3f} m/yr<extra></extra>'
    ))
    
    fig.add_vline(x=0, line_color="black", line_width=1)
    
    title = "Tasas Regionales de Disminución de Aguas Subterráneas" if lang == 'es' else "Regional Groundwater Decline Rates"
    xaxis = "Tasa Media de Disminución (m/año)" if lang == 'es' else "Mean Decline Rate (m/year)"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        height=500,
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    return fig


def create_shac_heatmap(df_shacs, lang='es'):
    """Create heatmap of SHAC metrics"""
    
    # Top 20 SHACs by decline rate
    df_top = df_shacs.nlargest(20, 'Avg_Linear_Slope_m_yr')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_top['SHAC'],
        x=df_top['Avg_Linear_Slope_m_yr'],
        orientation='h',
        marker=dict(
            color=df_top['Pct_Decreasing_Consensus'],
            colorscale='Reds',
            colorbar=dict(title="% Declining")
        ),
        text=[f"{x:.2f}" for x in df_top['Avg_Linear_Slope_m_yr']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Decline: %{x:.3f} m/yr<br>% Declining: %{marker.color:.1f}%<extra></extra>'
    ))
    
    title = "Top 20 SHACs Críticos por Tasa de Disminución" if lang == 'es' else "Top 20 Critical SHACs by Decline Rate"
    xaxis = "Tasa Media de Disminución (m/año)" if lang == 'es' else "Mean Decline Rate (m/year)"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        height=600,
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    return fig


def create_triple_comparison_chart(df_region, lang='es'):
    """Create grouped bar chart comparing DGA, Census 2017, and Census 2024 wells by region"""
    
    df_sorted = df_region.sort_values('Pozos_2024', ascending=True)
    
    fig = go.Figure()
    
    lbl_dga = 'Pozos DGA' if lang == 'es' else 'DGA Wells'
    lbl_c17 = 'Censo 2017' if lang == 'es' else 'Census 2017'
    lbl_c24 = 'Censo 2024' if lang == 'es' else 'Census 2024'
    
    fig.add_trace(go.Bar(
        name=lbl_dga,
        y=df_sorted['Region'],
        x=df_sorted['Pozos_DGA'],
        orientation='h',
        marker_color='#1976d2',
        text=df_sorted['Pozos_DGA'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name=lbl_c17,
        y=df_sorted['Region'],
        x=df_sorted['Pozos_Censo2017'],
        orientation='h',
        marker_color='#4caf50',
        text=df_sorted['Pozos_Censo2017'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name=lbl_c24,
        y=df_sorted['Region'],
        x=df_sorted['Pozos_2024'],
        orientation='h',
        marker_color='#ff9800',
        text=df_sorted['Pozos_2024'],
        textposition='auto',
    ))
    
    title = "Conteo de Pozos por Región: DGA vs Censo 2017 vs Censo 2024" if lang == 'es' else "Well Counts by Region: DGA vs Census 2017 vs Census 2024"
    xaxis = "Número de Pozos" if lang == 'es' else "Number of Wells"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        barmode='group',
        height=600,
        margin=dict(l=150, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_census_change_chart(df_cambio, level='Region', lang='es'):
    """Create chart showing census change between 2017 and 2024"""
    
    # Sort by change percentage
    df_sorted = df_cambio.sort_values('Cambio_Pozos_Pct', ascending=True)
    
    # Take top and bottom 15 for comuna level
    if level == 'Comuna':
        n_show = 20
        df_top = df_sorted.tail(n_show)
        df_bottom = df_sorted.head(n_show)
        df_sorted = pd.concat([df_bottom, df_top])
    
    # Color based on change direction
    colors = ['#4caf50' if x > 0 else '#d32f2f' for x in df_sorted['Cambio_Pozos_Pct']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted[level],
        x=df_sorted['Cambio_Pozos_Pct'],
        orientation='h',
        marker_color=colors,
        text=[f"{x:+.1f}%" for x in df_sorted['Cambio_Pozos_Pct']],
        textposition='outside',
        hovertemplate=f'<b>%{{y}}</b><br>Change: %{{x:.1f}}%<br>Wells 2017: %{{customdata[0]:,}}<br>Wells 2024: %{{customdata[1]:,}}<extra></extra>',
        customdata=df_sorted[['Pozos_2017', 'Pozos_2024']].values
    ))
    
    fig.add_vline(x=0, line_color="black", line_width=1)
    
    height = 600 if level == 'Region' else 800
    
    title = f"Cambio Censo 2017→2024 por {level} (%)" if lang == 'es' else f"Census Well Change 2017→2024 by {level} (%)"
    xaxis = "Cambio en Número de Pozos (%)" if lang == 'es' else "Change in Number of Wells (%)"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        height=height,
        margin=dict(l=200 if level == 'Comuna' else 150, r=80, t=50, b=50)
    )
    
    return fig


def create_gap_analysis_chart(df_region, lang='es'):
    """Create chart showing gap between DGA and Census data"""
    
    df_sorted = df_region.sort_values('Brecha_DGA_vs_Censo2024', ascending=False)
    
    t1 = 'Brecha: DGA vs Censo 2017' if lang == 'es' else 'Gap: DGA vs Census 2017'
    t2 = 'Brecha: DGA vs Censo 2024' if lang == 'es' else 'Gap: DGA vs Census 2024'
    
    fig = make_subplots(rows=1, cols=2, 
                        subplot_titles=(t1, t2),
                        shared_yaxes=True)
    
    # Gap vs Census 2017
    colors_2017 = ['#4caf50' if x >= 0 else '#d32f2f' for x in df_sorted['Brecha_DGA_vs_Censo2017']]
    fig.add_trace(go.Bar(
        y=df_sorted['Region'],
        x=df_sorted['Brecha_DGA_vs_Censo2017'],
        orientation='h',
        marker_color=colors_2017,
        name='vs Census 2017',
        text=[f"{x:+,}" for x in df_sorted['Brecha_DGA_vs_Censo2017']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Gap vs 2017: %{x:,}<extra></extra>'
    ), row=1, col=1)
    
    # Gap vs Census 2024
    colors_2024 = ['#4caf50' if x >= 0 else '#d32f2f' for x in df_sorted['Brecha_DGA_vs_Censo2024']]
    fig.add_trace(go.Bar(
        y=df_sorted['Region'],
        x=df_sorted['Brecha_DGA_vs_Censo2024'],
        orientation='h',
        marker_color=colors_2024,
        name='vs Census 2024',
        text=[f"{x:+,}" for x in df_sorted['Brecha_DGA_vs_Censo2024']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Gap vs 2024: %{x:,}<extra></extra>'
    ), row=1, col=2)
    
    fig.add_vline(x=0, line_color="black", line_width=1, row=1, col=1)
    fig.add_vline(x=0, line_color="black", line_width=1, row=1, col=2)
    
    title = "Brecha de Registro: DGA menos Censo (Negativo = No Registrado)" if lang == 'es' else "Registration Gap: DGA Wells minus Census Wells (Negative = Unregistered Wells)"
    
    fig.update_layout(
        title=title,
        height=600,
        showlegend=False,
        margin=dict(l=150, r=80, t=80, b=50)
    )
    
    return fig


def create_wells_per_housing_chart(df_cambio, level='Region', lang='es'):
    """Create chart showing wells per housing unit change"""
    
    df_sorted = df_cambio.sort_values('Cambio_Pct_Viviendas_Pozo', ascending=True)
    
    if level == 'Comuna':
        # Show top and bottom 15
        df_top = df_sorted.tail(15)
        df_bottom = df_sorted.head(15)
        df_sorted = pd.concat([df_bottom, df_top])
    
    fig = go.Figure()
    
    name1 = '% Viviendas con Pozo 2017' if lang == 'es' else '% Homes with Well 2017'
    name2 = '% Viviendas con Pozo 2024' if lang == 'es' else '% Homes with Well 2024'
    
    # Add bars for 2017 and 2024
    fig.add_trace(go.Bar(
        name=name1,
        y=df_sorted[level],
        x=df_sorted['Pct_Viviendas_Pozo_2017'],
        orientation='h',
        marker_color='#4caf50',
    ))
    
    fig.add_trace(go.Bar(
        name=name2,
        y=df_sorted[level],
        x=df_sorted['Pct_Viviendas_Pozo_2024'],
        orientation='h',
        marker_color='#ff9800',
    ))
    
    height = 600 if level == 'Region' else 800
    
    title = f"Porcentaje de Viviendas con Pozo por {level}: 2017 vs 2024" if lang == 'es' else f"Percentage of Homes with Wells by {level}: 2017 vs 2024"
    xaxis = "% Viviendas con Pozo" if lang == 'es' else "% of Homes with Wells"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis,
        barmode='group',
        height=height,
        margin=dict(l=200 if level == 'Comuna' else 150, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    """Main Streamlit application"""
    
    # ============================================================
    # SIDEBAR - DATA LOADING & FILTERS (Moved up for logic)
    # ============================================================
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/78/Flag_of_Chile.svg", width=100)
        
        # Language Selector
        lang_sel = st.radio("Idioma / Language", ["Español", "English"])
        lang = 'es' if lang_sel == "Español" else 'en'
        
        st.title(TRANS['sidebar_controls'][lang])
        
        st.markdown("---")
        
        # Data Loading (Simplified - Automatic)
        with st.spinner("Loading data..." if lang == 'en' else "Cargando datos..."):
            piezo_data = load_piezometric_data(None)
            census_data = load_census_data(None)
            triple_comparison_data = load_triple_comparison_data(None)
            well_history_data = load_well_history_data(None)
            dga_water_rights = load_dga_water_rights(None)
            census_2017_points = load_census_points(2017)
            census_2024_points = load_census_points(2024)
        
        if piezo_data.get('demo'):
            st.info("📊 Demo Data" if lang == 'en' else "📊 Datos de Demostración")
        
        # Show data loading status
        st.markdown(f"**{TRANS['data_status'][lang]}**")
        st.write(f"- Piezometric: {'✅' if piezo_data.get('loaded') else '❌'}")
        st.write(f"- Triple Comparison: {'✅' if triple_comparison_data.get('loaded') else '❌'}")
        st.write(f"- Well History: {'✅' if well_history_data.get('loaded') else '❌'}")
        st.write(f"- Water Rights: {'✅' if dga_water_rights.get('loaded') else '❌'}")
        st.write(f"- Census 2017: {'✅' if census_2017_points.get('loaded') else '❌'}")
        st.write(f"- Census 2024: {'✅' if census_2024_points.get('loaded') else '❌'}")
        
        st.markdown("---")
        
        # Filters
        st.subheader(TRANS['filters'][lang])
        
        if piezo_data.get('loaded'):
            df_wells = piezo_data['wells']
            
            # Region filter
            regions = ['All'] + sorted(df_wells['Region'].dropna().unique().tolist())
            selected_region = st.selectbox(TRANS['select_region'][lang], regions)
            
            # SHAC filter
            if selected_region != 'All':
                available_shacs = df_wells[df_wells['Region'] == selected_region]['SHAC'].dropna().unique()
            else:
                available_shacs = df_wells['SHAC'].dropna().unique()
            
            shacs = ['All'] + sorted(available_shacs.tolist())
            selected_shac = st.selectbox(TRANS['select_shac'][lang], shacs)
            
            # Trend filter
            trend_filter = st.multiselect(
                TRANS['trend_status'][lang],
                ['Decreasing', 'Increasing', 'Stable'],
                default=['Decreasing', 'Increasing', 'Stable']
            )
            
            # Apply filters
            df_filtered = df_wells.copy()
            if selected_region != 'All':
                df_filtered = df_filtered[df_filtered['Region'] == selected_region]
            if selected_shac != 'All':
                df_filtered = df_filtered[df_filtered['SHAC'] == selected_shac]
            if trend_filter:
                df_filtered = df_filtered[df_filtered['Consensus_Trend'].isin(trend_filter)]
            
            st.metric(TRANS['filtered_wells'][lang], len(df_filtered))
        else:
            df_filtered = pd.DataFrame()
        
        st.markdown("---")
        st.markdown(f"**{TRANS['last_updated'][lang]}** " + datetime.now().strftime("%Y-%m-%d"))

    # ============================================================
    # HEADER (In Main)
    # ============================================================
    st.markdown(f'<div class="main-header">💧 {TRANS["page_title"][lang]}</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{TRANS["sub_header"][lang]}</div>', 
                unsafe_allow_html=True)
    
    # ============================================================
    # MAIN CONTENT - TABS
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        TRANS['tab_overview'][lang], 
        TRANS['tab_census'][lang],
        TRANS['tab_analysis'][lang],
        TRANS['tab_spatial'][lang],
        TRANS['tab_tables'][lang],
        TRANS['tab_map'][lang]
    ])
    
    # ============================================================
    # TAB 1: OVERVIEW / DASHBOARD
    # ============================================================
    with tab1:
        st.header(TRANS['tab_overview'][lang])
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=TRANS['registered_wells'][lang],
                value="63,822",
                delta=None
            )
        
        with col2:
            st.metric(
                label=TRANS['unregistered_wells'][lang],
                value="~154,000",
                delta="+70.7%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label=TRANS['wells_declining'][lang],
                value="87.1%",
                delta="-413 wells",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label=TRANS['gw_dependence'][lang],
                value="+3.6%",
                delta="2017→2024",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Two columns for charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader(TRANS['extraction_sources'][lang])
            
            lbl_reg = 'Registrados (DGA)' if lang == 'es' else 'Registered (DGA)'
            lbl_unreg = 'No Registrados' if lang == 'es' else 'Unregistered'
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=[lbl_reg, lbl_unreg],
                values=[63822, 153580],
                hole=0.4,
                marker_colors=['#2166ac', '#d62728'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_pie.update_layout(
                height=350,
                showlegend=False,
                annotations=[dict(text='217K<br>Total', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig_pie, width="stretch")
        
        with col_right:
            st.subheader(TRANS['piezo_trends'][lang])
            
            lbl_dec = 'Disminuyendo' if lang == 'es' else 'Declining'
            lbl_stab = 'Estable/Subiendo' if lang == 'es' else 'Stable/Rising'
            
            fig_pie2 = go.Figure(data=[go.Pie(
                labels=[lbl_dec, lbl_stab],
                values=[413, 61],
                hole=0.4,
                marker_colors=['#d62728', '#2ca02c'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_pie2.update_layout(
                height=350,
                showlegend=False,
                annotations=[dict(text='474<br>Wells', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig_pie2, width="stretch")
        
        st.markdown("---")
        
        # Critical areas summary
        st.subheader("Áreas Críticas" if lang == 'es' else "Critical Areas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: #ffebee; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #d32f2f; margin: 0;">5</h1>
                <p style="margin: 5px 0 0 0;"><b>{TRANS['critical_regions'][lang]}</b></p>
                <small>≥90% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #ff6f00; margin: 0;">25</h1>
                <p style="margin: 5px 0 0 0;"><b>{TRANS['critical_basins'][lang]}</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: #f3e5f5; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #7b1fa2; margin: 0;">109</h1>
                <p style="margin: 5px 0 0 0;"><b>{TRANS['critical_comunas'][lang]}</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #1976d2; margin: 0;">102</h1>
                <p style="margin: 5px 0 0 0;"><b>{TRANS['critical_shacs'][lang]}</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Key findings
        st.subheader(TRANS['key_findings'][lang])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="critical-box">
                <h4>{TRANS['data_quality'][lang]}</h4>
                <ul>
                    <li>{TRANS['data_quality_text'][lang]}</li>
                    <li>7,233 wells plotted outside Chilean territory</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="critical-box">
                <h4>{TRANS['extraction_gap'][lang]}</h4>
                <ul>
                    <li>~154,000 unregistered extraction points nationally</li>
                    <li>70.7% of census-reported wells not in DGA registry</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="critical-box">
                <h4>{TRANS['depletion'][lang]}</h4>
                <ul>
                    <li>87.1% of monitored wells show declining trends</li>
                    <li>Mean decline rate: 0.24 m/year</li>
                    <li>Maximum decline: 4.24 m/year (unsustainable)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="critical-box">
                <h4>{TRANS['trajectory'][lang]}</h4>
                <ul>
                    <li>Groundwater dependence increased 3.6% (2017-2024)</li>
                    <li>Peri-urban zones show >80% increases</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 2: CENSUS COMPARISON
    # ============================================================
    with tab2:
        st.header(TRANS['census_header'][lang])
        
        if triple_comparison_data.get('loaded'):
            
            # Sub-tabs for different analyses
            subtab1, subtab2, subtab3, subtab4 = st.tabs([
                TRANS['regional_overview'][lang],
                TRANS['comuna_analysis'][lang], 
                TRANS['census_change'][lang],
                TRANS['detailed_tables'][lang]
            ])
            
            # ============================================================
            # SUBTAB 1: REGIONAL OVERVIEW
            # ============================================================
            with subtab1:
                st.subheader(TRANS['regional_overview'][lang])
                
                df_region = triple_comparison_data['region']
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_dga = df_region['Pozos_DGA'].sum()
                    st.metric("Total DGA", f"{total_dga:,}")
                
                with col2:
                    total_censo2017 = df_region['Pozos_Censo2017'].sum()
                    st.metric("Total Censo 2017", f"{total_censo2017:,}")
                
                with col3:
                    total_censo2024 = df_region['Pozos_2024'].sum()
                    st.metric("Total Censo 2024", f"{total_censo2024:,}")
                
                with col4:
                    change_pct = ((total_censo2024 - total_censo2017) / total_censo2017 * 100) if total_censo2017 > 0 else 0
                    st.metric("Cambio/Change 2017→2024", f"{change_pct:+.1f}%")
                
                st.markdown("---")
                
                # Triple comparison chart
                fig_triple = create_triple_comparison_chart(df_region, lang=lang)
                st.plotly_chart(fig_triple, width="stretch")
                
                st.markdown("---")
                
                # Gap analysis
                st.subheader("Análisis de Brecha" if lang == 'es' else "Gap Analysis")
                
                fig_gap = create_gap_analysis_chart(df_region, lang=lang)
                st.plotly_chart(fig_gap, width="stretch")
                
                # Summary statistics
                st.markdown("---")
                st.subheader("Tabla Resumen" if lang == 'es' else "Summary Table")
                
                df_display = df_region.copy()
                st.dataframe(df_display, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 2: COMUNA ANALYSIS
            # ============================================================
            with subtab2:
                st.subheader(TRANS['comuna_analysis'][lang])
                
                df_comuna = triple_comparison_data['comuna']
                
                # Filter options
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Search filter
                    search_comuna = st.text_input("🔍 Comuna:", "")
                    
                    # Sort options
                    sort_by = st.selectbox(
                        "Ordenar por / Sort by:",
                        ['Pozos_2024', 'Pozos_DGA', 'Brecha_DGA_vs_Censo2024', 'Cambio_Censo_2017_2024']
                    )
                    
                    sort_order = st.radio("Orden / Order:", ['Descending', 'Ascending'])
                
                with col2:
                    # Apply filters
                    df_filtered_comuna = df_comuna.copy()
                    
                    if search_comuna:
                        df_filtered_comuna = df_filtered_comuna[
                            df_filtered_comuna['Comuna'].str.contains(search_comuna, case=False, na=False)
                        ]
                    
                    ascending = sort_order == 'Ascending'
                    df_filtered_comuna = df_filtered_comuna.sort_values(sort_by, ascending=ascending)
                    
                    # Show top 30
                    df_top = df_filtered_comuna.head(30)
                    
                    # Create chart
                    fig = go.Figure()
                    
                    lbl_dga = 'Pozos DGA' if lang == 'es' else 'DGA Wells'
                    lbl_c17 = 'Censo 2017' if lang == 'es' else 'Census 2017'
                    lbl_c24 = 'Censo 2024' if lang == 'es' else 'Census 2024'

                    fig.add_trace(go.Bar(
                        name=lbl_dga,
                        y=df_top['Comuna'],
                        x=df_top['Pozos_DGA'],
                        orientation='h',
                        marker_color='#1976d2',
                    ))
                    
                    fig.add_trace(go.Bar(
                        name=lbl_c17,
                        y=df_top['Comuna'],
                        x=df_top['Pozos_Censo2017'],
                        orientation='h',
                        marker_color='#4caf50',
                    ))
                    
                    fig.add_trace(go.Bar(
                        name=lbl_c24,
                        y=df_top['Comuna'],
                        x=df_top['Pozos_2024'],
                        orientation='h',
                        marker_color='#ff9800',
                    ))
                    
                    title = f"Top 30 Comunas ({sort_by})"
                    xaxis = "Número de Pozos" if lang == 'es' else "Number of Wells"

                    fig.update_layout(
                        title=title,
                        xaxis_title=xaxis,
                        barmode='group',
                        height=800,
                        margin=dict(l=200, r=50, t=50, b=50),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig, width="stretch")
                
                # Table
                st.markdown("---")
                st.dataframe(df_filtered_comuna, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 3: CENSUS CHANGE ANALYSIS
            # ============================================================
            with subtab3:
                st.subheader(TRANS['census_change'][lang])
                
                analysis_level = st.radio(
                    "Nivel / Level:",
                    ['Regional', 'Comuna'],
                    horizontal=True
                )
                
                if analysis_level == 'Regional':
                    df_cambio = triple_comparison_data['cambio_region']
                    level_col = 'Region'
                else:
                    df_cambio = triple_comparison_data['cambio_comuna']
                    level_col = 'Comuna'
                
                # Change percentage chart
                st.subheader(f"Cambio Conteo Pozos / Well Count Change (%)")
                fig_change = create_census_change_chart(df_cambio, level_col, lang=lang)
                st.plotly_chart(fig_change, width="stretch")
                
                st.markdown("---")
                
                # Groundwater dependence chart
                st.subheader(f"Dependencia: % Viviendas con Pozo / % Homes with Wells")
                fig_gw = create_wells_per_housing_chart(df_cambio, level_col, lang=lang)
                st.plotly_chart(fig_gw, width="stretch")
                
                st.markdown("---")
                st.dataframe(df_cambio, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 4: DETAILED TABLES
            # ============================================================
            with subtab4:
                st.subheader(TRANS['detailed_tables'][lang])
                
                table_choice = st.selectbox(
                    "Select table:",
                    ['Regional Comparison', 'Comuna Comparison', 'Census Change by Region', 'Census Change by Comuna']
                )
                
                if table_choice == 'Regional Comparison':
                    df_export = triple_comparison_data['region']
                elif table_choice == 'Comuna Comparison':
                    df_export = triple_comparison_data['comuna']
                elif table_choice == 'Census Change by Region':
                    df_export = triple_comparison_data['cambio_region']
                else:
                    df_export = triple_comparison_data['cambio_comuna']
                
                st.dataframe(df_export, width="stretch", height=500)
                
                # Export button
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{table_choice.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.warning("No Data Available")
    
    # ============================================================
    # TAB 3: WELL ANALYSIS
    # ============================================================
    with tab3:
        st.header(TRANS['tab_analysis'][lang])
        
        if well_history_data.get('loaded'):
            df_history = well_history_data['data']
            
            # Get unique wells
            unique_wells = df_history.drop_duplicates(subset=['Station_Code'])[['Station_Code', 'Station_Name', 'Region', 'Comuna', 'Altitude', 'Latitude', 'Longitude']].copy()
            unique_wells = unique_wells.sort_values('Station_Name')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(TRANS['select_region'][lang])
                
                # Region filter for well selection
                regions_available = ['All'] + sorted(unique_wells['Region'].dropna().unique().tolist())
                selected_region_wells = st.selectbox(
                    "Filter Region:",
                    regions_available,
                    key="well_analysis_region"
                )
                
                if selected_region_wells != 'All':
                    wells_in_region = unique_wells[unique_wells['Region'] == selected_region_wells]
                else:
                    wells_in_region = unique_wells
                
                # Well selector
                well_options = wells_in_region.apply(
                    lambda x: f"{x['Station_Name']} ({x['Station_Code']})", axis=1
                ).tolist()
                
                if len(well_options) == 0:
                    st.warning("No wells available")
                    selected_well_display = None
                else:
                    label = "Seleccionar Pozo:" if lang == 'es' else "Select Well:"
                    selected_well_display = st.selectbox(label, well_options)
                
                if selected_well_display:
                    # Extract well code from selection
                    selected_well_code = selected_well_display.split('(')[-1].replace(')', '').strip()
                    selected_well_name = selected_well_display.split('(')[0].strip()
                    
                    # Get well info
                    well_info = unique_wells[unique_wells['Station_Code'] == selected_well_code].iloc[0]
                    
                    st.markdown("### Info")
                    
                    st.markdown(f"""
                    | Property | Value |
                    |----------|-------|
                    | **Station Code** | {well_info['Station_Code']} |
                    | **Station Name** | {well_info['Station_Name']} |
                    | **Region** | {well_info.get('Region', 'N/A')} |
                    | **Comuna** | {well_info.get('Comuna', 'N/A')} |
                    """)
            
            with col2:
                if selected_well_display:
                    st.subheader("Series de Tiempo" if lang == 'es' else "Time Series")
                    
                    # Create time series plot with regression
                    fig_ts, slope, r2, n_points = create_well_time_series_with_regression(
                        df_history, 
                        selected_well_code, 
                        selected_well_name,
                        lang=lang
                    )
                    
                    if fig_ts is not None:
                        st.plotly_chart(fig_ts, width="stretch")
                        
                        # Summary statistics
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Trend", f"{slope:+.4f} m/yr")
                        
                        with col_b:
                            st.metric("R² Value", f"{r2:.4f}")
                        
                        with col_c:
                            st.metric("Data Points", n_points)
                        
                        # Interpretation
                        st.markdown("---")
                        
                        if slope > 0.1:
                            st.warning(f"⚠️ **Decline:** {slope:.3f} m/year.")
                        elif slope < -0.1:
                            st.success(f"✅ **Recovery:** {slope:.3f} m/year.")
                        else:
                            st.info(f"ℹ️ **Stable:** {slope:.3f} m/year.")

                    else:
                        st.warning("Insufficient data" if lang == 'en' else "Datos insuficientes")
            
            # Data table for selected well
            if selected_well_display:
                st.markdown("---")
                
                well_data_display = df_history[df_history['Station_Code'] == selected_well_code][
                    ['Date', 'Water_Level', 'Station_Name', 'Altitude']
                ].sort_values('Date', ascending=False)
                
                st.dataframe(well_data_display, width="stretch", height=300)
                
                # Download button
                csv = well_data_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"well_{selected_well_code}_data.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No Well Data")
    
    # ============================================================
    # TAB 4: SPATIAL AGGREGATION
    # ============================================================
    with tab4:
        st.header(TRANS['tab_spatial'][lang])
        
        if piezo_data.get('loaded'):
            
            agg_level = st.radio(
                "Nivel / Level:",
                ['Region', 'SHAC', 'Comuna'],
                horizontal=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Rates: {agg_level}")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    fig_bar = create_regional_comparison_plot(piezo_data['regions'], lang=lang)
                    st.plotly_chart(fig_bar, width="stretch")
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    fig_bar = create_shac_heatmap(piezo_data['shacs'], lang=lang)
                    st.plotly_chart(fig_bar, width="stretch")
                elif agg_level == 'Comuna' and 'comunas' in piezo_data:
                    df_comunas = piezo_data['comunas'].nlargest(15, 'Avg_Linear_Slope_m_yr')
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=df_comunas['Comuna'],
                        x=df_comunas['Avg_Linear_Slope_m_yr'],
                        orientation='h',
                        marker_color='#d62728'
                    ))
                    fig.update_layout(
                        title="Top 15 Comunas",
                        xaxis_title="m/year",
                        height=500
                    )
                    st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.subheader("Stats")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    df_display = piezo_data['regions'][['Region', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    st.dataframe(df_display, width="stretch", height=500)
                    
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    df_display = piezo_data['shacs'][['SHAC', 'Total_Wells', 
                                                       'Avg_Linear_Slope_m_yr', 
                                                       'Pct_Decreasing_Consensus']].copy()
                    st.dataframe(df_display, width="stretch", height=500)
                    
                elif agg_level == 'Comuna' and 'comunas' in piezo_data:
                    df_display = piezo_data['comunas'][['Comuna', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    st.dataframe(df_display, width="stretch", height=500)
        else:
            st.warning("No data available.")
    
    # ============================================================
    # TAB 5: DATA TABLES
    # ============================================================
    with tab5:
        st.header(TRANS['tab_tables'][lang])
        
        if piezo_data.get('loaded'):
            
            table_choice = st.selectbox(
                "Select data table:",
                ['All Wells', 'Regional Summary', 'SHAC Summary', 'Comuna Summary', 'Well History Data']
            )
            
            if table_choice == 'All Wells':
                df_display = df_filtered.copy()
            elif table_choice == 'Regional Summary':
                df_display = piezo_data.get('regions', pd.DataFrame())
            elif table_choice == 'SHAC Summary':
                df_display = piezo_data.get('shacs', pd.DataFrame())
            elif table_choice == 'Comuna Summary':
                df_display = piezo_data.get('comunas', pd.DataFrame())
            elif table_choice == 'Well History Data':
                if well_history_data.get('loaded'):
                    df_display = well_history_data['data'].copy()
                else:
                    df_display = pd.DataFrame()
            
            st.dataframe(df_display, width="stretch", height=500)
            
            # Export button
            if len(df_display) > 0:
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{table_choice.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No data available.")
    
    # ============================================================
    # TAB 6: INTERACTIVE MAP (MOVED TO LAST)
    # ============================================================
    with tab6:
        st.header(TRANS['tab_map'][lang])
        
        # Disclaimers
        st.markdown(f"""
        <div class="disclaimer-box">
            <h4>{TRANS['disclaimer'][lang]}</h4>
            <ul>
                <li>DGA Water Rights geolocation may have errors.</li>
                <li>Census points are randomized within units (5m radius).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if piezo_data.get('loaded') and len(df_filtered) > 0:
            
            # Map options
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader(TRANS['map_options'][lang])
                
                color_option = st.selectbox(
                    TRANS['color_by'][lang],
                    ['Linear_Slope_m_yr', 'WL_Current', 'N_Records']
                )
                
                st.markdown("---")
                st.subheader(TRANS['toggle_layers'][lang])
                
                show_dga_stations = st.checkbox("🔵 DGA Stations", value=True)
                show_water_rights = st.checkbox("💧 Water Rights", value=False)
                show_census_2017 = st.checkbox("🏠 Censo 2017", value=False)
                show_census_2024 = st.checkbox("🏘️ Censo 2024", value=False)
            
            with col1:
                # Create map with all layers
                with st.spinner("Generando mapa..." if lang == 'es' else "Generating map..."):
                    m = create_well_map(
                        df_filtered, 
                        color_by=color_option,
                        show_dga_stations=show_dga_stations,
                        dga_stations_data=well_history_data,
                        show_water_rights=show_water_rights,
                        water_rights_data=dga_water_rights,
                        show_census_2017=show_census_2017,
                        census_2017_data=census_2017_points,
                        show_census_2024=show_census_2024,
                        census_2024_data=census_2024_points,
                        lang=lang
                    )
                
                # Display map
                st_folium(m, width=900, height=600, returned_objects=[])
            
            st.markdown("---")
            
            # Additional map controls
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                # Export filtered well coordinates
                if st.button(TRANS['export_coords'][lang]):
                    export_df = df_filtered[['Station_Code', 'Station_Name', 'Latitude', 'Longitude', 
                                             'Region', 'SHAC', 'Linear_Slope_m_yr', 'Consensus_Trend']].copy()
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="well_coordinates.csv",
                        mime="text/csv"
                    )
        
        else:
            st.warning("No well data available")
            
            # Show a basic Chile map anyway
            m = folium.Map(
                location=[-33.45, -70.65],
                zoom_start=5,
                tiles='cartodbpositron'
            )
            
            st_folium(m, width=800, height=500, returned_objects=[])
    
    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown("---")
    
    # Footer with methodology and credits
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📚 Data Sources
        - **DGA**: Dirección General de Aguas
        - **INE Census**: Instituto Nacional de Estadísticas
        """)
    
    with col2:
        st.markdown("""
        ### 🔬 Methodology
        - Linear regression for trend analysis
        - Consensus-based classification
        - Spatial aggregation
        """)
    
    with col3:
        st.markdown("""
        ### ⚠️ Limitations
        - Census data is self-reported
        - Piezometer coverage is uneven
        """)
    
    st.markdown("---")
    
    # Final disclaimer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.85rem; padding: 20px;">
        <b>Disclaimer:</b> This dashboard presents analysis of publicly available data for research and educational purposes. 
        The findings should be verified with official sources before making policy or management decisions.<br><br>
        <b>Chile Groundwater Assessment Dashboard</b> | Colorado School of Mines | 2024
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    main()
