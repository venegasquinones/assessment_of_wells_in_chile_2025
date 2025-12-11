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
        
        This interactive dashboard presents findings from a comprehensive 
        assessment of Chilean groundwater resources, combining:
        - DGA registry analysis
        - Census 2017 & 2024 comparison
        - Piezometric trend analysis
        - Ensemble projections to 2030
        
        **Authors**: [Your Name]
        **Institution**: Colorado School of Mines
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
                st.warning(f"Error loading {path}: {e}")
    
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
                st.warning(f"Error loading triple comparison data: {e}")
    
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
                st.warning(f"Error loading well history data: {e}")
    
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
                st.warning(f"Error loading DGA water rights: {e}")
    
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
                st.warning(f"Error loading Census {year} data: {e}")
    
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
                st.warning(f"Error loading census data: {e}")
    
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
                    show_census_2024=False, census_2024_data=None):
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
    wells_layer = folium.FeatureGroup(name='📍 Piezometric Wells', show=True)
    dga_stations_layer = folium.FeatureGroup(name='🔵 DGA Monitoring Stations', show=True)
    water_rights_layer = folium.FeatureGroup(name='💧 DGA Water Rights', show=False)
    census_2017_layer = folium.FeatureGroup(name='🏠 Census 2017 Wells', show=False)
    census_2024_layer = folium.FeatureGroup(name='🏘️ Census 2024 Wells', show=False)
    
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
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial; font-size: 11px;">
        <b>Layer Legend</b><br>
        <i style="background: red; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> High Decline Wells<br>
        <i style="background: orange; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Moderate Decline<br>
        <i style="background: blue; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Low/Recovery<br>
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


def create_well_time_series_with_regression(df_well_data, well_id, well_name):
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
    
    # Historical data points
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=df_well['Water_Level'],
        mode='markers',
        name='Observations',
        marker=dict(color='#2166ac', size=8, opacity=0.7),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Depth:</b> %{y:.2f} m<extra></extra>'
    ))
    
    # Linear regression line
    x_reg = df_well['Date'].values
    y_reg = intercept + slope * df_well['Days'].values
    
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=y_reg,
        mode='lines',
        name=f'Linear Trend ({slope_per_year:+.3f} m/yr)',
        line=dict(color='#d62728', width=3, dash='solid'),
        hovertemplate='<b>Trend:</b> %{y:.2f} m<extra></extra>'
    ))
    
    # Determine trend status
    if slope_per_year > 0.05:
        trend_status = "📈 Declining (water level deepening)"
        trend_color = "#d32f2f"
    elif slope_per_year < -0.05:
        trend_status = "📉 Recovering (water level rising)"
        trend_color = "#4caf50"
    else:
        trend_status = "➡️ Stable"
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
        xaxis_title="Date",
        yaxis_title="Depth to Water Level (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='closest'
    )
    
    # Invert y-axis (depth increases downward)
    fig.update_yaxes(autorange="reversed")
    
    return fig, slope_per_year, r_squared, len(df_well)


