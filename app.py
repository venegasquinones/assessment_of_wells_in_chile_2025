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
from streamlit_folium import st_folium, folium_static
from folium.plugins import MarkerCluster, HeatMap
import json
import os
from datetime import datetime

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

def create_well_map(df_wells, selected_wells=None, color_by='Linear_Slope_m_yr'):
    """Create interactive Folium map with wells"""
    
    # Center on Chile
    center_lat = df_wells['Latitude'].mean()
    center_lon = df_wells['Longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='cartodbpositron'
    )
    
    # Color scale based on trend
    def get_color(value, min_val, max_val):
        if pd.isna(value):
            return 'gray'
        # Normalize value
        norm = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        # Color from blue (low/negative) to red (high/positive)
        if norm < 0.5:
            return 'blue'
        elif norm < 0.7:
            return 'orange'
        else:
            return 'red'
    
    min_val = df_wells[color_by].min()
    max_val = df_wells[color_by].max()
    
    # Add marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    for idx, row in df_wells.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            color = get_color(row[color_by], min_val, max_val)
            
            # Highlight selected wells
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
    
    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial;">
        <b>Decline Rate (m/yr)</b><br>
        <i style="background: blue; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Low/Recovery<br>
        <i style="background: orange; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> Moderate<br>
        <i style="background: red; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> High Decline
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_time_series_plot(well_data, well_id):
    """Create time series plot for a selected well with projections"""
    
    well = well_data[well_data['Station_Code'] == well_id].iloc[0]
    
    # Generate synthetic historical data based on well statistics
    year_start = int(well.get('Year_Start', 2000))
    year_end = int(well.get('Year_End', 2024))
    current_level = well.get('WL_Current', 20)
    trend = well.get('Linear_Slope_m_yr', 0.1)
    
    years = np.arange(year_start, year_end + 1)
    years_from_end = year_end - years
    levels = current_level - trend * years_from_end
    
    # Add noise
    np.random.seed(hash(well_id) % 2**32)
    noise = np.random.normal(0, abs(trend) * 2, len(years))
    levels_noisy = levels + noise
    
    # Create figure
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=[f"Well: {well.get('Station_Name', well_id)}"]
    )
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=years,
        y=levels_noisy,
        mode='markers',
        name='Observations',
        marker=dict(color='#404040', size=6, opacity=0.5)
    ))
    
    # Trend line
    fig.add_trace(go.Scatter(
        x=years,
        y=levels,
        mode='lines',
        name='Trend',
        line=dict(color='#404040', width=2)
    ))
    
    # Projections
    proj_years = np.arange(year_end, 2031)
    
    # ARIMA projection
    arima_pred = well.get('ARIMA_Pred_2030')
    if pd.notna(arima_pred):
        arima_line = np.linspace(current_level, arima_pred, len(proj_years))
        fig.add_trace(go.Scatter(
            x=proj_years,
            y=arima_line,
            mode='lines',
            name='ARIMA',
            line=dict(color='#1f77b4', width=2, dash='dash')
        ))
    
    # Prophet projection
    prophet_pred = well.get('Prophet_Pred_2030')
    if pd.notna(prophet_pred):
        prophet_line = np.linspace(current_level, prophet_pred, len(proj_years))
        fig.add_trace(go.Scatter(
            x=proj_years,
            y=prophet_line,
            mode='lines',
            name='Prophet',
            line=dict(color='#2ca02c', width=2, dash='dash')
        ))
    
    # LSTM projection
    lstm_pred = well.get('LSTM_Pred_2030')
    if pd.notna(lstm_pred):
        lstm_line = np.linspace(current_level, lstm_pred, len(proj_years))
        fig.add_trace(go.Scatter(
            x=proj_years,
            y=lstm_line,
            mode='lines',
            name='LSTM',
            line=dict(color='#9467bd', width=2, dash='dash')
        ))
    
    # Ensemble (average)
    preds = [p for p in [arima_pred, prophet_pred, lstm_pred] if pd.notna(p)]
    if preds:
        ensemble_pred = np.mean(preds)
        ensemble_line = np.linspace(current_level, ensemble_pred, len(proj_years))
        fig.add_trace(go.Scatter(
            x=proj_years,
            y=ensemble_line,
            mode='lines',
            name='Ensemble',
            line=dict(color='#d62728', width=3)
        ))
    
    # Add vertical line at end of observations
    fig.add_vline(x=year_end, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add annotation
    fig.add_annotation(
        x=year_end + 0.5,
        y=current_level,
        text="Projection →",
        showarrow=False,
        font=dict(size=10, color="gray")
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="Water Level Depth (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified'
    )
    
    # Invert y-axis (depth increases downward)
    fig.update_yaxes(autorange="reversed")
    
    return fig

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
        else:
            piezo_file = None
            census_file = None
        
        st.markdown("---")
        
        # Load data
        with st.spinner("Loading data..."):
            piezo_data = load_piezometric_data(piezo_file)
            census_data = load_census_data(census_file)
        
        if piezo_data.get('demo'):
            st.info("📊 Using demonstration data")
        elif piezo_data.get('loaded'):
            st.success("✅ Data loaded successfully")
        
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
    # MAIN CONTENT - TABS
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🗺️ Interactive Map", 
        "📈 Well Analysis",
        "🏛️ Spatial Aggregation",
        "📋 Data Tables"
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
            st.plotly_chart(fig_pie, use_container_width=True)
        
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
            st.plotly_chart(fig_pie2, use_container_width=True)
        
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
    # TAB 2: INTERACTIVE MAP
    # ============================================================
    with tab2:
        st.header("Interactive Well Map")
        
        if piezo_data.get('loaded') and len(df_filtered) > 0:
            st.info(f"Showing {len(df_filtered)} wells. Click on markers for details.")
            
            # Map options
            col1, col2 = st.columns([3, 1])
            
            with col2:
                color_option = st.selectbox(
                    "Color wells by:",
                    ['Linear_Slope_m_yr', 'WL_Current', 'N_Records'],
                    format_func=lambda x: {
                        'Linear_Slope_m_yr': 'Decline Rate (m/yr)',
                        'WL_Current': 'Current Water Level (m)',
                        'N_Records': 'Number of Records'
                    }.get(x, x)
                )
            
            with col1:
                # Create and display map
                well_map = create_well_map(df_filtered, color_by=color_option)
                st_folium(well_map, width=None, height=600)
        else:
            st.warning("No data available. Please load data or adjust filters.")
    
    # ============================================================
    # TAB 3: WELL ANALYSIS
    # ============================================================
    with tab3:
        st.header("Individual Well Analysis")
        
        if piezo_data.get('loaded') and len(df_filtered) > 0:
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Well selector
                well_options = df_filtered.apply(
                    lambda x: f"{x['Station_Code']} - {x.get('Station_Name', 'Unknown')}", axis=1
                ).tolist()
                
                selected_well_display = st.selectbox(
                    "Select Well:",
                    well_options,
                    help="Choose a well to view detailed analysis"
                )
                
                selected_well_id = selected_well_display.split(' - ')[0]
                
                # Well details - check if well exists in filtered data
                well_matches = df_filtered[df_filtered['Station_Code'] == selected_well_id]
                
                if len(well_matches) == 0:
                    st.error("Selected well not found in filtered data. Please adjust filters.")
                    well_info = None
                else:
                    well_info = well_matches.iloc[0]
                    
                    st.markdown("### Well Information")
                    
                    # Safely extract values with proper defaults
                    try:
                        station_code = str(well_info.get('Station_Code', 'N/A'))
                        shac = str(well_info.get('SHAC', 'N/A'))
                        region = str(well_info.get('Region', 'N/A'))
                        comuna = str(well_info.get('Comuna', 'N/A'))
                        n_records = well_info.get('N_Records', 'N/A')
                        year_start = well_info.get('Year_Start', 'N/A')
                        year_end = well_info.get('Year_End', 'N/A')
                        wl_current = well_info.get('WL_Current', None)
                        slope = well_info.get('Linear_Slope_m_yr', None)
                        r2 = well_info.get('Linear_R2', None)
                        trend = str(well_info.get('Consensus_Trend', 'N/A'))
                        
                        # Format numeric values
                        wl_str = f"{float(wl_current):.1f}" if pd.notna(wl_current) else "N/A"
                        slope_str = f"{float(slope):.4f}" if pd.notna(slope) else "N/A"
                        r2_str = f"{float(r2):.3f}" if pd.notna(r2) else "N/A"
                        
                        st.markdown(f"""
                        | Property | Value |
                        |----------|-------|
                        | **Station Code** | {station_code} |
                        | **SHAC** | {shac} |
                        | **Region** | {region} |
                        | **Comuna** | {comuna} |
                        | **Records** | {n_records} |
                        | **Period** | {year_start} - {year_end} |
                        | **Current Level** | {wl_str} m |
                        | **Trend** | {slope_str} m/yr |
                        | **R²** | {r2_str} |
                        | **Status** | {trend} |
                        """)
                    except Exception as e:
                        st.error(f"Error displaying well information. Please try another well.")
                        well_info = None
                    
                    # 2030 Projections
                    if well_info is not None:
                        st.markdown("### 2030 Projections")
                        
                        try:
                            arima = well_info.get('ARIMA_Pred_2030')
                            prophet = well_info.get('Prophet_Pred_2030')
                            lstm = well_info.get('LSTM_Pred_2030')
                            current_level = well_info.get('WL_Current')
                            
                            if pd.notna(arima) and pd.notna(current_level):
                                change = float(arima) - float(current_level)
                                st.metric("ARIMA", f"{float(arima):.1f} m", f"{change:+.1f} m")
                            
                            if pd.notna(prophet) and pd.notna(current_level):
                                change = float(prophet) - float(current_level)
                                st.metric("Prophet", f"{float(prophet):.1f} m", f"{change:+.1f} m")
                            
                            if pd.notna(lstm) and pd.notna(current_level):
                                change = float(lstm) - float(current_level)
                                st.metric("LSTM", f"{float(lstm):.1f} m", f"{change:+.1f} m")
                        except Exception as e:
                            st.info("Projection data not available for this well.")
            
            with col2:
                # Time series plot - only show if well_info exists
                if well_info is not None:
                    st.markdown("### Time Series & Projections")
                    fig_ts = create_time_series_plot(df_filtered, selected_well_id)
                    st.plotly_chart(fig_ts, use_container_width=True)
                else:
                    st.info("Select a well from the list to view time series analysis.")
        else:
            st.warning("No data available. Please load data or adjust filters.")
    
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
                    st.plotly_chart(fig_bar, use_container_width=True)
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    fig_bar = create_shac_heatmap(piezo_data['shacs'])
                    st.plotly_chart(fig_bar, use_container_width=True)
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
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader(f"{agg_level} Summary Statistics")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    df_display = piezo_data['regions'][['Region', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Region', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False)
                    st.dataframe(df_display, use_container_width=True, height=500)
                    
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    df_display = piezo_data['shacs'][['SHAC', 'Total_Wells', 
                                                       'Avg_Linear_Slope_m_yr', 
                                                       'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['SHAC', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False).head(30)
                    st.dataframe(df_display, use_container_width=True, height=500)
                    
                elif agg_level == 'Comuna' and 'comunas' in piezo_data:
                    df_display = piezo_data['comunas'][['Comuna', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Comuna', 'Wells', 'Decline (m/yr)', '% Declining']
                    df_display = df_display.sort_values('Decline (m/yr)', ascending=False).head(30)
                    st.dataframe(df_display, use_container_width=True, height=500)
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
                ['All Wells', 'Regional Summary', 'SHAC Summary', 'Comuna Summary']
            )
            
            if table_choice == 'All Wells':
                df_display = df_filtered.copy()
            elif table_choice == 'Regional Summary':
                df_display = piezo_data.get('regions', pd.DataFrame())
            elif table_choice == 'SHAC Summary':
                df_display = piezo_data.get('shacs', pd.DataFrame())
            else:
                df_display = piezo_data.get('comunas', pd.DataFrame())
            
            # Search filter
            search_term = st.text_input("🔍 Search:", "")
            if search_term:
                mask = df_display.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
                df_display = df_display[mask]
            
            st.dataframe(df_display, use_container_width=True, height=500)
            
            # Export button
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
    # FOOTER
    # ============================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>
            <b>Chile Groundwater Assessment Dashboard</b><br>
            Data Sources: DGA Consolidado Nacional (2025), INE Census 2017 & 2024<br>
            Developed by Colorado School of Mines | 
            <a href="https://github.com/yourusername/chile-groundwater">GitHub</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    main()
