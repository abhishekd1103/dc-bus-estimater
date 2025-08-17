# ⚡ Data Center Electrical Bus Count Estimator

A professional-grade interactive dashboard for estimating electrical bus requirements in data center power distribution systems. Built with Streamlit for easy deployment and sharing.

## 🌐 Live Demo

**Deploy instantly on Streamlit Community Cloud:**
1. Fork this repository to your GitHub account
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repository
4. Deploy with one click!

## 🚀 Features

### Comprehensive Input Parameters
- **Flexible Starting Points**: Begin with either IT load or total facility load
- **PUE Configuration**: Industry-standard Power Usage Effectiveness settings
- **Data Center Types**: Enterprise/Colo, Hyperscale, AI/HPC with auto-adjusted defaults
- **Redundancy Tiers**: N, N+1 (Tier III), 2N (Tier IV) configurations
- **Equipment Capacities**: Customizable UPS, transformer, switchboard, and PDU blocks

### Advanced Calibration Factors
- **Geographic Climate**: Temperature-based cooling adjustments
- **Cooling Technology**: Air-cooled vs. liquid-cooled impact
- **Voltage Levels**: 2-level (MV+LV) or 3-level (HV+MV+LV) systems  
- **Backup Power**: Generator and transfer switch integration
- **Future Growth**: Expansion factor for capacity planning

### Professional Outputs
- **Detailed Breakdown**: Component-wise bus count analysis
- **Interactive Visualizations**: Pie charts and bar graphs using Plotly
- **Sensitivity Analysis**: PUE and load impact modeling
- **Validation Warnings**: Automatic checks for unrealistic results
- **Export Capabilities**: CSV and text summary downloads

## 📊 Mathematical Model

### Core Calculations

**Load Derivation:**