def create_regional_comparison_plot(df_regions):
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
    
    fig.update_layout(
        title="Regional Groundwater Decline Rates",
        xaxis_title="Mean Decline Rate (m/year)",
        height=500,
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    return fig


def create_shac_heatmap(df_shacs):
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
    
    fig.update_layout(
        title="Top 20 Critical SHACs by Decline Rate",
        xaxis_title="Mean Decline Rate (m/year)",
        height=600,
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    return fig


def create_triple_comparison_chart(df_region):
    """Create grouped bar chart comparing DGA, Census 2017, and Census 2024 wells by region"""
    
    df_sorted = df_region.sort_values('Pozos_2024', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='DGA Wells',
        y=df_sorted['Region'],
        x=df_sorted['Pozos_DGA'],
        orientation='h',
        marker_color='#1976d2',
        text=df_sorted['Pozos_DGA'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name='Census 2017',
        y=df_sorted['Region'],
        x=df_sorted['Pozos_Censo2017'],
        orientation='h',
        marker_color='#4caf50',
        text=df_sorted['Pozos_Censo2017'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name='Census 2024',
        y=df_sorted['Region'],
        x=df_sorted['Pozos_2024'],
        orientation='h',
        marker_color='#ff9800',
        text=df_sorted['Pozos_2024'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Well Counts by Region: DGA vs Census 2017 vs Census 2024",
        xaxis_title="Number of Wells",
        barmode='group',
        height=600,
        margin=dict(l=150, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_census_change_chart(df_cambio, level='Region'):
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
    
    fig.update_layout(
        title=f"Census Well Change 2017→2024 by {level} (%)",
        xaxis_title="Change in Number of Wells (%)",
        height=height,
        margin=dict(l=200 if level == 'Comuna' else 150, r=80, t=50, b=50)
    )
    
    return fig


def create_gap_analysis_chart(df_region):
    """Create chart showing gap between DGA and Census data"""
    
    df_sorted = df_region.sort_values('Brecha_DGA_vs_Censo2024', ascending=False)
    
    fig = make_subplots(rows=1, cols=2, 
                        subplot_titles=('Gap: DGA vs Census 2017', 'Gap: DGA vs Census 2024'),
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
    
    fig.update_layout(
        title="Registration Gap: DGA Wells minus Census Wells (Negative = Unregistered Wells)",
        height=600,
        showlegend=False,
        margin=dict(l=150, r=80, t=80, b=50)
    )
    
    return fig


def create_wells_per_housing_chart(df_cambio, level='Region'):
    """Create chart showing wells per housing unit change"""
    
    df_sorted = df_cambio.sort_values('Cambio_Pct_Viviendas_Pozo', ascending=True)
    
    if level == 'Comuna':
        # Show top and bottom 15
        df_top = df_sorted.tail(15)
        df_bottom = df_sorted.head(15)
        df_sorted = pd.concat([df_bottom, df_top])
    
    fig = go.Figure()
    
    # Add bars for 2017 and 2024
    fig.add_trace(go.Bar(
        name='% Homes with Well 2017',
        y=df_sorted[level],
        x=df_sorted['Pct_Viviendas_Pozo_2017'],
        orientation='h',
        marker_color='#4caf50',
    ))
    
    fig.add_trace(go.Bar(
        name='% Homes with Well 2024',
        y=df_sorted[level],
        x=df_sorted['Pct_Viviendas_Pozo_2024'],
        orientation='h',
        marker_color='#ff9800',
    ))
    
    height = 600 if level == 'Region' else 800
    
    fig.update_layout(
        title=f"Percentage of Homes with Wells by {level}: 2017 vs 2024",
        xaxis_title="% of Homes with Wells",
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
    # HEADER
    # ============================================================
    st.markdown('<div class="main-header">💧 Chile Groundwater Assessment Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive Analysis of Extraction, Depletion, and Projections</div>', 
                unsafe_allow_html=True)
    
    # ============================================================
    # SIDEBAR - DATA LOADING & FILTERS
    # ============================================================
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/78/Flag_of_Chile.svg", width=100)
        st.title("🔧 Controls")
        
        st.markdown("---")
        
        # File upload option
        st.subheader("📂 Data Source")
        
        data_source = st.radio(
            "Select data source:",
            ["Demo Data", "Upload Files"],
            help="Use demo data or upload your own Excel files"
        )
        
        if data_source == "Upload Files":
            piezo_file = st.file_uploader(
                "Piezometric Analysis Excel",
                type=['xlsx'],
                help="Upload Groundwater_Trend_Analysis_Complete.xlsx"
            )
            census_file = st.file_uploader(
                "Census Comparison Excel",
                type=['xlsx'],
                help="Upload Comparacion_Censo2017_vs_Censo2024.xlsx"
            )
            triple_file = st.file_uploader(
                "Triple Comparison Excel",
                type=['xlsx'],
                help="Upload Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx"
            )
        else:
            piezo_file = None
            census_file = None
            triple_file = None
        
        st.markdown("---")
        
        # Load data
        with st.spinner("Loading data..."):
            piezo_data = load_piezometric_data(piezo_file)
            census_data = load_census_data(census_file)
            triple_comparison_data = load_triple_comparison_data(triple_file)
            well_history_data = load_well_history_data()
            dga_water_rights = load_dga_water_rights()
            census_2017_points = load_census_points(2017)
            census_2024_points = load_census_points(2024)
        
        if piezo_data.get('demo'):
            st.info("📊 Using demonstration data")
        elif piezo_data.get('loaded'):
            st.success("✅ Data loaded successfully")
        
        # Show data loading status
        st.markdown("**Data Status:**")
        st.write(f"- Piezometric: {'✅' if piezo_data.get('loaded') else '❌'}")
        st.write(f"- Triple Comparison: {'✅' if triple_comparison_data.get('loaded') else '❌'}")
        st.write(f"- Well History: {'✅' if well_history_data.get('loaded') else '❌'}")
        st.write(f"- Water Rights: {'✅' if dga_water_rights.get('loaded') else '❌'}")
        st.write(f"- Census 2017: {'✅' if census_2017_points.get('loaded') else '❌'}")
        st.write(f"- Census 2024: {'✅' if census_2024_points.get('loaded') else '❌'}")
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        
        if piezo_data.get('loaded'):
            df_wells = piezo_data['wells']
            
            # Region filter
            regions = ['All'] + sorted(df_wells['Region'].dropna().unique().tolist())
            selected_region = st.selectbox("Select Region:", regions)
            
            # SHAC filter
            if selected_region != 'All':
                available_shacs = df_wells[df_wells['Region'] == selected_region]['SHAC'].dropna().unique()
            else:
                available_shacs = df_wells['SHAC'].dropna().unique()
            
            shacs = ['All'] + sorted(available_shacs.tolist())
            selected_shac = st.selectbox("Select SHAC:", shacs)
            
            # Trend filter
            trend_filter = st.multiselect(
                "Trend Status:",
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
            
            st.metric("Filtered Wells", len(df_filtered))
        else:
            df_filtered = pd.DataFrame()
        
        st.markdown("---")
        st.markdown("**📅 Last Updated:** " + datetime.now().strftime("%Y-%m-%d"))
    
    # ============================================================
    # MAIN CONTENT - TABS (REORDERED)
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "📊 Census Comparison",
        "📈 Well Analysis",
        "🏛️ Spatial Aggregation",
        "📋 Data Tables",
        "🗺️ Interactive Map"
    ])
    
    # ============================================================
    # TAB 1: OVERVIEW / DASHBOARD
    # ============================================================
    with tab1:
        st.header("National Summary Statistics")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Registered Wells (DGA)",
                value="63,822",
                delta=None,
                help="Validated extraction points in DGA registry"
            )
        
        with col2:
            st.metric(
                label="Unregistered Wells",
                value="~154,000",
                delta="+70.7%",
                delta_color="inverse",
                help="Census wells not in DGA registry"
            )
        
        with col3:
            st.metric(
                label="Wells Declining",
                value="87.1%",
                delta="-413 wells",
                delta_color="inverse",
                help="Piezometers with declining trends"
            )
        
        with col4:
            st.metric(
                label="GW Dependence Change",
                value="+3.6%",
                delta="2017→2024",
                delta_color="inverse",
                help="Change in groundwater dependence ratio"
            )
        
        st.markdown("---")
        
        # Two columns for charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Extraction Sources")
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Registered (DGA)', 'Unregistered (Census Gap)'],
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
            st.subheader("Piezometric Trends")
            
            fig_pie2 = go.Figure(data=[go.Pie(
                labels=['Declining', 'Stable/Rising'],
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
        st.subheader("Critical Areas Identified")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="background: #ffebee; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #d32f2f; margin: 0;">5</h1>
                <p style="margin: 5px 0 0 0;"><b>Critical Regions</b></p>
                <small>≥90% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #ff6f00; margin: 0;">25</h1>
                <p style="margin: 5px 0 0 0;"><b>Critical Basins</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: #f3e5f5; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #7b1fa2; margin: 0;">109</h1>
                <p style="margin: 5px 0 0 0;"><b>Critical Comunas</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #1976d2; margin: 0;">102</h1>
                <p style="margin: 5px 0 0 0;"><b>Critical SHACs</b></p>
                <small>≥75% declining</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Key findings
        st.subheader("Key Findings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="critical-box">
                <h4>⚠️ Data Quality Crisis</h4>
                <ul>
                    <li>10.4% of DGA records contain geolocation errors</li>
                    <li>7,233 wells plotted outside Chilean territory</li>
                    <li>Information base is fundamentally compromised</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="critical-box">
                <h4>⚠️ Massive Extraction Gap</h4>
                <ul>
                    <li>~154,000 unregistered extraction points nationally</li>
                    <li>70.7% of census-reported wells not in DGA registry</li>
                    <li>Concentrated in humid south and peri-urban zones</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="critical-box">
                <h4>⚠️ Widespread Aquifer Depletion</h4>
                <ul>
                    <li>87.1% of monitored wells show declining trends</li>
                    <li>Mean decline rate: 0.24 m/year</li>
                    <li>Maximum decline: 4.24 m/year (unsustainable)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="critical-box">
                <h4>⚠️ Worsening Trajectory</h4>
                <ul>
                    <li>Groundwater dependence increased 3.6% (2017-2024)</li>
                    <li>During Chile's megadrought when conservation expected</li>
                    <li>Peri-urban zones show >80% increases</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 2: CENSUS COMPARISON (NEW TAB)
    # ============================================================
    with tab2:
        st.header("Census Comparison: DGA vs Census 2017 vs Census 2024")
        
        st.markdown("""
        This section provides a comprehensive comparison between three data sources:
        - **DGA Registry**: Official groundwater extraction rights registered with DGA
        - **Census 2017**: Self-reported wells from the 2017 Population and Housing Census
        - **Census 2024**: Self-reported wells from the 2024 Population and Housing Census
        """)
        
        if triple_comparison_data.get('loaded'):
            
            # Sub-tabs for different analyses
            subtab1, subtab2, subtab3, subtab4 = st.tabs([
                "📊 Regional Overview",
                "🏘️ Comuna Analysis", 
                "📈 Census Change (2017→2024)",
                "📋 Detailed Tables"
            ])
            
            # ============================================================
            # SUBTAB 1: REGIONAL OVERVIEW
            # ============================================================
            with subtab1:
                st.subheader("Regional Comparison: DGA vs Census 2017 vs Census 2024")
                
                df_region = triple_comparison_data['region']
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_dga = df_region['Pozos_DGA'].sum()
                    st.metric("Total DGA Wells", f"{total_dga:,}")
                
                with col2:
                    total_censo2017 = df_region['Pozos_Censo2017'].sum()
                    st.metric("Total Census 2017", f"{total_censo2017:,}")
                
                with col3:
                    total_censo2024 = df_region['Pozos_2024'].sum()
                    st.metric("Total Census 2024", f"{total_censo2024:,}")
                
                with col4:
                    change_pct = ((total_censo2024 - total_censo2017) / total_censo2017 * 100) if total_censo2017 > 0 else 0
                    st.metric("Census Change 2017→2024", f"{change_pct:+.1f}%")
                
                st.markdown("---")
                
                # Triple comparison chart
                fig_triple = create_triple_comparison_chart(df_region)
                st.plotly_chart(fig_triple, width="stretch")
                
                st.markdown("---")
                
                # Gap analysis
                st.subheader("Registration Gap Analysis")
                st.markdown("""
                The gap shows the difference between DGA registered wells and Census-reported wells.
                **Negative values indicate unregistered wells** (Census reports more than DGA registry).
                """)
                
                fig_gap = create_gap_analysis_chart(df_region)
                st.plotly_chart(fig_gap, width="stretch")
                
                # Summary statistics
                st.markdown("---")
                st.subheader("Regional Summary Table")
                
                df_display = df_region.copy()
                df_display = df_display.rename(columns={
                    'Region': 'Region',
                    'Pozos_DGA': 'DGA Wells',
                    'Pozos_Censo2017': 'Census 2017',
                    'Pozos_2024': 'Census 2024',
                    'Viviendas_2024': 'Housing Units 2024',
                    'Brecha_DGA_vs_Censo2017': 'Gap vs 2017',
                    'Brecha_DGA_vs_Censo2024': 'Gap vs 2024',
                    'Cambio_Censo_2017_2024': 'Change 2017→2024',
                    'Cambio_Censo_Pct': 'Change %'
                })
                
                st.dataframe(df_display, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 2: COMUNA ANALYSIS
            # ============================================================
            with subtab2:
                st.subheader("Comuna-Level Comparison")
                
                df_comuna = triple_comparison_data['comuna']
                
                # Filter options
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Search filter
                    search_comuna = st.text_input("🔍 Search Comuna:", "")
                    
                    # Sort options
                    sort_by = st.selectbox(
                        "Sort by:",
                        ['Pozos_2024', 'Pozos_DGA', 'Brecha_DGA_vs_Censo2024', 'Cambio_Censo_2017_2024'],
                        format_func=lambda x: {
                            'Pozos_2024': 'Census 2024 Wells',
                            'Pozos_DGA': 'DGA Wells',
                            'Brecha_DGA_vs_Censo2024': 'Gap vs Census 2024',
                            'Cambio_Censo_2017_2024': 'Census Change 2017→2024'
                        }.get(x, x)
                    )
                    
                    sort_order = st.radio("Order:", ['Descending', 'Ascending'])
                
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
                    
                    fig.add_trace(go.Bar(
                        name='DGA Wells',
                        y=df_top['Comuna'],
                        x=df_top['Pozos_DGA'],
                        orientation='h',
                        marker_color='#1976d2',
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='Census 2017',
                        y=df_top['Comuna'],
                        x=df_top['Pozos_Censo2017'],
                        orientation='h',
                        marker_color='#4caf50',
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='Census 2024',
                        y=df_top['Comuna'],
                        x=df_top['Pozos_2024'],
                        orientation='h',
                        marker_color='#ff9800',
                    ))
                    
                    fig.update_layout(
                        title=f"Top 30 Comunas by {sort_by.replace('_', ' ')}",
                        xaxis_title="Number of Wells",
                        barmode='group',
                        height=800,
                        margin=dict(l=200, r=50, t=50, b=50),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig, width="stretch")
                
                # Table
                st.markdown("---")
                st.subheader("Comuna Data Table")
                
                df_display_comuna = df_filtered_comuna.rename(columns={
                    'Comuna': 'Comuna',
                    'Pozos_DGA': 'DGA Wells',
                    'Pozos_Censo2017': 'Census 2017',
                    'Pozos_2024': 'Census 2024',
                    'Viviendas_2024': 'Housing Units 2024',
                    'Brecha_DGA_vs_Censo2017': 'Gap vs 2017',
                    'Brecha_DGA_vs_Censo2024': 'Gap vs 2024',
                    'Cambio_Censo_2017_2024': 'Change 2017→2024'
                })
                
                st.dataframe(df_display_comuna, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 3: CENSUS CHANGE ANALYSIS
            # ============================================================
            with subtab3:
                st.subheader("Census Change Analysis: 2017 → 2024")
                
                analysis_level = st.radio(
                    "Analysis Level:",
                    ['Regional', 'Comuna'],
                    horizontal=True
                )
                
                if analysis_level == 'Regional':
                    df_cambio = triple_comparison_data['cambio_region']
                    level_col = 'Region'
                else:
                    df_cambio = triple_comparison_data['cambio_comuna']
                    level_col = 'Comuna'
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_2017 = df_cambio['Pozos_2017'].sum()
                    st.metric("Total Wells 2017", f"{total_2017:,}")
                
                with col2:
                    total_2024 = df_cambio['Pozos_2024'].sum()
                    st.metric("Total Wells 2024", f"{total_2024:,}")
                
                with col3:
                    change = total_2024 - total_2017
                    st.metric("Absolute Change", f"{change:+,}")
                
                with col4:
                    change_pct = ((total_2024 - total_2017) / total_2017 * 100) if total_2017 > 0 else 0
                    st.metric("Percentage Change", f"{change_pct:+.1f}%")
                
                st.markdown("---")
                
                # Change percentage chart
                st.subheader(f"Well Count Change by {level_col} (%)")
                fig_change = create_census_change_chart(df_cambio, level_col)
                st.plotly_chart(fig_change, width="stretch")
                
                st.markdown("---")
                
                # Groundwater dependence chart
                st.subheader(f"Groundwater Dependence: % of Homes with Wells")
                fig_gw = create_wells_per_housing_chart(df_cambio, level_col)
                st.plotly_chart(fig_gw, width="stretch")
                
                st.markdown("---")
                
                # Detailed metrics table
                st.subheader("Detailed Change Metrics")
                
                df_display_cambio = df_cambio.copy()
                
                # Rename columns for display
                rename_dict = {
                    level_col: level_col,
                    'Pozos_2017': 'Wells 2017',
                    'Viviendas_2017': 'Housing 2017',
                    'Pozos_2024': 'Wells 2024',
                    'Viviendas_2024': 'Housing 2024',
                    'Cambio_Pozos': 'Well Change',
                    'Cambio_Pozos_Pct': 'Well Change %',
                    'Cambio_Viviendas': 'Housing Change',
                    'Cambio_Viviendas_Pct': 'Housing Change %',
                    'Pct_Viviendas_Pozo_2017': '% Homes w/Well 2017',
                    'Pct_Viviendas_Pozo_2024': '% Homes w/Well 2024',
                    'Cambio_Pct_Viviendas_Pozo': 'Change in % Homes w/Well'
                }
                
                df_display_cambio = df_display_cambio.rename(columns=rename_dict)
                
                # Select columns to display
                display_cols = [level_col, 'Wells 2017', 'Wells 2024', 'Well Change', 'Well Change %',
                               '% Homes w/Well 2017', '% Homes w/Well 2024', 'Change in % Homes w/Well']
                
                df_display_cambio = df_display_cambio[[c for c in display_cols if c in df_display_cambio.columns]]
                
                st.dataframe(df_display_cambio, width="stretch", height=400)
            
            # ============================================================
            # SUBTAB 4: DETAILED TABLES
            # ============================================================
            with subtab4:
                st.subheader("Export Data Tables")
                
                table_choice = st.selectbox(
                    "Select table to view/export:",
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
                
                # Search filter
                search = st.text_input("🔍 Search:", "", key="census_search")
                if search:
                    mask = df_export.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_export = df_export[mask]
                
                st.dataframe(df_export, width="stretch", height=500)
                
                # Export button
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{table_choice.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.warning("Triple comparison data not available. Please ensure 'Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx' is in the data folder.")
            
            st.info("""
            **Expected file structure:**
            - Sheet 1: 'Por_Region' - Regional comparison
            - Sheet 2: 'Por_Comuna' - Comuna comparison
            - Sheet 3: 'Cambio_Censos_Comuna' - Census change by comuna
            - Sheet 4: 'Cambio_Censos_Region' - Census change by region
            """)
    
    # ============================================================
    # TAB 3: WELL ANALYSIS
    # ============================================================
    with tab3:
        st.header("Individual Well Analysis")
        
        if well_history_data.get('loaded'):
            df_history = well_history_data['data']
            
            # Get unique wells
            unique_wells = df_history.drop_duplicates(subset=['Station_Code'])[['Station_Code', 'Station_Name', 'Region', 'Comuna', 'Altitude', 'Latitude', 'Longitude']].copy()
            unique_wells = unique_wells.sort_values('Station_Name')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Select Well")
                
                # Region filter for well selection
                regions_available = ['All'] + sorted(unique_wells['Region'].dropna().unique().tolist())
                selected_region_wells = st.selectbox(
                    "Filter by Region:",
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
                    st.warning("No wells available for the selected region.")
                    selected_well_display = None
                else:
                    selected_well_display = st.selectbox(
                        "Select Well:",
                        well_options,
                        help="Choose a well to view detailed time series analysis"
                    )
                
                if selected_well_display:
                    # Extract well code from selection
                    selected_well_code = selected_well_display.split('(')[-1].replace(')', '').strip()
                    selected_well_name = selected_well_display.split('(')[0].strip()
                    
                    # Get well info
                    well_info = unique_wells[unique_wells['Station_Code'] == selected_well_code].iloc[0]
                    
                    st.markdown("### Well Information")
                    
                    st.markdown(f"""
                    | Property | Value |
                    |----------|-------|
                    | **Station Code** | {well_info['Station_Code']} |
                    | **Station Name** | {well_info['Station_Name']} |
                    | **Region** | {well_info.get('Region', 'N/A')} |
                    | **Comuna** | {well_info.get('Comuna', 'N/A')} |
                    | **Altitude** | {well_info.get('Altitude', 'N/A')} m |
                    | **Latitude** | {well_info.get('Latitude', 'N/A'):.6f} |
                    | **Longitude** | {well_info.get('Longitude', 'N/A'):.6f} |
                    """)
                    
                    # Get number of records for this well
                    well_records = df_history[df_history['Station_Code'] == selected_well_code]
                    st.markdown(f"**Total Records:** {len(well_records)}")
                    
                    if len(well_records) > 0:
                        min_date = well_records['Date'].min()
                        max_date = well_records['Date'].max()
                        if pd.notna(min_date) and pd.notna(max_date):
                            st.markdown(f"**Period:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            
            with col2:
                if selected_well_display:
                    st.subheader("Time Series & Linear Regression")
                    
                    # Create time series plot with regression
                    fig_ts, slope, r2, n_points = create_well_time_series_with_regression(
                        df_history, 
                        selected_well_code, 
                        selected_well_name
                    )
                    
                    if fig_ts is not None:
                        st.plotly_chart(fig_ts, width="stretch")
                        
                        # Summary statistics
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            if slope > 0:
                                st.metric("Trend", f"{slope:+.4f} m/yr", delta="Declining", delta_color="inverse")
                            else:
                                st.metric("Trend", f"{slope:+.4f} m/yr", delta="Recovering", delta_color="normal")
                        
                        with col_b:
                            st.metric("R² Value", f"{r2:.4f}")
                        
                        with col_c:
                            st.metric("Data Points", n_points)
                        
                        # Interpretation
                        st.markdown("---")
                        st.markdown("### Interpretation")
                        
                        if slope > 0.5:
                            st.error(f"⚠️ **Critical Decline:** This well shows a severe decline rate of {slope:.3f} m/year. At this rate, the water table is dropping rapidly, indicating potential over-extraction or reduced recharge.")
                        elif slope > 0.1:
                            st.warning(f"⚠️ **Moderate Decline:** This well shows a decline rate of {slope:.3f} m/year. Continued monitoring is recommended.")
                        elif slope > 0:
                            st.info(f"ℹ️ **Slight Decline:** This well shows a minor decline rate of {slope:.3f} m/year. The aquifer may be under mild stress.")
                        elif slope > -0.1:
                            st.success(f"✅ **Stable:** This well shows relatively stable water levels with minimal change ({slope:.3f} m/year).")
                        else:
                            st.success(f"✅ **Recovery:** This well shows rising water levels ({slope:.3f} m/year), indicating aquifer recovery.")
                        
                        if r2 < 0.3:
                            st.caption("Note: The low R² value indicates high variability in the data. The trend should be interpreted with caution.")
                    else:
                        st.warning("Insufficient data to generate time series plot. At least 2 valid measurements are required.")
                else:
                    st.info("Select a well from the list to view time series analysis.")
            
            # Data table for selected well
            if selected_well_display:
                st.markdown("---")
                st.subheader("Raw Data")
                
                well_data_display = df_history[df_history['Station_Code'] == selected_well_code][
                    ['Date', 'Water_Level', 'Station_Name', 'Altitude']
                ].sort_values('Date', ascending=False)
                
                well_data_display['Date'] = well_data_display['Date'].dt.strftime('%Y-%m-%d')
                well_data_display = well_data_display.rename(columns={
                    'Water_Level': 'Depth to Water (m)',
                    'Station_Name': 'Well Name',
                    'Altitude': 'Altitude (m)'
                })
                
                st.dataframe(well_data_display, width="stretch", height=300)
                
                # Download button
                csv = well_data_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download Well Data as CSV",
                    data=csv,
                    file_name=f"well_{selected_well_code}_data.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Well history data not available. Please ensure 'niveles_estaticos_pozos_historico.xlsx' is in the data folder.")
    
    # ============================================================
    # TAB 4: SPATIAL AGGREGATION
    # ============================================================
    with tab4:
        st.header("Spatial Aggregation Analysis")
        
        if piezo_data.get('loaded'):
            
            agg_level = st.radio(
                "Select aggregation level:",
                ['Region', 'SHAC', 'Comuna'],
                horizontal=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{agg_level} Decline Rates")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    fig_bar = create_regional_comparison_plot(piezo_data['regions'])
                    st.plotly_chart(fig_bar, width="stretch")
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    fig_bar = create_shac_heatmap(piezo_data['shacs'])
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
                        title="Top 15 Comunas by Decline Rate",
                        xaxis_title="Mean Decline Rate (m/year)",
                        height=500
                    )
                    st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.subheader(f"{agg_level} Summary Statistics")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    df_display = piezo_data['regions'][['Region', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Region', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False)
                    st.dataframe(df_display, width="stretch", height=500)
                    
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    df_display = piezo_data['shacs'][['SHAC', 'Total_Wells', 
                                                       'Avg_Linear_Slope_m_yr', 
                                                       'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['SHAC', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False).head(30)
                    st.dataframe(df_display, width="stretch", height=500)
                    
                elif agg_level == 'Comuna' and 'comunas' in piezo_data:
                    df_display = piezo_data['comunas'][['Comuna', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Comuna', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False).head(30)
                    st.dataframe(df_display, width="stretch", height=500)
        else:
            st.warning("No data available.")
    
    # ============================================================
    # TAB 5: DATA TABLES
    # ============================================================
    with tab5:
        st.header("Data Tables & Export")
        
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
                    st.warning("Well history data not loaded.")
            
            # Search filter
            search_term = st.text_input("🔍 Search:", "")
            if search_term and len(df_display) > 0:
                mask = df_display.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
                df_display = df_display[mask]
            
            st.dataframe(df_display, width="stretch", height=500)
            
            # Export button
            if len(df_display) > 0:
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
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
        st.header("Interactive Well Map")
        
        # Disclaimers
        st.markdown("""
        <div class="disclaimer-box">
            <h4>⚠️ Important Disclaimers</h4>
            <ul>
                <li><b>DGA Water Rights:</b> The water rights locations were processed by performing a join based on the expediente code. There may be errors in the geolocation of some points.</li>
                <li><b>Census 2017 & 2024 Points:</b> These points were generated using the 'Create Random Points' tool in ArcGIS Pro. Since this tool places points randomly within census units, locations may not be realistic, especially in larger areas. The 5-meter radius was used due to high density constraints. Census 2017 has block/rural/urban resolution while Census 2024 only has regional resolution, making Census 2017 more useful for detecting well density and location patterns.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if piezo_data.get('loaded') and len(df_filtered) > 0:
            st.info(f"Showing {len(df_filtered)} piezometric wells. Use the layer control to toggle additional data layers.")
            
            # Map options
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader("Map Options")
                
                color_option = st.selectbox(
                    "Color wells by:",
                    ['Linear_Slope_m_yr', 'WL_Current', 'N_Records'],
                    format_func=lambda x: {
                        'Linear_Slope_m_yr': 'Decline Rate (m/yr)',
                        'WL_Current': 'Current Water Level (m)',
                        'N_Records': 'Number of Records'
                    }.get(x, x)
                )
                
                st.markdown("---")
                st.subheader("Toggle Layers")
                
                show_dga_stations = st.checkbox(
                    "🔵 DGA Monitoring Stations",
                    value=True,
                    help="Show DGA monitoring station locations"
                )
                
                show_water_rights = st.checkbox(
                    "💧 DGA Water Rights",
                    value=False,
                    help="Show DGA water rights locations (may take time to load)"
                )
                
                show_census_2017 = st.checkbox(
                    "🏠 Census 2017 Wells",
                    value=False,
                    help="Show Census 2017 well locations"
                )
                
                show_census_2024 = st.checkbox(
                    "🏘️ Census 2024 Wells",
                    value=False,
                    help="Show Census 2024 well locations"
                )
                
                # Show layer statistics
                st.markdown("---")
                st.subheader("Layer Statistics")
                
                if show_dga_stations and well_history_data.get('loaded'):
                    unique_stations = well_history_data['data']['Station_Code'].nunique()
                    st.caption(f"🔵 DGA Stations: {unique_stations:,} locations")
                
                if show_water_rights and dga_water_rights.get('loaded'):
                    n_rights = len(dga_water_rights['data'])
                    st.caption(f"💧 Water Rights: {n_rights:,} points")
                    if n_rights > 5000:
                        st.caption("(Showing sample of 5,000)")
                
                if show_census_2017 and census_2017_points.get('loaded'):
                    n_c2017 = len(census_2017_points['data'])
                    st.caption(f"🏠 Census 2017: {n_c2017:,} points")
                    if n_c2017 > 5000:
                        st.caption("(Showing sample of 5,000)")
                
                if show_census_2024 and census_2024_points.get('loaded'):
                    n_c2024 = len(census_2024_points['data'])
                    st.caption(f"🏘️ Census 2024: {n_c2024:,} points")
                    if n_c2024 > 5000:
                        st.caption("(Showing sample of 5,000)")
            
            with col1:
                # Create map with all layers
                with st.spinner("Generating map..."):
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
                        census_2024_data=census_2024_points
                    )
                
                # Display map
                st_folium(m, width=900, height=600, returned_objects=[])
            
            # Map legend and explanation
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("""
                **🔴 High Decline Wells**
                - Decline rate > 0.3 m/year
                - Critical monitoring needed
                - Potential over-extraction
                """)
            
            with col_b:
                st.markdown("""
                **🟠 Moderate Decline Wells**
                - Decline rate 0.1-0.3 m/year
                - Regular monitoring recommended
                - Watch for acceleration
                """)
            
            with col_c:
                st.markdown("""
                **🔵 Low/Recovery Wells**
                - Decline rate < 0.1 m/year
                - Stable or recovering aquifers
                - May indicate sustainable use
                """)
            
            st.markdown("---")
            
            # Additional map controls
            st.subheader("Map Export Options")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                # Export filtered well coordinates
                if st.button("📥 Export Visible Well Coordinates"):
                    export_df = df_filtered[['Station_Code', 'Station_Name', 'Latitude', 'Longitude', 
                                             'Region', 'SHAC', 'Linear_Slope_m_yr', 'Consensus_Trend']].copy()
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download Well Coordinates CSV",
                        data=csv,
                        file_name="well_coordinates.csv",
                        mime="text/csv"
                    )
            
            with col_exp2:
                st.info("💡 Tip: Use the layer control on the map to toggle different data layers on/off.")
        
        else:
            st.warning("No well data available to display on map. Please check data loading status in the sidebar.")
            
            # Show a basic Chile map anyway
            st.markdown("### Chile Overview Map")
            
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
        - **INE Census 2017**: Instituto Nacional de Estadísticas
        - **INE Census 2024**: Instituto Nacional de Estadísticas
        - **Piezometric Data**: DGA Monitoring Network
        """)
    
    with col2:
        st.markdown("""
        ### 🔬 Methodology
        - Linear regression for trend analysis
        - Ensemble approach (ARIMA, Prophet, LSTM)
        - Consensus-based classification
        - Spatial aggregation by admin units
        """)
    
    with col3:
        st.markdown("""
        ### ⚠️ Limitations
        - 10.4% of DGA records have location errors
        - Census data is self-reported
        - Piezometer coverage is uneven
        - Projections assume trend continuity
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
