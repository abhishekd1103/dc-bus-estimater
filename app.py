import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="DC Power Studies Cost Estimator | Abhishek Diwanji",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e8b57 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .developer-credit {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
    }
    .cost-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .study-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 3px solid #2e8b57;
    }
    .calibration-section {
        background: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border: 2px solid #1f4e79;
    }
</style>
""", unsafe_allow_html=True)

# Header with branding
st.markdown("""
<div class="main-header">
    <h1>⚡ Data Center Power System Studies</h1>
    <h2>Professional Cost Estimation Dashboard</h2>
    <p>Advanced Engineering Tool for Load Flow, Short Circuit, PDC & Arc Flash Studies</p>
</div>
""", unsafe_allow_html=True)

# Developer credit
st.markdown("""
<div class="developer-credit">
    🚀 Developed by <strong>Abhishek Diwanji</strong> | Power Systems Engineering Expert 
    <br>📧 Contact for Custom Solutions & Professional Consulting
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <h4>⚠️ Important Disclaimer</h4>
    <p><strong>Bus Count Estimation:</strong> This tool focuses on cost estimation for power system studies. 
    Bus count calculations are handled by a separate specialized tool which will be integrated in future versions. 
    Current bus estimates are for costing purposes only.</p>
    <p><strong>Professional Use:</strong> Results are estimates based on industry standards. 
    Always validate with qualified electrical engineers for actual project implementation.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header("📊 Project Configuration")

# Project Information
st.sidebar.subheader("🏢 Project Details")
project_name = st.sidebar.text_input("Project Name", value="Data Center Power Studies")
client_name = st.sidebar.text_input("Client Name", value="")

