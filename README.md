# 💧 Chile Groundwater Assessment Dashboard

Interactive dashboard for exploring Chilean groundwater extraction patterns, 
piezometric trends, and ensemble projections to 2030.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chile-groundwater.streamlit.app)

## 🌟 Features

- **Interactive Map**: Explore 474+ monitoring wells with clustering and filtering
- **Time Series Analysis**: View historical trends and 2030 projections for individual wells
- **Spatial Aggregation**: Compare regions, SHACs, and comunas
- **Data Export**: Download filtered datasets as CSV

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| Registered Wells (DGA) | 63,822 |
| Unregistered Wells (Gap) | ~154,000 |
| Wells with Declining Trend | 87.1% |
| Mean Decline Rate | 0.24 m/year |
| Critical SHACs | 102 |

## 🚀 Quick Start

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/chile-groundwater.git
cd chile-groundwater

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
