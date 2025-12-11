# ============================================================
# CHILE GROUNDWATER ASSESSMENT - INTERACTIVE DASHBOARD
# Streamlit Application for Data Visualization and Analysis
# Bilingual Support: Spanish (default) / English
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
from folium.plugins import MarkerCluster
import os
from datetime import datetime
from scipy import stats

# ============================================================
# TRANSLATION CONFIGURATION
# ============================================================
TRANSLATIONS = {
    'es': {
        # Page & Headers
        'page_title': "Evaluación de Aguas Subterráneas de Chile",
        'main_header': "💧 Panel de Evaluación de Aguas Subterráneas",
        'sub_header': "Análisis Integral de Extracción, Agotamiento y Proyecciones",
        'controls': "🔧 Controles",
        'language': "🌐 Idioma",
        'last_updated': "**📅 Última Actualización:**",
        
        # Sidebar
        'data_source': "📂 Fuente de Datos",
        'select_data_source': "Seleccionar fuente de datos:",
        'demo_data': "Datos de Demostración",
        'upload_files': "Subir Archivos",
        'piezo_excel': "Excel Análisis Piezométrico",
        'census_excel': "Excel Comparación Censal",
        'triple_excel': "Excel Comparación Triple",
        'loading_data': "Cargando datos...",
        'using_demo': "📊 Usando datos de demostración",
        'data_loaded': "✅ Datos cargados exitosamente",
        'data_status': "**Estado de Datos:**",
        'filters': "🔍 Filtros",
        'select_region': "Seleccionar Región:",
        'select_shac': "Seleccionar SHAC:",
        'trend_status': "Estado de Tendencia:",
        'filtered_wells': "Pozos Filtrados",
        'all': "Todos",
        
        # Tabs
        'tab_overview': "📊 Resumen",
        'tab_census': "📊 Comparación Censal",
        'tab_analysis': "📈 Análisis de Pozos",
        'tab_spatial': "🏛️ Agregación Espacial",
        'tab_tables': "📋 Tablas de Datos",
        'tab_map': "🗺️ Mapa Interactivo",
        
        # Overview
        'nat_summary': "Estadísticas Resumen Nacional",
        'reg_wells': "Pozos Registrados (DGA)",
        'unreg_wells': "Pozos No Registrados",
        'wells_declining': "Pozos en Declive",
        'gw_change': "Cambio Dependencia AS",
        'help_reg': "Puntos de extracción validados en registro DGA",
        'help_unreg': "Pozos censados no en registro DGA",
        'help_dec': "Piezómetros con tendencias decrecientes",
        'help_dep': "Cambio en ratio de dependencia de aguas subterráneas",
        'ext_sources': "Fuentes de Extracción",
        'piezo_trends': "Tendencias Piezométricas",
        'crit_areas': "Áreas Críticas Identificadas",
        'crit_regions': "Regiones Críticas",
        'crit_basins': "Cuencas Críticas",
        'crit_comunas': "Comunas Críticas",
        'crit_shacs': "SHACs Críticos",
        'pct_declining': "en declive",
        'key_findings': "Hallazgos Clave",
        'crisis_title': "⚠️ Crisis de Calidad de Datos",
        'gap_title': "⚠️ Brecha Masiva de Extracción",
        'depletion_title': "⚠️ Agotamiento Generalizado",
        'trajectory_title': "⚠️ Trayectoria en Deterioro",
        
        # Census Tab
        'census_header': "Comparación: DGA vs Censo 2017 vs Censo 2024",
        'subtab_regional': "Panorama Regional",
        'subtab_comuna': "Análisis Comunal",
        'subtab_change': "Análisis de Cambio (2017→2024)",
        'subtab_tables': "Tablas Detalladas",
        'total_dga': "Total Pozos DGA",
        'total_c17': "Total Censo 2017",
        'total_c24': "Total Censo 2024",
        'census_change': "Cambio Censal",
        'gap_analysis': "Análisis de Brecha de Registro",
        'search_comuna': "🔍 Buscar Comuna:",
        'sort_by': "Ordenar por:",
        
        # Well Analysis
        'ind_analysis': "Análisis Individual de Pozos",
        'select_well': "Seleccionar Pozo",
        'well_info': "Información del Pozo",
        'time_series': "Series Temporales y Regresión Lineal",
        'trend': "Tendencia",
        'points': "Puntos",
        'interpretation': "Interpretación",
        'raw_data': "Datos Crudos",
        'download_csv': "📥 Descargar CSV",
        'status_declining': "📉 En Declive (nivel bajando)",
        'status_recovering': "📈 Recuperando (nivel subiendo)",
        'status_stable': "➡️ Estable",
        'depth_water': "Profundidad al Agua (m)",
        
        # Spatial
        'agg_level': "Nivel de agregación:",
        'decline_rates': "Tasas de Descenso",
        'summary_stats': "Estadísticas Resumen",
        
        # Map
        'map_title': "Mapa Interactivo de Pozos",
        'disclaimers': "⚠️ Descargos de Responsabilidad Importantes",
        'map_options': "Opciones del Mapa",
        'color_by': "Colorear por:",
        'toggle_layers': "Alternar Capas",
        'layer_dga': "🔵 Estaciones DGA",
        'layer_rights': "💧 Derechos de Agua",
        'layer_c17': "🏠 Censo 2017",
        'layer_c24': "🏘️ Censo 2024",
        'legend_title': "Leyenda de Capas",
        'high_decline': "Alto Descenso",
        'moderate': "Moderado",
        'recovery': "Recuperación",
        
        # Footer
        'data_disclaimers': "📋 Descargos de Responsabilidad y Notas Metodológicas",
        'footer_text': "Fuentes de Datos: DGA Consolidado Nacional (2025), INE Censo 2017 & 2024",
        
        # Dynamic Values
        'val_declining': "En Declive",
        'val_stable': "Estable/Subiendo",
        'val_registered': "Registrados (DGA)",
        'val_unregistered': "No Registrados",
    },
    'en': {
        # Page & Headers
        'page_title': "Chile Groundwater Assessment",
        'main_header': "💧 Chile Groundwater Assessment Dashboard",
        'sub_header': "Comprehensive Analysis of Extraction, Depletion, and Projections",
        'controls': "🔧 Controls",
        'language': "🌐 Language",
        'last_updated': "**📅 Last Updated:**",
        
        # Sidebar
        'data_source': "📂 Data Source",
        'select_data_source': "Select data source:",
        'demo_data': "Demo Data",
        'upload_files': "Upload Files",
        'piezo_excel': "Piezometric Analysis Excel",
        'census_excel': "Census Comparison Excel",
        'triple_excel': "Triple Comparison Excel",
        'loading_data': "Loading data...",
        'using_demo': "📊 Using demonstration data",
        'data_loaded': "✅ Data loaded successfully",
        'data_status': "**Data Status:**",
        'filters': "🔍 Filters",
        'select_region': "Select Region:",
        'select_shac': "Select SHAC:",
        'trend_status': "Trend Status:",
        'filtered_wells': "Filtered Wells",
        'all': "All",
        
        # Tabs
        'tab_overview': "📊 Overview",
        'tab_census': "📊 Census Comparison",
        'tab_analysis': "📈 Well Analysis",
        'tab_spatial': "🏛️ Spatial Aggregation",
        'tab_tables': "📋 Data Tables",
        'tab_map': "🗺️ Interactive Map",
        
        # Overview
        'nat_summary': "National Summary Statistics",
        'reg_wells': "Registered Wells (DGA)",
        'unreg_wells': "Unregistered Wells",
        'wells_declining': "Wells Declining",
        'gw_change': "GW Dependence Change",
        'help_reg': "Validated extraction points in DGA registry",
        'help_unreg': "Census wells not in DGA registry",
        'help_dec': "Piezometers with declining trends",
        'help_dep': "Change in groundwater dependence ratio",
        'ext_sources': "Extraction Sources",
        'piezo_trends': "Piezometric Trends",
        'crit_areas': "Critical Areas Identified",
        'crit_regions': "Critical Regions",
        'crit_basins': "Critical Basins",
        'crit_comunas': "Critical Comunas",
        'crit_shacs': "Critical SHACs",
        'pct_declining': "declining",
        'key_findings': "Key Findings",
        'crisis_title': "⚠️ Data Quality Crisis",
        'gap_title': "⚠️ Massive Extraction Gap",
        'depletion_title': "⚠️ Widespread Depletion",
        'trajectory_title': "⚠️ Worsening Trajectory",
        
        # Census Tab
        'census_header': "Comparison: DGA vs Census 2017 vs Census 2024",
        'subtab_regional': "Regional Overview",
        'subtab_comuna': "Comuna Analysis",
        'subtab_change': "Change Analysis (2017→2024)",
        'subtab_tables': "Detailed Tables",
        'total_dga': "Total DGA Wells",
        'total_c17': "Total Census 2017",
        'total_c24': "Total Census 2024",
        'census_change': "Census Change",
        'gap_analysis': "Registration Gap Analysis",
        'search_comuna': "🔍 Search Comuna:",
        'sort_by': "Sort by:",
        
        # Well Analysis
        'ind_analysis': "Individual Well Analysis",
        'select_well': "Select Well",
        'well_info': "Well Information",
        'time_series': "Time Series & Linear Regression",
        'trend': "Trend",
        'points': "Points",
        'interpretation': "Interpretation",
        'raw_data': "Raw Data",
        'download_csv': "📥 Download CSV",
        'status_declining': "📉 Declining (water level deepening)",
        'status_recovering': "📈 Recovering (water level rising)",
        'status_stable': "➡️ Stable",
        'depth_water': "Depth to Water (m)",
        
        # Spatial
        'agg_level': "Aggregation level:",
        'decline_rates': "Decline Rates",
        'summary_stats': "Summary Statistics",
        
        # Map
        'map_title': "Interactive Well Map",
        'disclaimers': "⚠️ Important Disclaimers",
        'map_options': "Map Options",
        'color_by': "Color by:",
        'toggle_layers': "Toggle Layers",
        'layer_dga': "🔵 DGA Stations",
        'layer_rights': "💧 Water Rights",
        'layer_c17': "🏠 Census 2017",
        'layer_c24': "🏘️ Census 2024",
        'legend_title': "Layer Legend",
        'high_decline': "High Decline",
        'moderate': "Moderate",
        'recovery': "Recovery",
        
        # Footer
        'data_disclaimers': "📋 Data Disclaimers & Methodology Notes",
        'footer_text': "Data Sources: DGA Consolidado Nacional (2025), INE Census 2017 & 2024",
        
        # Dynamic Values
        'val_declining': "Declining",
        'val_stable': "Stable/Rising",
        'val_registered': "Registered (DGA)",
        'val_unregistered': "Unregistered",
    }
}