# Load inputs
st.sidebar.subheader("⚡ Electrical Load Parameters")
it_capacity = st.sidebar.number_input("IT Capacity (MW)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
mechanical_load = st.sidebar.number_input("Mechanical Load (MW)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
house_load = st.sidebar.number_input("House/Auxiliary Load (MW)", min_value=0.1, max_value=20.0, value=0.5, step=0.1)

# Tier and delivery
tier_level = st.sidebar.selectbox("Tier Level", ["Tier I", "Tier II", "Tier III", "Tier IV"], index=2)
delivery_type = st.sidebar.selectbox("Delivery Type", ["Standard", "Urgent"])
report_format = st.sidebar.selectbox("Report Format", ["Basic PDF", "Detailed Report with Appendices", "Client-Branded Report"], index=1)

# Studies selection
st.sidebar.subheader("📋 Studies Required")
studies_selected = {}
studies_selected['load_flow'] = st.sidebar.checkbox("Load Flow Study", value=True)
studies_selected['short_circuit'] = st.sidebar.checkbox("Short Circuit Study", value=True)
studies_selected['pdc'] = st.sidebar.checkbox("Protective Device Coordination", value=True)
studies_selected['arc_flash'] = st.sidebar.checkbox("Arc Flash Study", value=True)

# Additional parameters
client_meetings = st.sidebar.slider("Expected Client Meetings", 0, 10, 2, 1)
custom_margin = st.sidebar.slider("Custom Margin (%)", 0, 30, 15, 1)

# =============================================================================
# CALIBRATION CONTROL SECTION
# =============================================================================
st.sidebar.subheader("🔧 Calibration & Customization")

# Bus Count Calibration
bus_calibration = st.sidebar.slider(
    "Bus Count Calibration Factor", 
    min_value=0.5, max_value=2.0, value=1.0, step=0.1,
    help="Adjust bus count estimation based on historical project data"
)

# Study-wise Calibration Factors
st.sidebar.write("**Study Calibration Factors:**")
load_flow_factor = st.sidebar.slider("Load Flow Factor", 0.5, 2.0, 1.0, 0.1)
short_circuit_factor = st.sidebar.slider("Short Circuit Factor", 0.5, 2.0, 1.0, 0.1)
pdc_factor = st.sidebar.slider("PDC Factor", 0.5, 2.0, 1.0, 0.1)
arc_flash_factor = st.sidebar.slider("Arc Flash Factor", 0.5, 2.0, 1.0, 0.1)

# Level-wise Work Allocation (Customizable)
st.sidebar.write("**Resource Allocation (%):**")
senior_allocation = st.sidebar.slider("Senior Engineer %", 10, 40, 20, 1) / 100
mid_allocation = st.sidebar.slider("Mid-level Engineer %", 20, 50, 30, 1) / 100
junior_allocation = st.sidebar.slider("Junior Engineer %", 30, 70, 50, 1) / 100

# Normalize allocations to 100%
total_allocation = senior_allocation + mid_allocation + junior_allocation
if total_allocation != 1.0:
    senior_allocation = senior_allocation / total_allocation
    mid_allocation = mid_allocation / total_allocation
    junior_allocation = junior_allocation / total_allocation
    st.sidebar.info(f"Allocations normalized to 100%: Sr:{senior_allocation*100:.0f}%, Mid:{mid_allocation*100:.0f}%, Jr:{junior_allocation*100:.0f}%")

# Hourly Rates (Customizable)
st.sidebar.write("**Hourly Rates (₹):**")
senior_rate = st.sidebar.slider("Senior Engineer Rate", 800, 2000, 1200, 50)
mid_rate = st.sidebar.slider("Mid-level Engineer Rate", 400, 1000, 650, 25)
junior_rate = st.sidebar.slider("Junior Engineer Rate", 200, 600, 350, 25)

# Other Customizable Factors
meeting_cost = st.sidebar.slider("Cost per Meeting (₹)", 3000, 15000, 8000, 500)
urgency_multiplier = st.sidebar.slider("Urgent Delivery Multiplier", 1.1, 2.0, 1.3, 0.1)

# Reset calibration button
if st.sidebar.button("🔄 Reset Calibration to Defaults"):
    st.experimental_rerun()

# Study data with original logic
TIER_FACTORS = {"Tier I": 1.0, "Tier II": 1.2, "Tier III": 1.5, "Tier IV": 2.0}
BUS_PER_MW = {"Tier I": 1.5, "Tier II": 1.7, "Tier III": 2.0, "Tier IV": 2.3}

STUDIES_DATA = {
    'load_flow': {
        'name': 'Load Flow Study', 
        'base_hours_per_bus': 0.8, 
        'complexity': 'Medium', 
        'emoji': '⚡',
        'calibration_factor': load_flow_factor
    },
    'short_circuit': {
        'name': 'Short Circuit Study', 
        'base_hours_per_bus': 1.0, 
        'complexity': 'Medium-High', 
        'emoji': '⚡',
        'calibration_factor': short_circuit_factor
    },
    'pdc': {
        'name': 'Protective Device Coordination', 
        'base_hours_per_bus': 1.5, 
        'complexity': 'High', 
        'emoji': '🔧',
        'calibration_factor': pdc_factor
    },
    'arc_flash': {
        'name': 'Arc Flash Study', 
        'base_hours_per_bus': 1.2, 
        'complexity': 'High', 
        'emoji': '🔥',
        'calibration_factor': arc_flash_factor
    }
}

RATES = {
    'senior': {'hourly': senior_rate, 'allocation': senior_allocation, 'title': 'Senior Engineer/Manager'},
    'mid': {'hourly': mid_rate, 'allocation': mid_allocation, 'title': 'Mid-level Engineer'},
    'junior': {'hourly': junior_rate, 'allocation': junior_allocation, 'title': 'Junior Engineer'}
}

REPORT_MULTIPLIERS = {"Basic PDF": 1.0, "Detailed Report with Appendices": 1.8, "Client-Branded Report": 2.2}

# Calculation function (EXACT PERPLEXITY LOGIC)
def calculate_project_cost():
    # Step 1: Load derivation (Perplexity Logic)
    total_load = it_capacity + mechanical_load + house_load
    
    # Step 2: Bus count estimation with calibration (Perplexity Logic)
    estimated_buses = math.ceil(total_load * BUS_PER_MW[tier_level] * bus_calibration)
    
    results = {
        'project_info': {
            'name': project_name,
            'client': client_name,
            'total_load': total_load,
            'estimated_buses': estimated_buses,
            'tier': tier_level,
            'delivery': delivery_type,
            'report_format': report_format
        },
        'studies': {},
        'costs': {},
        'calibration_info': {
            'bus_calibration': bus_calibration,
            'study_factors': {
                'load_flow': load_flow_factor,
                'short_circuit': short_circuit_factor,
                'pdc': pdc_factor,
                'arc_flash': arc_flash_factor
            },
            'allocations': {
                'senior': senior_allocation,
                'mid': mid_allocation, 
                'junior': junior_allocation
            },
            'rates': {
                'senior': senior_rate,
                'mid': mid_rate,
                'junior': junior_rate
            }
        }
    }
    
    # Step 3: Study-wise calculations (Perplexity Logic)
    total_study_hours = 0
    total_study_cost = 0
    tier_complexity = TIER_FACTORS[tier_level]
    
    for study_key, study_data in STUDIES_DATA.items():
        if studies_selected.get(study_key, False):
            # Calculate study hours with calibration (Perplexity Logic)
            study_hours = (estimated_buses * 
                          study_data['base_hours_per_bus'] * 
                          study_data['calibration_factor'] * 
                          tier_complexity)
            
            total_study_hours += study_hours
            
            # Calculate costs by level with custom allocations
            senior_hours = study_hours * RATES['senior']['allocation']
            mid_hours = study_hours * RATES['mid']['allocation']
            junior_hours = study_hours * RATES['junior']['allocation']
            
            # Apply urgency multiplier if needed (Perplexity Logic)
            rate_multiplier = urgency_multiplier if delivery_type == "Urgent" else 1.0
            
            senior_cost = senior_hours * RATES['senior']['hourly'] * rate_multiplier
            mid_cost = mid_hours * RATES['mid']['hourly'] * rate_multiplier
            junior_cost = junior_hours * RATES['junior']['hourly'] * rate_multiplier
            
            study_total_cost = senior_cost + mid_cost + junior_cost
            total_study_cost += study_total_cost
            
            # Store study results
            results['studies'][study_key] = {
                'name': study_data['name'],
                'emoji': study_data['emoji'],
                'hours': study_hours,
                'senior_hours': senior_hours,
                'mid_hours': mid_hours,
                'junior_hours': junior_hours,
                'senior_cost': senior_cost,
                'mid_cost': mid_cost,
                'junior_cost': junior_cost,
                'total_cost': study_total_cost,
                'complexity': study_data['complexity']
            }
    
    # Step 4: Additional costs (Perplexity Logic)
    total_meeting_cost = client_meetings * meeting_cost
    report_cost = 15000 * REPORT_MULTIPLIERS[report_format]
    
    # Step 5: Total project cost calculation (Perplexity Logic)
    subtotal = total_study_cost + total_meeting_cost + report_cost
    total_cost = subtotal * (1 + custom_margin/100)
    
    results['costs'] = {
        'total_study_cost': total_study_cost,
        'meeting_cost': total_meeting_cost,
        'report_cost': report_cost,
        'subtotal': subtotal,
        'margin_amount': subtotal * (custom_margin/100),
        'total_cost': total_cost,
        'total_hours': total_study_hours
    }
    
    return results

# Calculate results
results = calculate_project_cost()

# =============================================================================
# MAIN DASHBOARD DISPLAY
# =============================================================================

# Display results
st.header("📊 Cost Analysis Results")

# Key metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">💰 Total Cost</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">₹{results['costs']['total_cost']:,.0f}</h2>
        <p style="margin: 0; color: #666;">+{custom_margin}% margin</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">⏱️ Total Hours</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['costs']['total_hours']:.0f}</h2>
        <p style="margin: 0; color: #666;">{len(results['studies'])} studies</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">🔌 Buses</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['project_info']['estimated_buses']}</h2>
        <p style="margin: 0; color: #666;">Bus Cal: {bus_calibration}x</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="cost-card">
        <h3 style="color: #1f4e79; margin: 0;">⚡ Load</h3>
        <h2 style="color: #2e8b57; margin: 5px 0;">{results['project_info']['total_load']:.1f}</h2>
        <p style="margin: 0; color: #666;">MW total</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SIMPLE PIE CHART FOR STUDY COSTS (WITHOUT PLOTLY)
# =============================================================================
if results['studies']:
    st.header("📊 Study-wise Cost Distribution")
    
    # Create pie chart data
    study_names = [study['name'] for study in results['studies'].values()]
    study_costs = [study['total_cost'] for study in results['studies'].values()]
    study_percentages = [cost/sum(study_costs)*100 for cost in study_costs]
    
    # Display pie chart using Streamlit's native chart
    pie_df = pd.DataFrame({
        'Study': study_names,
        'Cost': study_costs,
        'Percentage': study_percentages
    })
    
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        # Simple bar chart as pie chart alternative
        st.bar_chart(pie_df.set_index('Study')['Cost'])
        
    with col_data:
        st.subheader("💰 Cost Breakdown")
        for i, (name, cost, pct) in enumerate(zip(study_names, study_costs, study_percentages)):
            emoji = list(results['studies'].values())[i]['emoji']
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;">
                <strong>{emoji} {name}</strong><br>
                ₹{cost:,.0f} ({pct:.1f}%)
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# CALIBRATION STATUS DISPLAY
# =============================================================================
st.header("🔧 Current Calibration Settings")

cal_col1, cal_col2, cal_col3 = st.columns(3)

with cal_col1:
    st.markdown(f"""
    <div class="calibration-section">
        <h4>🔌 Bus Count Calibration</h4>
        <p><strong>Factor:</strong> {bus_calibration}x</p>
        <p><strong>Tier:</strong> {tier_level} ({BUS_PER_MW[tier_level]} buses/MW base)</p>
        <p><strong>Estimated Buses:</strong> {results['project_info']['estimated_buses']}</p>
    </div>
    """, unsafe_allow_html=True)

with cal_col2:
    st.markdown(f"""
    <div class="calibration-section">
        <h4>📊 Study Factors</h4>
        <p><strong>Load Flow:</strong> {load_flow_factor}x</p>
        <p><strong>Short Circuit:</strong> {short_circuit_factor}x</p>
        <p><strong>PDC:</strong> {pdc_factor}x</p>
        <p><strong>Arc Flash:</strong> {arc_flash_factor}x</p>
    </div>
    """, unsafe_allow_html=True)

with cal_col3:
    st.markdown(f"""
    <div class="calibration-section">
        <h4>👥 Resource Allocation</h4>
        <p><strong>Senior:</strong> {senior_allocation*100:.0f}% @ ₹{senior_rate}/hr</p>
        <p><strong>Mid:</strong> {mid_allocation*100:.0f}% @ ₹{mid_rate}/hr</p>
        <p><strong>Junior:</strong> {junior_allocation*100:.0f}% @ ₹{junior_rate}/hr</p>
        <p><strong>Meeting Cost:</strong> ₹{meeting_cost:,}/meeting</p>
    </div>
    """, unsafe_allow_html=True)

# Study breakdown with calibration info
if results['studies']:
    st.header("📋 Detailed Study Analysis")
    
    for study_key, study in results['studies'].items():
        calibration_factor = STUDIES_DATA[study_key]['calibration_factor']
        base_hours = STUDIES_DATA[study_key]['base_hours_per_bus']
        
        st.markdown(f"""
        <div class="study-item">
            <h4>{study['emoji']} {study['name']}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <p><strong>Complexity:</strong> {study['complexity']}</p>
                    <p><strong>Base Hours/Bus:</strong> {base_hours}</p>
                    <p><strong>Calibration Factor:</strong> {calibration_factor}x</p>
                    <p><strong>Tier Multiplier:</strong> {TIER_FACTORS[tier_level]}x</p>
                    <p><strong>Total Hours:</strong> {study['hours']:.1f}</p>
                </div>
                <div>
                    <p><strong>Senior:</strong> {study['senior_hours']:.1f}h × ₹{senior_rate} = ₹{study['senior_cost']:,.0f}</p>
                    <p><strong>Mid:</strong> {study['mid_hours']:.1f}h × ₹{mid_rate} = ₹{study['mid_cost']:,.0f}</p>
                    <p><strong>Junior:</strong> {study['junior_hours']:.1f}h × ₹{junior_rate} = ₹{study['junior_cost']:,.0f}</p>
                    <p style="border-top: 2px solid #2e8b57; padding-top: 10px;"><strong>Total Cost: ₹{study['total_cost']:,.0f}</strong></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Additional costs breakdown
st.subheader("💼 Additional Cost Components")

additional_col1, additional_col2, additional_col3 = st.columns(3)

with additional_col1:
    st.markdown(f"""
    <div class="study-item">
        <h4>🤝 Client Meetings</h4>
        <p><strong>{client_meetings} meetings × ₹{meeting_cost:,}</strong></p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['meeting_cost']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

with additional_col2:
    st.markdown(f"""
    <div class="study-item">
        <h4>📄 Report Preparation</h4>
        <p><strong>{report_format}</strong></p>
        <p>Base: ₹15,000 × {REPORT_MULTIPLIERS[report_format]}x</p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['report_cost']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

with additional_col3:
    st.markdown(f"""
    <div class="study-item">
        <h4>📈 Profit Margin</h4>
        <p><strong>{custom_margin}% on subtotal</strong></p>
        <p>₹{results['costs']['subtotal']:,.0f} × {custom_margin}%</p>
        <h3 style="color: #2e8b57; margin: 0;">₹{results['costs']['margin_amount']:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ No studies selected. Please select at least one study type from the sidebar.")

# Technical specifications
with st.expander("🔧 Technical Specifications & Methodology"):
    st.markdown("""
    ### 📊 Calculation Methodology (Perplexity AI Labs Logic)
    
    **Bus Count Estimation:**
    ```
    Estimated_Buses = ⌈Total_Load × Tier_Factor × Bus_Calibration_Factor⌉
    ```
    
    **Study Hours Calculation:**
    ```
    Study_Hours = Bus_Count × Base_Hours_per_Bus × Study_Calibration_Factor × Tier_Complexity_Factor
    ```
    
    **Cost Calculation:**
    ```
    Study_Cost = (Senior_Hours × Senior_Rate + Mid_Hours × Mid_Rate + Junior_Hours × Junior_Rate) × Urgency_Factor
    Total_Cost = (Study_Costs + Meeting_Costs + Report_Costs) × (1 + Margin%)
    ```
    
    **Current Calibration Values:**
    - Bus Calibration Factor: {bus_calibration}x
    - Study Factors: LF:{load_flow_factor}x, SC:{short_circuit_factor}x, PDC:{pdc_factor}x, AF:{arc_flash_factor}x
    - Resource Allocation: Sr:{senior_allocation*100:.0f}%, Mid:{mid_allocation*100:.0f}%, Jr:{junior_allocation*100:.0f}%
    - Hourly Rates: Sr:₹{senior_rate}, Mid:₹{mid_rate}, Jr:₹{junior_rate}
    - Urgency Multiplier: {urgency_multiplier}x
    """.format(
        bus_calibration=bus_calibration,
        load_flow_factor=load_flow_factor,
        short_circuit_factor=short_circuit_factor,
        pdc_factor=pdc_factor,
        arc_flash_factor=arc_flash_factor,
        senior_allocation=senior_allocation,
        mid_allocation=mid_allocation,
        junior_allocation=junior_allocation,
        senior_rate=senior_rate,
        mid_rate=mid_rate,
        junior_rate=junior_rate,
        urgency_multiplier=urgency_multiplier
    ))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>⚡ Data Center Power System Studies Cost Estimator</b></p>
    <p>🚀 Developed by <b>Abhishek Diwanji</b> | Power Systems Engineering Expert</p>
    <p>📧 For professional consulting, custom tools, and technical support</p>
    <p><i>Enhanced Version 2.0 | Full Calibration Controls</i></p>
</div>
""", unsafe_allow_html=True)
