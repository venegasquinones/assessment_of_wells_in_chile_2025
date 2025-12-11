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
from streamlit_folium import st_folium, folium_static
from folium.plugins import MarkerCluster, HeatMap
import json
import os
from datetime import datetime
from scipy import stats

# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

TRANSLATIONS = {
    'es': {
        # Page config
        'page_title': "Evaluación de Aguas Subterráneas de Chile",
        'page_icon': "💧",
        
        # Main headers
        'main_header': "💧 Panel de Evaluación de Aguas Subterráneas de Chile",
        'sub_header': "Análisis Integral de Extracción, Agotamiento y Proyecciones",
        
        # Sidebar
        'controls': "🔧 Controles",
        'data_source': "📂 Fuente de Datos",
        'select_data_source': "Seleccionar fuente de datos:",
        'demo_data': "Datos de Demostración",
        'upload_files': "Subir Archivos",
        'piezometric_excel': "Excel de Análisis Piezométrico",
        'census_excel': "Excel de Comparación Censal",
        'upload_help_piezo': "Subir Groundwater_Trend_Analysis_Complete.xlsx",
        'upload_help_census': "Subir Comparacion_Censo2017_vs_Censo2024.xlsx",
        'using_demo_data': "📊 Usando datos de demostración",
        'data_loaded': "✅ Datos cargados exitosamente",
        'data_status': "**Estado de Datos:**",
        'well_history': "Historial de Pozos",
        'water_rights': "Derechos de Agua",
        'filters': "🔍 Filtros",
        'select_region': "Seleccionar Región:",
        'select_shac': "Seleccionar SHAC:",
        'trend_status': "Estado de Tendencia:",
        'decreasing': "Decreciente",
        'increasing': "Creciente",
        'stable': "Estable",
        'filtered_wells': "Pozos Filtrados",
        'last_updated': "**📅 Última Actualización:**",
        'language': "🌐 Idioma",
        'spanish': "Español",
        'english': "English",
        
        # Tabs
        'tab_overview': "📊 Resumen",
        'tab_map': "🗺️ Mapa Interactivo",
        'tab_well_analysis': "📈 Análisis de Pozos",
        'tab_spatial': "🏛️ Agregación Espacial",
        'tab_data': "📋 Tablas de Datos",
        
        # Tab 1: Overview
        'national_summary': "Estadísticas Resumen Nacional",
        'registered_wells_dga': "Pozos Registrados (DGA)",
        'unregistered_wells': "Pozos No Registrados",
        'wells_declining': "Pozos en Declive",
        'gw_dependence_change': "Cambio Dependencia AS",
        'validated_points': "Puntos de extracción validados en el registro DGA",
        'census_not_registry': "Pozos censados no en registro DGA",
        'piezometers_declining': "Piezómetros con tendencias decrecientes",
        'dependence_ratio_change': "Cambio en ratio de dependencia de aguas subterráneas",
        'extraction_sources': "Fuentes de Extracción",
        'registered_dga': "Registrados (DGA)",
        'unregistered_census': "No Registrados (Brecha Censal)",
        'total': "Total",
        'piezometric_trends': "Tendencias Piezométricas",
        'declining': "En Declive",
        'stable_rising': "Estable/En Aumento",
        'wells': "Pozos",
        'critical_areas': "Áreas Críticas Identificadas",
        'critical_regions': "Regiones Críticas",
        'critical_basins': "Cuencas Críticas",
        'critical_comunas': "Comunas Críticas",
        'critical_shacs': "SHACs Críticos",
        'pct_declining': "≥90% en declive",
        'pct_declining_75': "≥75% en declive",
        'key_findings': "Hallazgos Clave",
        'data_quality_crisis': "⚠️ Crisis de Calidad de Datos",
        'data_quality_items': [
            "10.4% de los registros DGA contienen errores de geolocalización",
            "7,233 pozos ubicados fuera del territorio chileno",
            "La base de información está fundamentalmente comprometida"
        ],
        'massive_extraction_gap': "⚠️ Brecha Masiva de Extracción",
        'extraction_gap_items': [
            "~154,000 puntos de extracción no registrados a nivel nacional",
            "70.7% de los pozos reportados en censos no están en registro DGA",
            "Concentrados en el sur húmedo y zonas periurbanas"
        ],
        'widespread_depletion': "⚠️ Agotamiento Generalizado de Acuíferos",
        'depletion_items': [
            "87.1% de los pozos monitoreados muestran tendencias decrecientes",
            "Tasa media de descenso: 0.24 m/año",
            "Descenso máximo: 4.24 m/año (insostenible)"
        ],
        'worsening_trajectory': "⚠️ Trayectoria en Deterioro",
        'trajectory_items': [
            "La dependencia de aguas subterráneas aumentó 3.6% (2017-2024)",
            "Durante la megasequía de Chile cuando se esperaba conservación",
            "Zonas periurbanas muestran aumentos >80%"
        ],
        
        # Tab 2: Map
        'interactive_map': "Mapa Interactivo de Pozos",
        'disclaimers_title': "⚠️ Descargos de Responsabilidad Importantes",
        'disclaimer_water_rights': "<b>Derechos de Agua DGA:</b> Las ubicaciones de los derechos de agua fueron procesadas mediante una unión basada en el código de expediente. Puede haber errores en la geolocalización de algunos puntos.",
        'disclaimer_census': "<b>Puntos Censo 2017 y 2024:</b> Estos puntos fueron generados usando la herramienta 'Crear Puntos Aleatorios' de ArcGIS Pro. Como esta herramienta coloca puntos aleatoriamente dentro de las unidades censales, las ubicaciones pueden no ser realistas, especialmente en áreas grandes. Se usó un radio de 5 metros debido a restricciones de alta densidad. El Censo 2017 tiene resolución de manzana/rural/urbano mientras que el Censo 2024 solo tiene resolución regional, haciendo al Censo 2017 más útil para detectar patrones de densidad y ubicación de pozos.",
        'showing_wells': "Mostrando {n} pozos piezométricos. Use el control de capas para alternar capas de datos adicionales.",
        'map_options': "Opciones del Mapa",
        'color_wells_by': "Colorear pozos por:",
        'decline_rate': "Tasa de Descenso (m/año)",
        'current_water_level': "Nivel de Agua Actual (m)",
        'number_records': "Número de Registros",
        'toggle_layers': "Alternar Capas",
        'dga_stations': "🔵 Estaciones de Monitoreo DGA",
        'dga_water_rights': "💧 Derechos de Agua DGA",
        'census_2017_wells': "🏠 Pozos Censo 2017",
        'census_2024_wells': "🏘️ Pozos Censo 2024",
        'show_dga_stations_help': "Mostrar ubicaciones de estaciones de monitoreo DGA",
        'show_water_rights_help': "Mostrar ubicaciones de derechos de agua DGA (puede tardar en cargar)",
        'show_census_2017_help': "Mostrar ubicaciones de pozos Censo 2017",
        'show_census_2024_help': "Mostrar ubicaciones de pozos Censo 2024",
        'points': "puntos",
        'no_data_available': "No hay datos disponibles. Por favor cargue datos o ajuste los filtros.",
        
        # Tab 3: Well Analysis
        'individual_well_analysis': "Análisis Individual de Pozos",
        'select_well': "Seleccionar Pozo",
        'filter_by_region': "Filtrar por Región:",
        'select_well_label': "Seleccionar Pozo:",
        'select_well_help': "Elija un pozo para ver análisis detallado de series temporales",
        'no_wells_region': "No hay pozos disponibles para la región seleccionada.",
        'well_information': "Información del Pozo",
        'station_code': "Código de Estación",
        'station_name': "Nombre de Estación",
        'region': "Región",
        'comuna': "Comuna",
        'altitude': "Altitud",
        'latitude': "Latitud",
        'longitude': "Longitud",
        'total_records': "**Registros Totales:**",
        'period': "**Período:**",
        'time_series_regression': "Series Temporales y Regresión Lineal",
        'trend': "Tendencia",
        'r2_value': "Valor R²",
        'data_points': "Puntos de Datos",
        'interpretation': "Interpretación",
        'critical_decline': "⚠️ **Descenso Crítico:** Este pozo muestra una tasa severa de descenso de {slope:.3f} m/año. A este ritmo, el nivel freático está bajando rápidamente, indicando potencial sobreextracción o recarga reducida.",
        'moderate_decline': "⚠️ **Descenso Moderado:** Este pozo muestra una tasa de descenso de {slope:.3f} m/año. Se recomienda monitoreo continuo.",
        'slight_decline': "ℹ️ **Descenso Leve:** Este pozo muestra una tasa menor de descenso de {slope:.3f} m/año. El acuífero puede estar bajo estrés leve.",
        'stable_level': "✅ **Estable:** Este pozo muestra niveles de agua relativamente estables con cambio mínimo ({slope:.3f} m/año).",
        'recovery': "✅ **Recuperación:** Este pozo muestra niveles de agua en aumento ({slope:.3f} m/año), indicando recuperación del acuífero.",
        'low_r2_note': "Nota: El bajo valor de R² indica alta variabilidad en los datos. La tendencia debe interpretarse con precaución.",
        'insufficient_data': "Datos insuficientes para generar gráfico de series temporales. Se requieren al menos 2 mediciones válidas.",
        'select_well_prompt': "Seleccione un pozo de la lista para ver el análisis de series temporales.",
        'raw_data': "Datos Crudos",
        'date': "Fecha",
        'depth_to_water': "Profundidad al Agua (m)",
        'well_name': "Nombre del Pozo",
        'altitude_m': "Altitud (m)",
        'download_well_data': "📥 Descargar Datos del Pozo como CSV",
        'well_history_not_available': "Datos de historial de pozos no disponibles. Asegúrese de que 'niveles_estaticos_pozos_historico.xlsx' esté en la carpeta de datos.",
        
        # Tab 4: Spatial Aggregation
        'spatial_aggregation': "Análisis de Agregación Espacial",
        'select_aggregation': "Seleccionar nivel de agregación:",
        'decline_rates': "Tasas de Descenso",
        'summary_statistics': "Estadísticas Resumen",
        'regional_decline_rates': "Tasas Regionales de Descenso de Aguas Subterráneas",
        'mean_decline_rate': "Tasa Media de Descenso (m/año)",
        'top_20_shacs': "Top 20 SHACs Críticos por Tasa de Descenso",
        'top_15_comunas': "Top 15 Comunas por Tasa de Descenso",
        
        # Tab 5: Data Tables
        'data_tables_export': "Tablas de Datos y Exportación",
        'select_data_table': "Seleccionar tabla de datos:",
        'all_wells': "Todos los Pozos",
        'regional_summary': "Resumen Regional",
        'shac_summary': "Resumen SHAC",
        'comuna_summary': "Resumen Comuna",
        'well_history_data': "Datos de Historial de Pozos",
        'search': "🔍 Buscar:",
        'download_csv': "📥 Descargar como CSV",
        'well_history_not_loaded': "Datos de historial de pozos no cargados.",
        
        # Footer disclaimers
        'footer_disclaimers_title': "📋 Descargos de Responsabilidad y Notas Metodológicas",
        'footer_disclaimer_water_rights': "<b>Ubicaciones de Derechos de Agua DGA:</b> Las coordenadas geográficas para los derechos de agua DGA fueron procesadas mediante una unión basada en el código de expediente. Debido a la naturaleza de este proceso de unión, puede haber errores en la geolocalización de algunos puntos. Los usuarios deben verificar las coordenadas para aplicaciones críticas.",
        'footer_disclaimer_census': "<b>Ubicaciones de Pozos Censo 2017 y 2024:</b> Las ubicaciones de pozos mostradas para el Censo 2017 y Censo 2024 fueron generadas usando la herramienta 'Crear Puntos Aleatorios' en ArcGIS Pro. Como esta herramienta coloca puntos aleatoriamente dentro de las unidades geográficas censales, los puntos pueden estar ubicados en áreas no realistas, especialmente al evaluar áreas grandes. Se usó un radio de 5 metros entre puntos artificiales de pozos; aumentar el radio resultaría en no poder ajustar todos los pozos debido a restricciones de densidad. El Censo 2024 solo tiene resolución a nivel regional, mientras que el Censo 2017 tiene resolución de manzana/rural/urbano. Por lo tanto, el Censo 2017 es más útil para detectar la densidad y ubicación de hogares con pozos a mayor resolución.",
        'footer_disclaimer_verification': "<b>Verificación de Datos:</b> Todos los valores presentados en este panel deben ser corroborados con fuentes primarias antes de usar en la toma de decisiones. Este análisis es parte de un estudio científico en curso.",
        'scientific_paper': "📄 Artículo Científico:",
        'paper_link_text': "Para metodología completa y análisis detallado, por favor consulte la publicación científica asociada:",
        'paper_coming_soon': "[Enlace al artículo - Próximamente]",
        'footer_credits': "Data Sources: DGA Consolidado Nacional (2025), INE Censo 2017 & 2024<br>Desarrollado por Colorado School of Mines",
        
        # Map legend
        'layer_legend': "Leyenda de Capas",
        'high_decline': "Alto Descenso",
        'moderate': "Moderado",
        'low_recovery': "Bajo/Recuperación",
        'dga_stations_legend': "Estaciones DGA",
        'water_rights_legend': "Derechos de Agua",
        'census_2017_legend': "Censo 2017",
        'census_2024_legend': "Censo 2024",
        
        # Popup content
        'popup_shac': "SHAC",
        'popup_region': "Región",
        'popup_records': "Registros",
        'popup_current_level': "Nivel Actual",
        'popup_trend': "Tendencia",
        'popup_status': "Estado",
        'popup_dga_station': "🔵 Estación DGA",
        'popup_name': "Nombre",
        'popup_code': "Código",
        'popup_altitude': "Altitud",
        'popup_water_right': "💧 Derecho de Agua",
        'popup_expediente': "Expediente",
        'popup_annual_flow': "Caudal Anual",
        
        # Plot labels
        'observations': "Observaciones",
        'linear_trend': "Tendencia Lineal",
        'year': "Año",
        'water_level_depth': "Profundidad del Nivel de Agua (m)",
        'declining_deepening': "📈 En declive (nivel bajando)",
        'recovering_rising': "📉 Recuperando (nivel subiendo)",
        'stable_status': "➡️ Estable",
        'trend_label': "Tendencia",
        'status_label': "Estado",
        
        # Misc
        'all': "Todos",
        'property': "Propiedad",
        'value': "Valor",
        'm_year': "m/año",
        'm': "m",
    },
    
    'en': {
        # Page config
        'page_title': "Chile Groundwater Assessment",
        'page_icon': "💧",
        
        # Main headers
        'main_header': "💧 Chile Groundwater Assessment Dashboard",
        'sub_header': "Comprehensive Analysis of Extraction, Depletion, and Projections",
        
        # Sidebar
        'controls': "🔧 Controls",
        'data_source': "📂 Data Source",
        'select_data_source': "Select data source:",
        'demo_data': "Demo Data",
        'upload_files': "Upload Files",
        'piezometric_excel': "Piezometric Analysis Excel",
        'census_excel': "Census Comparison Excel",
        'upload_help_piezo': "Upload Groundwater_Trend_Analysis_Complete.xlsx",
        'upload_help_census': "Upload Comparacion_Censo2017_vs_Censo2024.xlsx",
        'using_demo_data': "📊 Using demonstration data",
        'data_loaded': "✅ Data loaded successfully",
        'data_status': "**Data Status:**",
        'well_history': "Well History",
        'water_rights': "Water Rights",
        'filters': "🔍 Filters",
        'select_region': "Select Region:",
        'select_shac': "Select SHAC:",
        'trend_status': "Trend Status:",
        'decreasing': "Decreasing",
        'increasing': "Increasing",
        'stable': "Stable",
        'filtered_wells': "Filtered Wells",
        'last_updated': "**📅 Last Updated:**",
        'language': "🌐 Language",
        'spanish': "Español",
        'english': "English",
        
        # Tabs
        'tab_overview': "📊 Overview",
        'tab_map': "🗺️ Interactive Map",
        'tab_well_analysis': "📈 Well Analysis",
        'tab_spatial': "🏛️ Spatial Aggregation",
        'tab_data': "📋 Data Tables",
        
        # Tab 1: Overview
        'national_summary': "National Summary Statistics",
        'registered_wells_dga': "Registered Wells (DGA)",
        'unregistered_wells': "Unregistered Wells",
        'wells_declining': "Wells Declining",
        'gw_dependence_change': "GW Dependence Change",
        'validated_points': "Validated extraction points in DGA registry",
        'census_not_registry': "Census wells not in DGA registry",
        'piezometers_declining': "Piezometers with declining trends",
        'dependence_ratio_change': "Change in groundwater dependence ratio",
        'extraction_sources': "Extraction Sources",
        'registered_dga': "Registered (DGA)",
        'unregistered_census': "Unregistered (Census Gap)",
        'total': "Total",
        'piezometric_trends': "Piezometric Trends",
        'declining': "Declining",
        'stable_rising': "Stable/Rising",
        'wells': "Wells",
        'critical_areas': "Critical Areas Identified",
        'critical_regions': "Critical Regions",
        'critical_basins': "Critical Basins",
        'critical_comunas': "Critical Comunas",
        'critical_shacs': "Critical SHACs",
        'pct_declining': "≥90% declining",
        'pct_declining_75': "≥75% declining",
        'key_findings': "Key Findings",
        'data_quality_crisis': "⚠️ Data Quality Crisis",
        'data_quality_items': [
            "10.4% of DGA records contain geolocation errors",
            "7,233 wells plotted outside Chilean territory",
            "Information base is fundamentally compromised"
        ],
        'massive_extraction_gap': "⚠️ Massive Extraction Gap",
        'extraction_gap_items': [
            "~154,000 unregistered extraction points nationally",
            "70.7% of census-reported wells not in DGA registry",
            "Concentrated in humid south and peri-urban zones"
        ],
        'widespread_depletion': "⚠️ Widespread Aquifer Depletion",
        'depletion_items': [
            "87.1% of monitored wells show declining trends",
            "Mean decline rate: 0.24 m/year",
            "Maximum decline: 4.24 m/year (unsustainable)"
        ],
        'worsening_trajectory': "⚠️ Worsening Trajectory",
        'trajectory_items': [
            "Groundwater dependence increased 3.6% (2017-2024)",
            "During Chile's megadrought when conservation expected",
            "Peri-urban zones show >80% increases"
        ],
        
        # Tab 2: Map
        'interactive_map': "Interactive Well Map",
        'disclaimers_title': "⚠️ Important Disclaimers",
        'disclaimer_water_rights': "<b>DGA Water Rights:</b> The water rights locations were processed by performing a join based on the expediente code. There may be errors in the geolocation of some points.",
        'disclaimer_census': "<b>Census 2017 & 2024 Points:</b> These points were generated using the 'Create Random Points' tool in ArcGIS Pro. Since this tool places points randomly within census units, locations may not be realistic, especially in larger areas. The 5-meter radius was used due to high density constraints. Census 2017 has block/rural/urban resolution while Census 2024 only has regional resolution, making Census 2017 more useful for detecting well density and location patterns.",
        'showing_wells': "Showing {n} piezometric wells. Use the layer control to toggle additional data layers.",
        'map_options': "Map Options",
        'color_wells_by': "Color wells by:",
        'decline_rate': "Decline Rate (m/yr)",
        'current_water_level': "Current Water Level (m)",
        'number_records': "Number of Records",
        'toggle_layers': "Toggle Layers",
        'dga_stations': "🔵 DGA Monitoring Stations",
        'dga_water_rights': "💧 DGA Water Rights",
        'census_2017_wells': "🏠 Census 2017 Wells",
        'census_2024_wells': "🏘️ Census 2024 Wells",
        'show_dga_stations_help': "Show DGA monitoring station locations",
        'show_water_rights_help': "Show DGA water rights locations (may take time to load)",
        'show_census_2017_help': "Show Census 2017 well locations",
        'show_census_2024_help': "Show Census 2024 well locations",
        'points': "points",
        'no_data_available': "No data available. Please load data or adjust filters.",
        
        # Tab 3: Well Analysis
        'individual_well_analysis': "Individual Well Analysis",
        'select_well': "Select Well",
        'filter_by_region': "Filter by Region:",
        'select_well_label': "Select Well:",
        'select_well_help': "Choose a well to view detailed time series analysis",
        'no_wells_region': "No wells available for the selected region.",
        'well_information': "Well Information",
        'station_code': "Station Code",
        'station_name': "Station Name",
        'region': "Region",
        'comuna': "Comuna",
        'altitude': "Altitude",
        'latitude': "Latitude",
        'longitude': "Longitude",
        'total_records': "**Total Records:**",
        'period': "**Period:**",
        'time_series_regression': "Time Series & Linear Regression",
        'trend': "Trend",
        'r2_value': "R² Value",
        'data_points': "Data Points",
        'interpretation': "Interpretation",
        'critical_decline': "⚠️ **Critical Decline:** This well shows a severe decline rate of {slope:.3f} m/year. At this rate, the water table is dropping rapidly, indicating potential over-extraction or reduced recharge.",
        'moderate_decline': "⚠️ **Moderate Decline:** This well shows a decline rate of {slope:.3f} m/year. Continued monitoring is recommended.",
        'slight_decline': "ℹ️ **Slight Decline:** This well shows a minor decline rate of {slope:.3f} m/year. The aquifer may be under mild stress.",
        'stable_level': "✅ **Stable:** This well shows relatively stable water levels with minimal change ({slope:.3f} m/year).",
        'recovery': "✅ **Recovery:** This well shows rising water levels ({slope:.3f} m/year), indicating aquifer recovery.",
        'low_r2_note': "Note: The low R² value indicates high variability in the data. The trend should be interpreted with caution.",
        'insufficient_data': "Insufficient data to generate time series plot. At least 2 valid measurements are required.",
        'select_well_prompt': "Select a well from the list to view time series analysis.",
        'raw_data': "Raw Data",
        'date': "Date",
        'depth_to_water': "Depth to Water (m)",
        'well_name': "Well Name",
        'altitude_m': "Altitude (m)",
        'download_well_data': "📥 Download Well Data as CSV",
        'well_history_not_available': "Well history data not available. Please ensure 'niveles_estaticos_pozos_historico.xlsx' is in the data folder.",
        
        # Tab 4: Spatial Aggregation
        'spatial_aggregation': "Spatial Aggregation Analysis",
        'select_aggregation': "Select aggregation level:",
        'decline_rates': "Decline Rates",
        'summary_statistics': "Summary Statistics",
        'regional_decline_rates': "Regional Groundwater Decline Rates",
        'mean_decline_rate': "Mean Decline Rate (m/year)",
        'top_20_shacs': "Top 20 Critical SHACs by Decline Rate",
        'top_15_comunas': "Top 15 Comunas by Decline Rate",
        
        # Tab 5: Data Tables
        'data_tables_export': "Data Tables & Export",
        'select_data_table': "Select data table:",
        'all_wells': "All Wells",
        'regional_summary': "Regional Summary",
        'shac_summary': "SHAC Summary",
        'comuna_summary': "Comuna Summary",
        'well_history_data': "Well History Data",
        'search': "🔍 Search:",
        'download_csv': "📥 Download as CSV",
        'well_history_not_loaded': "Well history data not loaded.",
        
        # Footer disclaimers
        'footer_disclaimers_title': "📋 Data Disclaimers & Methodology Notes",
        'footer_disclaimer_water_rights': "<b>DGA Water Rights Locations:</b> The geographic coordinates for DGA water rights were processed by performing a join based on the expediente code. Due to the nature of this join process, there may be errors in the geolocation of some points. Users should verify coordinates for critical applications.",
        'footer_disclaimer_census': "<b>Census 2017 & 2024 Well Locations:</b> The well locations shown for Census 2017 and Census 2024 were generated using the 'Create Random Points' tool in ArcGIS Pro. Since this tool plots values randomly within census geographic units, points may be located in unrealistic areas, especially when assessing larger areas. A 5-meter radius between artificial well points was used; increasing the radius would result in not being able to fit all wells due to density constraints. Census 2024 has regional-level resolution only, while Census 2017 has block/rural/urban resolution. Therefore, Census 2017 is more useful for detecting the density and location of homes with wells at higher resolution.",
        'footer_disclaimer_verification': "<b>Data Verification:</b> All values presented in this dashboard should be corroborated with primary sources before use in decision-making. This analysis is part of an ongoing scientific study.",
        'scientific_paper': "📄 Scientific Paper:",
        'paper_link_text': "For complete methodology and detailed analysis, please refer to the associated scientific publication:",
        'paper_coming_soon': "[Link to paper - Coming Soon]",
        'footer_credits': "Data Sources: DGA Consolidado Nacional (2025), INE Census 2017 & 2024<br>Developed by Colorado School of Mines",
        
        # Map legend
        'layer_legend': "Layer Legend",
        'high_decline': "High Decline Wells",
        'moderate': "Moderate Decline",
        'low_recovery': "Low/Recovery",
        'dga_stations_legend': "DGA Stations",
        'water_rights_legend': "Water Rights",
        'census_2017_legend': "Census 2017",
        'census_2024_legend': "Census 2024",
        
        # Popup content
        'popup_shac': "SHAC",
        'popup_region': "Region",
        'popup_records': "Records",
        'popup_current_level': "Current Level",
        'popup_trend': "Trend",
        'popup_status': "Status",
        'popup_dga_station': "🔵 DGA Station",
        'popup_name': "Name",
        'popup_code': "Code",
        'popup_altitude': "Altitude",
        'popup_water_right': "💧 Water Right",
        'popup_expediente': "Expediente",
        'popup_annual_flow': "Annual Flow",
        
        # Plot labels
        'observations': "Observations",
        'linear_trend': "Linear Trend",
        'year': "Year",
        'water_level_depth': "Water Level Depth (m)",
        'declining_deepening': "📈 Declining (water level deepening)",
        'recovering_rising': "📉 Recovering (water level rising)",
        'stable_status': "➡️ Stable",
        'trend_label': "Trend",
        'status_label': "Status",
        
        # Misc
        'all': "All",
        'property': "Property",
        'value': "Value",
        'm_year': "m/yr",
        'm': "m",
    }
}