def t(key):
    """Get translated string based on session state language"""
    lang = st.session_state.get('language', 'es')
    return TRANSLATIONS[lang].get(key, key)

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Chile Groundwater Assessment",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Language State
if 'language' not in st.session_state:
    st.session_state.language = 'es'

# ============================================================
# CUSTOM CSS STYLING
# ============================================================
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1a1a2e; text-align: center; padding: 1rem 0; border-bottom: 3px solid #2166ac; margin-bottom: 1rem; }
    .sub-header { font-size: 1.2rem; color: #4a4a6a; text-align: center; font-style: italic; margin-bottom: 2rem; }
    .metric-card { background-color: white; border-radius: 10px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #2166ac; }
    .critical-box { background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 1rem; border-radius: 0 10px 10px 0; margin: 1rem 0; }
    .disclaimer-box { background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 1rem; border-radius: 0 10px 10px 0; margin: 1rem 0; font-size: 0.85rem; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING FUNCTIONS (Unchanged logic, wrapped for brevity)
# ============================================================

@st.cache_data(ttl=3600)
def load_piezometric_data(file_path=None):
    potential_paths = [file_path, "data/Groundwater_Trend_Analysis_Complete.xlsx", "Groundwater_Trend_Analysis_Complete.xlsx"]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                return {
                    'wells': pd.read_excel(path, sheet_name='All_Wells_Details'),
                    'regions': pd.read_excel(path, sheet_name='Rankings_Region'),
                    'comunas': pd.read_excel(path, sheet_name='Rankings_Comuna'),
                    'shacs': pd.read_excel(path, sheet_name='Rankings_SHAC'),
                    'loaded': True
                }
            except: pass
    return generate_demo_data()

@st.cache_data(ttl=3600)
def load_triple_comparison_data(file_path=None):
    potential_paths = [file_path, "data/Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx", "Comparacion_Triple_DGA_Censo2017_Censo2024.xlsx"]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                return {
                    'region': pd.read_excel(path, sheet_name='Por_Region'),
                    'comuna': pd.read_excel(path, sheet_name='Por_Comuna'),
                    'cambio_comuna': pd.read_excel(path, sheet_name='Cambio_Censos_Comuna'),
                    'cambio_region': pd.read_excel(path, sheet_name='Cambio_Censos_Region'),
                    'loaded': True
                }
            except: pass
    return {'loaded': False}

@st.cache_data(ttl=3600)
def load_well_history_data(file_path=None):
    potential_paths = [file_path, "data/niveles_estaticos_pozos_historico.xlsx", "niveles_estaticos_pozos_historico.xlsx"]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                df['Date'] = pd.to_datetime(df['Fecha_US'], format='%m-%d-%Y', errors='coerce')
                df = df.rename(columns={'CODIGO ESTACION': 'Station_Code', 'NOMBRE ESTACION': 'Station_Name', 'Nivel': 'Water_Level', 'ALTITUD': 'Altitude', 'latitud_WGS84': 'Latitude', 'longitud_WGS84': 'Longitude', 'REGION': 'Region', 'COMUNA': 'Comuna'})
                df['Station_Code'] = df['Station_Code'].astype(str)
                return {'data': df, 'loaded': True}
            except: pass
    return {'loaded': False}

@st.cache_data(ttl=3600)
def load_dga_water_rights(file_path=None):
    potential_paths = [file_path, "data/FINAL_VALIDOS_En_Chile_ultimo.xlsx", "FINAL_VALIDOS_En_Chile_ultimo.xlsx"]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                df = df.rename(columns={'Código de Expediente': 'Expediente_Code', 'lat_wgs84_final': 'Latitude', 'lon_wgs84_final': 'Longitude', 'Caudal Anual Prom': 'Annual_Flow', 'Unidad de Caudal': 'Flow_Unit', 'Región': 'Region', 'Comuna': 'Comuna'})
                df = df.dropna(subset=['Latitude', 'Longitude'])
                return {'data': df, 'loaded': True}
            except: pass
    return {'loaded': False}

@st.cache_data(ttl=3600)
def load_census_points(year):
    filename = "Censo_2017_pozos_5_meters.xlsx" if year == 2017 else "Censo_2024_pozos_5_meters.xlsx"
    potential_paths = [f"data/{filename}", filename]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_excel(path)
                df = df.rename(columns={'Long_WGS84': 'Longitude', 'Lat_WGS84': 'Latitude'})
                df = df.dropna(subset=['Latitude', 'Longitude'])
                return {'data': df, 'loaded': True}
            except: pass
    return {'loaded': False}

@st.cache_data(ttl=3600)
def load_census_data(file_path=None):
    potential_paths = [file_path, "data/Comparacion_Censo2017_vs_Censo2024.xlsx", "Comparacion_Censo2017_vs_Censo2024.xlsx"]
    for path in potential_paths:
        if path and os.path.exists(path):
            try:
                return {'region': pd.read_excel(path, sheet_name='Por_Region'), 'comuna': pd.read_excel(path, sheet_name='Por_Comuna'), 'shac': pd.read_excel(path, sheet_name='Por_SHAC'), 'loaded': True}
            except: pass
    return {'loaded': False}

def generate_demo_data():
    np.random.seed(42)
    n_wells = 474
    regions = ['Valparaíso', 'Metropolitana de Santiago', 'Coquimbo', "O'Higgins", 'Tarapacá', 'Atacama', 'Biobío', 'Maule']
    df_wells = pd.DataFrame({
        'Station_Code': [f'{i:08d}' for i in range(n_wells)],
        'Station_Name': [f'Well_{i}' for i in range(n_wells)],
        'SHAC': np.random.choice(['Lampa', 'Chacabuco Polpaico', 'Colina', 'Popeta', 'Lo Barnechea', 'Santiago Norte', 'Maipo'], n_wells),
        'Region': np.random.choice(regions, n_wells),
        'Comuna': np.random.choice(['Santiago', 'Lampa', 'Colina', 'Quilicura', 'Pudahuel', 'Maipú', 'La Florida'], n_wells),
        'Latitude': np.random.uniform(-35, -30, n_wells),
        'Longitude': np.random.uniform(-71.5, -70, n_wells),
        'N_Records': np.random.randint(24, 500, n_wells),
        'WL_Current': np.random.uniform(5, 80, n_wells),
        'Linear_Slope_m_yr': np.random.uniform(-0.5, 1.5, n_wells),
        'Consensus_Trend': np.random.choice(['Decreasing', 'Increasing', 'Stable'], n_wells, p=[0.87, 0.08, 0.05])
    })
    df_regions = df_wells.groupby('Region').agg({'Station_Code': 'count', 'Linear_Slope_m_yr': 'mean', 'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100}).reset_index()
    df_regions.columns = ['Region', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    df_shacs = df_wells.groupby('SHAC').agg({'Station_Code': 'count', 'Linear_Slope_m_yr': 'mean', 'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100}).reset_index()
    df_shacs.columns = ['SHAC', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    df_comunas = df_wells.groupby('Comuna').agg({'Station_Code': 'count', 'Linear_Slope_m_yr': 'mean', 'Consensus_Trend': lambda x: (x == 'Decreasing').sum() / len(x) * 100}).reset_index()
    df_comunas.columns = ['Comuna', 'Total_Wells', 'Avg_Linear_Slope_m_yr', 'Pct_Decreasing_Consensus']
    return {'wells': df_wells, 'regions': df_regions, 'comunas': df_comunas, 'shacs': df_shacs, 'loaded': True, 'demo': True}

# ============================================================
# VISUALIZATION FUNCTIONS (Updated with Language Support)
# ============================================================

def create_well_map(df_wells, selected_wells=None, color_by='Linear_Slope_m_yr',
                    show_dga_stations=False, dga_stations_data=None,
                    show_water_rights=False, water_rights_data=None,
                    show_census_2017=False, census_2017_data=None,
                    show_census_2024=False, census_2024_data=None, lang='es'):
    
    center_lat = df_wells['Latitude'].mean() if len(df_wells) > 0 else -33.45
    center_lon = df_wells['Longitude'].mean() if len(df_wells) > 0 else -70.65
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles='cartodbpositron')
    
    # Translated layer names
    wells_layer = folium.FeatureGroup(name='📍 ' + t('filtered_wells'), show=True)
    dga_layer = folium.FeatureGroup(name=t('layer_dga'), show=True)
    rights_layer = folium.FeatureGroup(name=t('layer_rights'), show=False)
    c17_layer = folium.FeatureGroup(name=t('layer_c17'), show=False)
    c24_layer = folium.FeatureGroup(name=t('layer_c24'), show=False)
    
    def get_color(value, min_val, max_val):
        if pd.isna(value): return 'gray'
        norm = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        return 'blue' if norm < 0.5 else 'orange' if norm < 0.7 else 'red'
    
    if len(df_wells) > 0:
        min_val, max_val = df_wells[color_by].min(), df_wells[color_by].max()
        marker_cluster = MarkerCluster().add_to(wells_layer)
        for idx, row in df_wells.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                color = get_color(row[color_by], min_val, max_val)
                popup = f"<b>{row.get('Station_Name')}</b><br>{t('trend')}: {row.get('Linear_Slope_m_yr',0):.3f} m/yr"
                folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=6,
                    popup=folium.Popup(popup, max_width=200), color=color, fill=True, fillColor=color, fillOpacity=0.7).add_to(marker_cluster)

    if show_dga_stations and dga_stations_data and dga_stations_data.get('loaded'):
        station_cluster = MarkerCluster().add_to(dga_layer)
        unique = dga_stations_data['data'].drop_duplicates('Station_Code')
        for idx, row in unique.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=8, color='#1976d2', fill=True, fillOpacity=0.8,
                    popup=f"{t('layer_dga')}: {row.get('Station_Name')}").add_to(station_cluster)

    if show_water_rights and water_rights_data and water_rights_data.get('loaded'):
        rights_cluster = MarkerCluster().add_to(rights_layer)
        df_sample = water_rights_data['data'].sample(n=min(5000, len(water_rights_data['data'])), random_state=42)
        for idx, row in df_sample.iterrows():
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color='#7b1fa2', fill=True, fillOpacity=0.6,
                popup=f"{t('layer_rights')}<br>{row.get('Annual_Flow')} {row.get('Flow_Unit')}").add_to(rights_cluster)

    if show_census_2017 and census_2017_data and census_2017_data.get('loaded'):
        c17_cluster = MarkerCluster().add_to(c17_layer)
        df_sample = census_2017_data['data'].sample(n=min(5000, len(census_2017_data['data'])), random_state=42)
        for idx, row in df_sample.iterrows():
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=4, color='#4caf50', fill=True, fillOpacity=0.5, popup=t('layer_c17')).add_to(c17_cluster)

    if show_census_2024 and census_2024_data and census_2024_data.get('loaded'):
        c24_cluster = MarkerCluster().add_to(c24_layer)
        df_sample = census_2024_data['data'].sample(n=min(5000, len(census_2024_data['data'])), random_state=42)
        for idx, row in df_sample.iterrows():
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=4, color='#ff9800', fill=True, fillOpacity=0.5, popup=t('layer_c24')).add_to(c24_cluster)

    wells_layer.add_to(m)
    dga_layer.add_to(m)
    rights_layer.add_to(m)
    c17_layer.add_to(m)
    c24_layer.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Legend
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; border: 2px solid gray; font-family: Arial; font-size: 11px;">
        <b>{t('legend_title')}</b><br>
        <i style="background: red; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('high_decline')}<br>
        <i style="background: orange; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('moderate')}<br>
        <i style="background: blue; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('recovery')}<br>
        <i style="background: #1976d2; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('layer_dga')}<br>
        <i style="background: #7b1fa2; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('layer_rights')}<br>
        <i style="background: #4caf50; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('layer_c17')}<br>
        <i style="background: #ff9800; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> {t('layer_c24')}
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

def create_well_time_series_with_regression(df_well_data, well_id, well_name, lang='es'):
    df_well = df_well_data[df_well_data['Station_Code'] == well_id].copy().dropna(subset=['Date', 'Water_Level']).sort_values('Date')
    if len(df_well) < 2: return None, None, None, None
    
    df_well['Days'] = (df_well['Date'] - df_well['Date'].min()).dt.days
    slope, intercept, r_value, _, _ = stats.linregress(df_well['Days'].values, df_well['Water_Level'].values)
    slope_per_year = slope * 365.25
    r_squared = r_value ** 2
    
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=df_well['Date'], y=df_well['Water_Level'], mode='markers', name='Obs', marker=dict(color='#2166ac', size=8)))
    fig.add_trace(go.Scatter(x=df_well['Date'], y=intercept + slope * df_well['Days'].values, mode='lines', name=f"{t('trend')} ({slope_per_year:+.3f} m/yr)", line=dict(color='#d62728', width=3)))
    
    title = f"{t('select_well')}: {well_name} ({well_id})"
    fig.update_layout(title=title, height=500, xaxis_title="Date", yaxis_title=t('depth_water'))
    fig.update_yaxes(autorange="reversed")
    return fig, slope_per_year, r_squared, len(df_well)

def create_regional_comparison_plot(df_regions, lang='es'):
    df_sorted = df_regions.sort_values('Avg_Linear_Slope_m_yr')
    colors = ['#d62728' if x > 0.3 else '#ff7f0e' if x > 0.1 else '#2ca02c' for x in df_sorted['Avg_Linear_Slope_m_yr']]
    fig = go.Figure(go.Bar(y=df_sorted['Region'], x=df_sorted['Avg_Linear_Slope_m_yr'], orientation='h', marker_color=colors))
    fig.update_layout(title=t('nat_summary'), xaxis_title="m/yr", height=500)
    return fig

def create_triple_comparison_chart(df_region, lang='es'):
    df_sorted = df_region.sort_values('Pozos_2024')
    fig = go.Figure()
    fig.add_trace(go.Bar(name='DGA', y=df_sorted['Region'], x=df_sorted['Pozos_DGA'], orientation='h', marker_color='#1976d2'))
    fig.add_trace(go.Bar(name=t('layer_c17'), y=df_sorted['Region'], x=df_sorted['Pozos_Censo2017'], orientation='h', marker_color='#4caf50'))
    fig.add_trace(go.Bar(name=t('layer_c24'), y=df_sorted['Region'], x=df_sorted['Pozos_2024'], orientation='h', marker_color='#ff9800'))
    fig.update_layout(title=t('census_header'), barmode='group', height=600)
    return fig

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    # Language Selector in Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/78/Flag_of_Chile.svg", width=100)
        c1, c2 = st.columns(2)
        if c1.button("🇪🇸 Español"): st.session_state.language = 'es'; st.rerun()
        if c2.button("🇬🇧 English"): st.session_state.language = 'en'; st.rerun()
        
        st.title(t('controls'))
        data_source = st.radio(t('select_data_source'), [t('demo_data'), t('upload_files')])
        
        piezo_file, census_file, triple_file = None, None, None
        if data_source == t('upload_files'):
            piezo_file = st.file_uploader(t('piezo_excel'), type=['xlsx'])
            census_file = st.file_uploader(t('census_excel'), type=['xlsx'])
            triple_file = st.file_uploader(t('triple_excel'), type=['xlsx'])
            
        with st.spinner(t('loading_data')):
            piezo_data = load_piezometric_data(piezo_file)
            census_data = load_census_data(census_file)
            triple_comparison_data = load_triple_comparison_data(triple_file)
            well_history_data = load_well_history_data()
            dga_water_rights = load_dga_water_rights()
            census_2017_points = load_census_points(2017)
            census_2024_points = load_census_points(2024)
            
        if piezo_data.get('demo'): st.info(t('using_demo'))
        elif piezo_data.get('loaded'): st.success(t('data_loaded'))
        
        if piezo_data.get('loaded'):
            df_wells = piezo_data['wells']
            regions = [t('all')] + sorted(df_wells['Region'].dropna().unique().tolist())
            selected_region = st.selectbox(t('select_region'), regions)
            
            if selected_region != t('all'):
                df_filtered = df_wells[df_wells['Region'] == selected_region]
            else:
                df_filtered = df_wells
            st.metric(t('filtered_wells'), len(df_filtered))
        else:
            df_filtered = pd.DataFrame()

    # Main Content
    st.markdown(f'<div class="main-header">{t("main_header")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t("sub_header")}</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t('tab_overview'), t('tab_census'), t('tab_analysis'), 
        t('tab_spatial'), t('tab_tables'), t('tab_map')
    ])
    
    # Tab 1: Overview
    with tab1:
        st.header(t('nat_summary'))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t('reg_wells'), "63,822", help=t('help_reg'))
        c2.metric(t('unreg_wells'), "~154,000", "+70.7%", delta_color="inverse", help=t('help_unreg'))
        c3.metric(t('wells_declining'), "87.1%", "-413", delta_color="inverse", help=t('help_dec'))
        c4.metric(t('gw_change'), "+3.6%", "2017→2024", delta_color="inverse", help=t('help_dep'))
        
        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader(t('ext_sources'))
            fig_pie = go.Figure(data=[go.Pie(labels=[t('val_registered'), t('val_unregistered')], values=[63822, 153580], hole=0.4)])
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_right:
            st.subheader(t('piezo_trends'))
            fig_pie2 = go.Figure(data=[go.Pie(labels=[t('val_declining'), t('val_stable')], values=[413, 61], hole=0.4)])
            st.plotly_chart(fig_pie2, use_container_width=True)

        st.markdown("---")
        st.subheader(t('key_findings'))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='critical-box'><h4>{t('crisis_title')}</h4><p>10.4% errors in DGA records.</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='critical-box'><h4>{t('gap_title')}</h4><p>70.7% gap between Census and DGA.</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='critical-box'><h4>{t('depletion_title')}</h4><p>87.1% wells declining.</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='critical-box'><h4>{t('trajectory_title')}</h4><p>GW dependence increased 3.6%.</p></div>", unsafe_allow_html=True)

    # Tab 2: Census
    with tab2:
        st.header(t('census_header'))
        if triple_comparison_data.get('loaded'):
            fig_triple = create_triple_comparison_chart(triple_comparison_data['region'], lang=st.session_state.language)
            st.plotly_chart(fig_triple, use_container_width=True)
        else:
            st.warning("No Data")

    # Tab 3: Well Analysis
    with tab3:
        st.header(t('ind_analysis'))
        if well_history_data.get('loaded'):
            df_hist = well_history_data['data']
            unique_wells = df_hist.drop_duplicates('Station_Code').sort_values('Station_Name')
            
            c1, c2 = st.columns([1, 2])
            with c1:
                sel_well_str = st.selectbox(t('select_well'), unique_wells.apply(lambda x: f"{x['Station_Name']} ({x['Station_Code']})", axis=1))
                if sel_well_str:
                    sel_code = sel_well_str.split('(')[-1].strip(')')
                    sel_name = sel_well_str.split('(')[0].strip()
            with c2:
                if sel_well_str:
                    fig_ts, slope, r2, n = create_well_time_series_with_regression(df_hist, sel_code, sel_name, lang=st.session_state.language)
                    if fig_ts:
                        st.plotly_chart(fig_ts, use_container_width=True)
                        trend_msg = t('status_declining') if slope > 0 else t('status_recovering')
                        st.info(f"{t('trend')}: {slope:+.4f} m/yr | R²: {r2:.4f} | {trend_msg}")

    # Tab 4: Spatial
    with tab4:
        st.header(t('tab_spatial'))
        if piezo_data.get('loaded'):
            st.plotly_chart(create_regional_comparison_plot(piezo_data['regions'], lang=st.session_state.language), use_container_width=True)

    # Tab 5: Tables
    with tab5:
        st.header(t('tab_tables'))
        if piezo_data.get('loaded'):
            st.dataframe(df_filtered, use_container_width=True)

    # Tab 6: Map
    with tab6:
        st.header(t('map_title'))
        st.markdown(f"<div class='disclaimer-box'><h4>{t('disclaimers')}</h4><p>ArcGIS Random Points used for Census data visualization.</p></div>", unsafe_allow_html=True)
        
        if piezo_data.get('loaded'):
            c1, c2 = st.columns([3, 1])
            with c2:
                st.subheader(t('map_options'))
                color_opt = st.selectbox(t('color_by'), ['Linear_Slope_m_yr', 'WL_Current'])
                show_dga = st.checkbox(t('layer_dga'), True)
                show_rights = st.checkbox(t('layer_rights'), False)
                show_c17 = st.checkbox(t('layer_c17'), False)
                show_c24 = st.checkbox(t('layer_c24'), False)
            with c1:
                with st.spinner(t('loading_data')):
                    m = create_well_map(df_filtered, selected_wells=None, color_by=color_opt,
                                      show_dga_stations=show_dga, dga_stations_data=well_history_data,
                                      show_water_rights=show_rights, water_rights_data=dga_water_rights,
                                      show_census_2017=show_c17, census_2017_data=census_2017_points,
                                      show_census_2024=show_c24, census_2024_data=census_2024_points,
                                      lang=st.session_state.language)
                    st_folium(m, width=None, height=600)

    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #666;'>{t('footer_text')}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