def get_text(key, lang='es'):
    """Get translated text for a given key"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['es']).get(key, key)


def t(key):
    """Shorthand function to get translated text using session state language"""
    lang = st.session_state.get('language', 'es')
    return get_text(key, lang)


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Chile Groundwater Assessment / Evaluación de Aguas Subterráneas",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/chile-groundwater',
        'Report a bug': 'https://github.com/yourusername/chile-groundwater/issues',
        'About': """
        # Chile Groundwater Assessment Dashboard
        # Panel de Evaluación de Aguas Subterráneas de Chile
        
        This interactive dashboard presents findings from a comprehensive 
        assessment of Chilean groundwater resources.
        
        Este panel interactivo presenta hallazgos de una evaluación 
        integral de los recursos de aguas subterráneas de Chile.
        
        **Authors / Autores**: [Your Name]
        **Institution / Institución**: Colorado School of Mines
        """
    }
)

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'es'

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
    
    return generate_demo_data()


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
    
    df_wells['ARIMA_Pred_2030'] = df_wells['WL_Current'] + df_wells['Linear_Slope_m_yr'] * 5
    df_wells['Prophet_Pred_2030'] = df_wells['ARIMA_Pred_2030'] * np.random.uniform(0.9, 1.1, n_wells)
    df_wells['LSTM_Pred_2030'] = df_wells['ARIMA_Pred_2030'] * np.random.uniform(0.85, 1.15, n_wells)
    
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
    
    # Layer names based on language
    wells_layer_name = '📍 Pozos Piezométricos' if lang == 'es' else '📍 Piezometric Wells'
    dga_layer_name = '🔵 Estaciones DGA' if lang == 'es' else '🔵 DGA Stations'
    rights_layer_name = '💧 Derechos de Agua' if lang == 'es' else '💧 Water Rights'
    census17_layer_name = '🏠 Censo 2017' if lang == 'es' else '🏠 Census 2017'
    census24_layer_name = '🏘️ Censo 2024' if lang == 'es' else '🏘️ Census 2024'
    
    # Create feature groups for layer control
    wells_layer = folium.FeatureGroup(name=wells_layer_name, show=True)
    dga_stations_layer = folium.FeatureGroup(name=dga_layer_name, show=True)
    water_rights_layer = folium.FeatureGroup(name=rights_layer_name, show=False)
    census_2017_layer = folium.FeatureGroup(name=census17_layer_name, show=False)
    census_2024_layer = folium.FeatureGroup(name=census24_layer_name, show=False)
    
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
                
                # Popup content based on language
                shac_label = "SHAC" if lang == 'es' else "SHAC"
                region_label = "Región" if lang == 'es' else "Region"
                records_label = "Registros" if lang == 'es' else "Records"
                current_label = "Nivel Actual" if lang == 'es' else "Current Level"
                trend_label = "Tendencia" if lang == 'es' else "Trend"
                status_label = "Estado" if lang == 'es' else "Status"
                
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin-bottom: 5px;">{row.get('Station_Name', row['Station_Code'])}</h4>
                    <hr style="margin: 5px 0;">
                    <b>{shac_label}:</b> {row.get('SHAC', 'N/A')}<br>
                    <b>{region_label}:</b> {row.get('Region', 'N/A')}<br>
                    <b>{records_label}:</b> {row.get('N_Records', 'N/A')}<br>
                    <b>{current_label}:</b> {row.get('WL_Current', 'N/A'):.1f} m<br>
                    <b>{trend_label}:</b> {row.get('Linear_Slope_m_yr', 'N/A'):.3f} m/año<br>
                    <b>{status_label}:</b> {row.get('Consensus_Trend', 'N/A')}
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
        unique_stations = df_stations.drop_duplicates(subset=['Station_Code'])[['Station_Code', 'Station_Name', 'Latitude', 'Longitude', 'Altitude', 'Region', 'Comuna']].copy()
        
        station_cluster = MarkerCluster().add_to(dga_stations_layer)
        
        name_label = "Nombre" if lang == 'es' else "Name"
        code_label = "Código" if lang == 'es' else "Code"
        region_label = "Región" if lang == 'es' else "Region"
        comuna_label = "Comuna" if lang == 'es' else "Comuna"
        alt_label = "Altitud" if lang == 'es' else "Altitude"
        station_title = "🔵 Estación DGA" if lang == 'es' else "🔵 DGA Station"
        
        for idx, row in unique_stations.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                popup_html = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin-bottom: 5px; color: #1976d2;">{station_title}</h4>
                    <hr style="margin: 5px 0;">
                    <b>{name_label}:</b> {row.get('Station_Name', 'N/A')}<br>
                    <b>{code_label}:</b> {row.get('Station_Code', 'N/A')}<br>
                    <b>{region_label}:</b> {row.get('Region', 'N/A')}<br>
                    <b>{comuna_label}:</b> {row.get('Comuna', 'N/A')}<br>
                    <b>{alt_label}:</b> {row.get('Altitude', 'N/A')} m
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
        
        if len(df_rights) > 5000:
            df_rights_sample = df_rights.sample(n=5000, random_state=42)
        else:
            df_rights_sample = df_rights
        
        rights_cluster = MarkerCluster().add_to(water_rights_layer)
        
        exp_label = "Expediente" if lang == 'es' else "Expediente"
        flow_label = "Caudal Anual" if lang == 'es' else "Annual Flow"
        region_label = "Región" if lang == 'es' else "Region"
        comuna_label = "Comuna" if lang == 'es' else "Comuna"
        rights_title = "💧 Derecho de Agua" if lang == 'es' else "💧 Water Right"
        
        for idx, row in df_rights_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                annual_flow = row.get('Annual_Flow', 'N/A')
                flow_unit = row.get('Flow_Unit', '')
                
                popup_html = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin-bottom: 5px; color: #7b1fa2;">{rights_title}</h4>
                    <hr style="margin: 5px 0;">
                    <b>{exp_label}:</b> {row.get('Expediente_Code', 'N/A')}<br>
                    <b>{flow_label}:</b> {annual_flow} {flow_unit}<br>
                    <b>{region_label}:</b> {row.get('Region', 'N/A')}<br>
                    <b>{comuna_label}:</b> {row.get('Comuna', 'N/A')}
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
        
        if len(df_census) > 5000:
            df_census_sample = df_census.sample(n=5000, random_state=42)
        else:
            df_census_sample = df_census
        
        census17_cluster = MarkerCluster().add_to(census_2017_layer)
        
        census_label = "Pozo Censo 2017" if lang == 'es' else "Census 2017 Well"
        
        for idx, row in df_census_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=4,
                    popup=folium.Popup(f"{census_label}<br>ID: {row.get('OID', 'N/A')}", max_width=150),
                    color='#4caf50',
                    fill=True,
                    fillColor='#4caf50',
                    fillOpacity=0.5,
                    weight=1
                ).add_to(census17_cluster)
    
    # Add Census 2024 layer
    if show_census_2024 and census_2024_data is not None and census_2024_data.get('loaded'):
        df_census = census_2024_data['data']
        
        if len(df_census) > 5000:
            df_census_sample = df_census.sample(n=5000, random_state=42)
        else:
            df_census_sample = df_census
        
        census24_cluster = MarkerCluster().add_to(census_2024_layer)
        
        census_label = "Pozo Censo 2024" if lang == 'es' else "Census 2024 Well"
        
        for idx, row in df_census_sample.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=4,
                    popup=folium.Popup(f"{census_label}<br>ID: {row.get('OID', 'N/A')}", max_width=150),
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
    
    # Legend labels based on language
    legend_title = "Leyenda de Capas" if lang == 'es' else "Layer Legend"
    high_decline = "Alto Descenso" if lang == 'es' else "High Decline"
    moderate = "Moderado" if lang == 'es' else "Moderate"
    low_recovery = "Bajo/Recuperación" if lang == 'es' else "Low/Recovery"
    dga_stations_leg = "Estaciones DGA" if lang == 'es' else "DGA Stations"
    water_rights_leg = "Derechos de Agua" if lang == 'es' else "Water Rights"
    census_2017_leg = "Censo 2017" if lang == 'es' else "Census 2017"
    census_2024_leg = "Censo 2024" if lang == 'es' else "Census 2024"
    
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial; font-size: 11px;">
        <b>{legend_title}</b><br>
        <i style="background: red; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {high_decline}<br>
        <i style="background: orange; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {moderate}<br>
        <i style="background: blue; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {low_recovery}<br>
        <i style="background: #1976d2; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {dga_stations_leg}<br>
        <i style="background: #7b1fa2; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {water_rights_leg}<br>
        <i style="background: #4caf50; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {census_2017_leg}<br>
        <i style="background: #ff9800; width: 12px; height: 12px; 
                  display: inline-block; border-radius: 50%;"></i> {census_2024_leg}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def create_well_time_series_with_regression(df_well_data, well_id, well_name, lang='es'):
    """Create time series plot for a selected well with linear regression"""
    
    df_well = df_well_data[df_well_data['Station_Code'] == well_id].copy()
    df_well = df_well.dropna(subset=['Date', 'Water_Level'])
    df_well = df_well.sort_values('Date')
    
    if len(df_well) < 2:
        return None, None, None, None
    
    df_well['Days'] = (df_well['Date'] - df_well['Date'].min()).dt.days
    df_well['Years'] = df_well['Days'] / 365.25
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_well['Days'].values, 
        df_well['Water_Level'].values
    )
    
    slope_per_year = slope * 365.25
    r_squared = r_value ** 2
    
    fig = make_subplots(rows=1, cols=1)
    
    # Labels based on language
    obs_label = "Observaciones" if lang == 'es' else "Observations"
    trend_label = "Tendencia Lineal" if lang == 'es' else "Linear Trend"
    date_label = "Fecha" if lang == 'es' else "Date"
    depth_label = "Profundidad" if lang == 'es' else "Depth"
    
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=df_well['Water_Level'],
        mode='markers',
        name=obs_label,
        marker=dict(color='#2166ac', size=8, opacity=0.7),
        hovertemplate=f'<b>{date_label}:</b> %{{x|%Y-%m-%d}}<br><b>{depth_label}:</b> %{{y:.2f}} m<extra></extra>'
    ))
    
    x_reg = df_well['Date'].values
    y_reg = intercept + slope * df_well['Days'].values
    
    fig.add_trace(go.Scatter(
        x=df_well['Date'],
        y=y_reg,
        mode='lines',
        name=f'{trend_label} ({slope_per_year:+.3f} m/año)',
        line=dict(color='#d62728', width=3, dash='solid'),
        hovertemplate=f'<b>{trend_label}:</b> %{{y:.2f}} m<extra></extra>'
    ))
    
    # Determine trend status
    if slope_per_year > 0.05:
        if lang == 'es':
            trend_status = "📈 En declive (nivel bajando)"
        else:
            trend_status = "📈 Declining (water level deepening)"
        trend_color = "#d32f2f"
    elif slope_per_year < -0.05:
        if lang == 'es':
            trend_status = "📉 Recuperando (nivel subiendo)"
        else:
            trend_status = "📉 Recovering (water level rising)"
        trend_color = "#4caf50"
    else:
        if lang == 'es':
            trend_status = "➡️ Estable"
        else:
            trend_status = "➡️ Stable"
        trend_color = "#ff9800"
    
    trend_text = "Tendencia" if lang == 'es' else "Trend"
    status_text = "Estado" if lang == 'es' else "Status"
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>{trend_text}:</b> {slope_per_year:+.4f} m/año<br><b>R²:</b> {r_squared:.4f}<br><b>{status_text}:</b> {trend_status}",
        showarrow=False,
        font=dict(size=12, color=trend_color),
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=trend_color,
        borderwidth=2,
        borderpad=4
    )
    
    pozo_label = "Pozo" if lang == 'es' else "Well"
    fecha_label = "Fecha" if lang == 'es' else "Date"
    prof_label = "Profundidad del Nivel de Agua (m)" if lang == 'es' else "Depth to Water Level (m)"
    
    fig.update_layout(
        title=dict(
            text=f"{pozo_label}: {well_name} ({well_id})",
            font=dict(size=16)
        ),
        height=500,
        xaxis_title=fecha_label,
        yaxis_title=prof_label,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='closest'
    )
    
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
        text=[f"{x:.2f} m/año" for x in df_sorted['Avg_Linear_Slope_m_yr']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Tasa de Descenso: %{x:.3f} m/año<extra></extra>' if lang == 'es' else '<b>%{y}</b><br>Decline Rate: %{x:.3f} m/yr<extra></extra>'
    ))
    
    fig.add_vline(x=0, line_color="black", line_width=1)
    
    title = "Tasas Regionales de Descenso de Aguas Subterráneas" if lang == 'es' else "Regional Groundwater Decline Rates"
    xaxis_title = "Tasa Media de Descenso (m/año)" if lang == 'es' else "Mean Decline Rate (m/year)"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        height=500,
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    return fig


def create_shac_heatmap(df_shacs, lang='es'):
    """Create heatmap of SHAC metrics"""
    
    df_top = df_shacs.nlargest(20, 'Avg_Linear_Slope_m_yr')
    
    fig = go.Figure()
    
    colorbar_title = "% En Declive" if lang == 'es' else "% Declining"
    
    fig.add_trace(go.Bar(
        y=df_top['SHAC'],
        x=df_top['Avg_Linear_Slope_m_yr'],
        orientation='h',
        marker=dict(
            color=df_top['Pct_Decreasing_Consensus'],
            colorscale='Reds',
            colorbar=dict(title=colorbar_title)
        ),
        text=[f"{x:.2f}" for x in df_top['Avg_Linear_Slope_m_yr']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Descenso: %{x:.3f} m/año<br>% En Declive: %{marker.color:.1f}%<extra></extra>' if lang == 'es' else '<b>%{y}</b><br>Decline: %{x:.3f} m/yr<br>% Declining: %{marker.color:.1f}%<extra></extra>'
    ))
    
    title = "Top 20 SHACs Críticos por Tasa de Descenso" if lang == 'es' else "Top 20 Critical SHACs by Decline Rate"
    xaxis_title = "Tasa Media de Descenso (m/año)" if lang == 'es' else "Mean Decline Rate (m/year)"
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
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
    # SIDEBAR - LANGUAGE SELECTOR AT TOP
    # ============================================================
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/78/Flag_of_Chile.svg", width=100)
        
        # Language selector
        st.markdown("---")
        st.subheader(t('language'))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇪🇸 Español", use_container_width=True, 
                        type="primary" if st.session_state.language == 'es' else "secondary"):
                st.session_state.language = 'es'
                st.rerun()
        with col2:
            if st.button("🇬🇧 English", use_container_width=True,
                        type="primary" if st.session_state.language == 'en' else "secondary"):
                st.session_state.language = 'en'
                st.rerun()
        
        st.markdown("---")
        
        st.title(t('controls'))
        
        st.markdown("---")
        
        # File upload option
        st.subheader(t('data_source'))
        
        data_source = st.radio(
            t('select_data_source'),
            [t('demo_data'), t('upload_files')],
            help="Use demo data or upload your own Excel files" if st.session_state.language == 'en' else "Use datos de demostración o suba sus propios archivos Excel"
        )
        
        if data_source == t('upload_files'):
            piezo_file = st.file_uploader(
                t('piezometric_excel'),
                type=['xlsx'],
                help=t('upload_help_piezo')
            )
            census_file = st.file_uploader(
                t('census_excel'),
                type=['xlsx'],
                help=t('upload_help_census')
            )
        else:
            piezo_file = None
            census_file = None
        
        st.markdown("---")
        
        # Load data
        with st.spinner("Loading data..." if st.session_state.language == 'en' else "Cargando datos..."):
            piezo_data = load_piezometric_data(piezo_file)
            census_data = load_census_data(census_file)
            well_history_data = load_well_history_data()
            dga_water_rights = load_dga_water_rights()
            census_2017_points = load_census_points(2017)
            census_2024_points = load_census_points(2024)
        
        if piezo_data.get('demo'):
            st.info(t('using_demo_data'))
        elif piezo_data.get('loaded'):
            st.success(t('data_loaded'))
        
        # Show data loading status
        st.markdown(t('data_status'))
        st.write(f"- {t('well_history')}: {'✅' if well_history_data.get('loaded') else '❌'}")
        st.write(f"- {t('water_rights')}: {'✅' if dga_water_rights.get('loaded') else '❌'}")
        st.write(f"- Censo 2017: {'✅' if census_2017_points.get('loaded') else '❌'}")
        st.write(f"- Censo 2024: {'✅' if census_2024_points.get('loaded') else '❌'}")
        
        st.markdown("---")
        
        # Filters
        st.subheader(t('filters'))
        
        if piezo_data.get('loaded'):
            df_wells = piezo_data['wells']
            
            # Region filter
            regions = [t('all')] + sorted(df_wells['Region'].dropna().unique().tolist())
            selected_region = st.selectbox(t('select_region'), regions)
            
            # SHAC filter
            if selected_region != t('all'):
                available_shacs = df_wells[df_wells['Region'] == selected_region]['SHAC'].dropna().unique()
            else:
                available_shacs = df_wells['SHAC'].dropna().unique()
            
            shacs = [t('all')] + sorted(available_shacs.tolist())
            selected_shac = st.selectbox(t('select_shac'), shacs)
            
            # Trend filter
            trend_options = [t('decreasing'), t('increasing'), t('stable')]
            trend_filter = st.multiselect(
                t('trend_status'),
                trend_options,
                default=trend_options
            )
            
            # Map trend filter back to English for data filtering
            trend_map = {
                t('decreasing'): 'Decreasing',
                t('increasing'): 'Increasing',
                t('stable'): 'Stable'
            }
            trend_filter_en = [trend_map.get(tf, tf) for tf in trend_filter]
            
            # Apply filters
            df_filtered = df_wells.copy()
            if selected_region != t('all'):
                df_filtered = df_filtered[df_filtered['Region'] == selected_region]
            if selected_shac != t('all'):
                df_filtered = df_filtered[df_filtered['SHAC'] == selected_shac]
            if trend_filter_en:
                df_filtered = df_filtered[df_filtered['Consensus_Trend'].isin(trend_filter_en)]
            
            st.metric(t('filtered_wells'), len(df_filtered))
        else:
            df_filtered = pd.DataFrame()
        
        st.markdown("---")
        st.markdown(t('last_updated') + " " + datetime.now().strftime("%Y-%m-%d"))
    
    # ============================================================
    # HEADER
    # ============================================================
    st.markdown(f'<div class="main-header">{t("main_header")}</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t("sub_header")}</div>', 
                unsafe_allow_html=True)
    
    # ============================================================
    # MAIN CONTENT - TABS
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t('tab_overview'), 
        t('tab_map'), 
        t('tab_well_analysis'),
        t('tab_spatial'),
        t('tab_data')
    ])
    
    # ============================================================
    # TAB 1: OVERVIEW / DASHBOARD
    # ============================================================
    with tab1:
        st.header(t('national_summary'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=t('registered_wells_dga'),
                value="63,822",
                delta=None,
                help=t('validated_points')
            )
        
        with col2:
            st.metric(
                label=t('unregistered_wells'),
                value="~154,000",
                delta="+70.7%",
                delta_color="inverse",
                help=t('census_not_registry')
            )
        
        with col3:
            st.metric(
                label=t('wells_declining'),
                value="87.1%",
                delta="-413 " + t('wells').lower(),
                delta_color="inverse",
                help=t('piezometers_declining')
            )
        
        with col4:
            st.metric(
                label=t('gw_dependence_change'),
                value="+3.6%",
                delta="2017→2024",
                delta_color="inverse",
                help=t('dependence_ratio_change')
            )
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader(t('extraction_sources'))
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=[t('registered_dga'), t('unregistered_census')],
                values=[63822, 153580],
                hole=0.4,
                marker_colors=['#2166ac', '#d62728'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_pie.update_layout(
                height=350,
                showlegend=False,
                annotations=[dict(text=f'217K<br>{t("total")}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_right:
            st.subheader(t('piezometric_trends'))
            
            fig_pie2 = go.Figure(data=[go.Pie(
                labels=[t('declining'), t('stable_rising')],
                values=[413, 61],
                hole=0.4,
                marker_colors=['#d62728', '#2ca02c'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_pie2.update_layout(
                height=350,
                showlegend=False,
                annotations=[dict(text=f'474<br>{t("wells")}', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig_pie2, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader(t('critical_areas'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: #ffebee; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #d32f2f; margin: 0;">5</h1>
                <p style="margin: 5px 0 0 0;"><b>{t('critical_regions')}</b></p>
                <small>{t('pct_declining')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #ff6f00; margin: 0;">25</h1>
                <p style="margin: 5px 0 0 0;"><b>{t('critical_basins')}</b></p>
                <small>{t('pct_declining_75')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: #f3e5f5; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #7b1fa2; margin: 0;">109</h1>
                <p style="margin: 5px 0 0 0;"><b>{t('critical_comunas')}</b></p>
                <small>{t('pct_declining_75')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #1976d2; margin: 0;">102</h1>
                <p style="margin: 5px 0 0 0;"><b>{t('critical_shacs')}</b></p>
                <small>{t('pct_declining_75')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader(t('key_findings'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            items_dq = t('data_quality_items')
            st.markdown(f"""
            <div class="critical-box">
                <h4>{t('data_quality_crisis')}</h4>
                <ul>
                    <li>{items_dq[0]}</li>
                    <li>{items_dq[1]}</li>
                    <li>{items_dq[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            items_eg = t('extraction_gap_items')
            st.markdown(f"""
            <div class="critical-box">
                <h4>{t('massive_extraction_gap')}</h4>
                <ul>
                    <li>{items_eg[0]}</li>
                    <li>{items_eg[1]}</li>
                    <li>{items_eg[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            items_dep = t('depletion_items')
            st.markdown(f"""
            <div class="critical-box">
                <h4>{t('widespread_depletion')}</h4>
                <ul>
                    <li>{items_dep[0]}</li>
                    <li>{items_dep[1]}</li>
                    <li>{items_dep[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            items_tr = t('trajectory_items')
            st.markdown(f"""
            <div class="critical-box">
                <h4>{t('worsening_trajectory')}</h4>
                <ul>
                    <li>{items_tr[0]}</li>
                    <li>{items_tr[1]}</li>
                    <li>{items_tr[2]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 2: INTERACTIVE MAP
    # ============================================================
    with tab2:
        st.header(t('interactive_map'))
        
        # Disclaimers
        st.markdown(f"""
        <div class="disclaimer-box">
            <h4>{t('disclaimers_title')}</h4>
            <ul>
                <li>{t('disclaimer_water_rights')}</li>
                <li>{t('disclaimer_census')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if piezo_data.get('loaded') and len(df_filtered) > 0:
            st.info(t('showing_wells').format(n=len(df_filtered)))
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader(t('map_options'))
                
                color_options = {
                    'Linear_Slope_m_yr': t('decline_rate'),
                    'WL_Current': t('current_water_level'),
                    'N_Records': t('number_records')
                }
                
                color_option = st.selectbox(
                    t('color_wells_by'),
                    list(color_options.keys()),
                    format_func=lambda x: color_options[x]
                )
                
                st.markdown("---")
                st.subheader(t('toggle_layers'))
                
                show_dga_stations = st.checkbox(
                    t('dga_stations'),
                    value=True,
                    help=t('show_dga_stations_help')
                )
                
                show_water_rights = st.checkbox(
                    t('dga_water_rights'),
                    value=False,
                    help=t('show_water_rights_help')
                )
                
                show_census_2017 = st.checkbox(
                    t('census_2017_wells'),
                    value=False,
                    help=t('show_census_2017_help')
                )
                
                show_census_2024 = st.checkbox(
                    t('census_2024_wells'),
                    value=False,
                    help=t('show_census_2024_help')
                )
                
                if show_water_rights and dga_water_rights.get('loaded'):
                    st.caption(f"{t('water_rights')}: {len(dga_water_rights['data']):,} {t('points')}")
                
                if show_census_2017 and census_2017_points.get('loaded'):
                    st.caption(f"Censo 2017: {len(census_2017_points['data']):,} {t('points')}")
                
                if show_census_2024 and census_2024_points.get('loaded'):
                    st.caption(f"Censo 2024: {len(census_2024_points['data']):,} {t('points')}")
            
            with col1:
                well_map = create_well_map(
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
                    lang=st.session_state.language
                )
                st_folium(well_map, width=None, height=600)
        else:
            st.warning(t('no_data_available'))
    
    # ============================================================
    # TAB 3: WELL ANALYSIS
    # ============================================================
    with tab3:
        st.header(t('individual_well_analysis'))
        
        if well_history_data.get('loaded'):
            df_history = well_history_data['data']
            
            unique_wells = df_history.drop_duplicates(subset=['Station_Code'])[['Station_Code', 'Station_Name', 'Region', 'Comuna', 'Altitude', 'Latitude', 'Longitude']].copy()
            unique_wells = unique_wells.sort_values('Station_Name')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(t('select_well'))
                
                regions_available = [t('all')] + sorted(unique_wells['Region'].dropna().unique().tolist())
                selected_region_wells = st.selectbox(
                    t('filter_by_region'),
                    regions_available,
                    key="well_analysis_region"
                )
                
                if selected_region_wells != t('all'):
                    wells_in_region = unique_wells[unique_wells['Region'] == selected_region_wells]
                else:
                    wells_in_region = unique_wells
                
                well_options = wells_in_region.apply(
                    lambda x: f"{x['Station_Name']} ({x['Station_Code']})", axis=1
                ).tolist()
                
                if len(well_options) == 0:
                    st.warning(t('no_wells_region'))
                    selected_well_display = None
                else:
                    selected_well_display = st.selectbox(
                        t('select_well_label'),
                        well_options,
                        help=t('select_well_help')
                    )
                
                # Robust extraction of well code and information
                if selected_well_display:
                    try:
                        # Extract code robustly: "Name (Code)"
                        parts = selected_well_display.rpartition('(')
                        selected_well_name = parts[0].strip()
                        selected_well_code = parts[2].replace(')', '').strip()
                        
                        well_subset = unique_wells[unique_wells['Station_Code'] == selected_well_code]
                        
                        if not well_subset.empty:
                            well_info = well_subset.iloc[0]
                            
                            st.markdown(f"### {t('well_information')}")
                            
                            st.markdown(f"""
                            | {t('property')} | {t('value')} |
                            |----------|-------|
                            | **{t('station_code')}** | {well_info['Station_Code']} |
                            | **{t('station_name')}** | {well_info['Station_Name']} |
                            | **{t('region')}** | {well_info.get('Region', 'N/A')} |
                            | **{t('comuna')}** | {well_info.get('Comuna', 'N/A')} |
                            | **{t('altitude')}** | {well_info.get('Altitude', 'N/A')} m |
                            | **{t('latitude')}** | {well_info.get('Latitude', 'N/A'):.6f} |
                            | **{t('longitude')}** | {well_info.get('Longitude', 'N/A'):.6f} |
                            """)
                            
                            well_records = df_history[df_history['Station_Code'] == selected_well_code]
                            st.markdown(f"{t('total_records')} {len(well_records)}")
                            
                            if len(well_records) > 0:
                                min_date = well_records['Date'].min()
                                max_date = well_records['Date'].max()
                                if pd.notna(min_date) and pd.notna(max_date):
                                    st.markdown(f"{t('period')} {min_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}")
                        else:
                            st.warning(f"Well information not found for code: {selected_well_code}")
                            selected_well_display = None # Prevents graph rendering
                    except Exception as e:
                        st.error(f"Error processing well selection: {str(e)}")
                        selected_well_display = None
            
            with col2:
                if selected_well_display:
                    st.subheader(t('time_series_regression'))
                    
                    fig_ts, slope, r2, n_points = create_well_time_series_with_regression(
                        df_history, 
                        selected_well_code, 
                        selected_well_name,
                        lang=st.session_state.language
                    )
                    
                    if fig_ts is not None:
                        st.plotly_chart(fig_ts, use_container_width=True)
                        
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            trend_text = "Declining" if slope > 0 else "Recovering"
                            if st.session_state.language == 'es':
                                trend_text = "Decreciente" if slope > 0 else "Recuperando"
                                
                            st.metric(t('trend'), f"{slope:+.4f} {t('m_year')}", delta=trend_text, delta_color="inverse" if slope > 0 else "normal")
                        
                        with col_b:
                            st.metric(t('r2_value'), f"{r2:.4f}")
                        
                        with col_c:
                            st.metric(t('data_points'), n_points)
                        
                        st.markdown("---")
                        st.markdown(f"### {t('interpretation')}")
                        
                        if slope > 0.5:
                            st.error(t('critical_decline').format(slope=slope))
                        elif slope > 0.1:
                            st.warning(t('moderate_decline').format(slope=slope))
                        elif slope > 0:
                            st.info(t('slight_decline').format(slope=slope))
                        elif slope > -0.1:
                            st.success(t('stable_level').format(slope=slope))
                        else:
                            st.success(t('recovery').format(slope=slope))
                        
                        if r2 < 0.3:
                            st.caption(t('low_r2_note'))
                    else:
                        st.warning(t('insufficient_data'))
                else:
                    st.info(t('select_well_prompt'))
            
            if selected_well_display:
                st.markdown("---")
                st.subheader(t('raw_data'))
                
                well_data_display = df_history[df_history['Station_Code'] == selected_well_code][
                    ['Date', 'Water_Level', 'Station_Name', 'Altitude']
                ].sort_values('Date', ascending=False)
                
                well_data_display['Date'] = well_data_display['Date'].dt.strftime('%Y-%m-%d')
                well_data_display = well_data_display.rename(columns={
                    'Date': t('date'),
                    'Water_Level': t('depth_to_water'),
                    'Station_Name': t('well_name'),
                    'Altitude': t('altitude_m')
                })
                
                st.dataframe(well_data_display, use_container_width=True, height=300)
                
                csv = well_data_display.to_csv(index=False)
                st.download_button(
                    label=t('download_well_data'),
                    data=csv,
                    file_name=f"well_{selected_well_code}_data.csv",
                    mime="text/csv"
                )
        else:
            st.warning(t('well_history_not_available'))
    
    # ============================================================
    # TAB 4: SPATIAL AGGREGATION
    # ============================================================
    with tab4:
        st.header(t('spatial_aggregation'))
        
        if piezo_data.get('loaded'):
            
            agg_level = st.radio(
                t('select_aggregation'),
                ['Region', 'SHAC', 'Comuna'],
                horizontal=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{agg_level} - {t('decline_rates')}")
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    fig_bar = create_regional_comparison_plot(piezo_data['regions'], lang=st.session_state.language)
                    st.plotly_chart(fig_bar, use_container_width=True)
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    fig_bar = create_shac_heatmap(piezo_data['shacs'], lang=st.session_state.language)
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
                    
                    title = t('top_15_comunas')
                    xaxis = t('mean_decline_rate')
                    
                    fig.update_layout(
                        title=title,
                        xaxis_title=xaxis,
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader(f"{agg_level} - {t('summary_statistics')}")
                
                decline_col = f"Decline ({t('m_year')})"
                pct_col = "% " + t('declining')
                
                if agg_level == 'Region' and 'regions' in piezo_data:
                    df_display = piezo_data['regions'][['Region', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Region', t('wells'), decline_col, pct_col]
                    df_display = df_display.sort_values(decline_col, ascending=False)
                    st.dataframe(df_display, use_container_width=True, height=500)
                    
                elif agg_level == 'SHAC' and 'shacs' in piezo_data:
                    df_display = piezo_data['shacs'][['SHAC', 'Total_Wells', 
                                                       'Avg_Linear_Slope_m_yr', 
                                                       'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['SHAC', t('wells'), decline_col, pct_col]
                    df_display = df_display.sort_values(decline_col, ascending=False).head(30)
                    st.dataframe(df_display, use_container_width=True, height=500)
                    
                elif agg_level == 'Comuna' and 'comunas' in piezo_data:
                    df_display = piezo_data['comunas'][['Comuna', 'Total_Wells', 
                                                         'Avg_Linear_Slope_m_yr', 
                                                         'Pct_Decreasing_Consensus']].copy()
                    df_display.columns = ['Comuna', t('wells'), decline_col, pct_col]
                    df_display = df_display.sort_values(decline_col, ascending=False).head(30)
                    st.dataframe(df_display, use_container_width=True, height=500)
        else:
            st.warning(t('no_data_available'))
    
    # ============================================================
    # TAB 5: DATA TABLES
    # ============================================================
    with tab5:
        st.header(t('data_tables_export'))
        
        if piezo_data.get('loaded'):
            
            table_options = {
                'All Wells': t('all_wells'),
                'Regional Summary': t('regional_summary'),
                'SHAC Summary': t('shac_summary'),
                'Comuna Summary': t('comuna_summary'),
                'Well History Data': t('well_history_data')
            }
            
            table_key = st.selectbox(
                t('select_data_table'),
                list(table_options.keys()),
                format_func=lambda x: table_options[x]
            )
            
            if table_key == 'All Wells':
                df_display = df_filtered.copy()
            elif table_key == 'Regional Summary':
                df_display = piezo_data.get('regions', pd.DataFrame())
            elif table_key == 'SHAC Summary':
                df_display = piezo_data.get('shacs', pd.DataFrame())
            elif table_key == 'Comuna Summary':
                df_display = piezo_data.get('comunas', pd.DataFrame())
            elif table_key == 'Well History Data':
                if well_history_data.get('loaded'):
                    df_display = well_history_data['data'].copy()
                else:
                    df_display = pd.DataFrame()
                    st.warning(t('well_history_not_loaded'))
            
            # Search filter
            search_term = st.text_input(t('search'), "")
            if search_term and len(df_display) > 0:
                mask = df_display.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
                df_display = df_display[mask]
            
            st.dataframe(df_display, use_container_width=True, height=500)
            
            # Export button
            if len(df_display) > 0:
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label=t('download_csv'),
                    data=csv,
                    file_name=f"{table_key.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning(t('no_data_available'))
    
    # ============================================================
    # FOOTER WITH DISCLAIMERS
    # ============================================================
    st.markdown("---")
    
    st.markdown(f"""
    <div class="disclaimer-box">
        <h4>{t('footer_disclaimers_title')}</h4>
        <ul>
            <li>{t('footer_disclaimer_water_rights')}</li>
            <li>{t('footer_disclaimer_census')}</li>
            <li>{t('footer_disclaimer_verification')}</li>
        </ul>
        <p><b>{t('scientific_paper')}</b> {t('paper_link_text')} <a href="#">{t('paper_coming_soon')}</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 20px;">
        <p>
            <b>{t('page_title')}</b><br>
            {t('footer_credits')} | 
            <a href="https://github.com/yourusername/chile-groundwater">GitHub</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    main()
