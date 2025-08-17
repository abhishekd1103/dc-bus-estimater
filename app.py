import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Data Center Bus Estimator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("⚡ Data Center Electrical Bus Count Estimator")
st.markdown("**Professional tool for estimating electrical bus requirements in data center power distribution systems**")

# Sidebar for inputs
st.sidebar.header("📊 Configuration Parameters")

# Toggle for input type
input_type = st.sidebar.radio(
    "Starting Point:",
    ["IT Load (MW)", "Total Facility Load (MW)"],
    help="Choose whether to start from critical IT load or total facility load"
)

# Main load input
if input_type == "IT Load (MW)":
    it_mw = st.sidebar.number_input(
        "IT Load (MW)", 
        min_value=0.1, 
        max_value=100.0, 
        value=5.0, 
        step=0.1,
        help="Critical IT load capacity (servers, storage, networking)"
    )
    total_mw = None
else:
    total_mw = st.sidebar.number_input(
        "Total Facility Load (MW)", 
        min_value=0.2, 
        max_value=200.0, 
        value=7.8, 
        step=0.1,
        help="Total facility electrical load including IT and infrastructure"
    )
    it_mw = None

# PUE input
pue = st.sidebar.slider(
    "PUE (Power Usage Effectiveness)", 
    min_value=1.1, 
    max_value=2.0, 
    value=1.56, 
    step=0.01,
    help="Industry average: 1.56 (Uptime Institute 2024)"
)

# Data center type
dc_type = st.sidebar.selectbox(
    "Data Center Type",
    ["Enterprise/Colo", "Hyperscale", "AI/HPC"],
    help="Different types have varying infrastructure requirements"
)

# Auto-adjust defaults based on DC type
if dc_type == "AI/HPC":
    default_mech_frac = 0.8
    pue_adjustment = -0.2  # AI/HPC often has better cooling efficiency
elif dc_type == "Hyperscale":
    default_mech_frac = 0.75
    pue_adjustment = -0.1
else:  # Enterprise/Colo
    default_mech_frac = 0.7
    pue_adjustment = 0.0

# Apply PUE adjustment
adjusted_pue = max(1.1, pue + pue_adjustment)

# Non-IT load split
mech_fraction = st.sidebar.slider(
    "Mechanical (Cooling) Fraction of Non-IT Load", 
    min_value=0.5, 
    max_value=0.9, 
    value=default_mech_frac, 
    step=0.01,
    help="Percentage of non-IT load dedicated to cooling systems"
)

# Redundancy tier
redundancy = st.sidebar.selectbox(
    "Redundancy Tier",
    ["N (Base)", "Tier III (N+1)", "Tier IV (2N)"],
    index=1,
    help="Higher tiers require more redundant equipment and buses"
)

# Equipment capacities section
st.sidebar.subheader("🔧 Equipment Block Capacities")

ups_lineup = st.sidebar.slider("UPS Lineup (MW)", 0.5, 2.0, 1.5, 0.1)
transformer_mva = st.sidebar.slider("Transformer MV→LV (MVA)", 1.0, 5.0, 3.0, 0.1)
lv_bus_mw = st.sidebar.slider("LV Switchboard Bus Section (MW)", 2.0, 4.5, 3.0, 0.1)
pdu_mva = st.sidebar.slider("PDU Capacity (MVA)", 0.2, 0.6, 0.3, 0.05)
mv_base = st.sidebar.slider("MV Buses Base (per system)", 1, 4, 2, 1)

# Additional factors
st.sidebar.subheader("⚙️ Additional Factors")

voltage_levels = st.sidebar.selectbox("Voltage Levels", [2, 3], index=0, help="2=MV+LV, 3=HV+MV+LV")
backup_gens = st.sidebar.slider("Backup Generators", 0, 10, 0, 1)
cooling_type = st.sidebar.selectbox("Cooling Type", ["Air-cooled", "Liquid-cooled"])
geo_factor = st.sidebar.selectbox(
    "Geographic Climate", 
    ["Temperate", "Cold", "Hot/Humid"],
    help="Affects cooling load and PUE"
)
expansion_factor = st.sidebar.slider("Future Expansion Factor", 1.0, 1.5, 1.0, 0.05)
power_factor = st.sidebar.slider("Power Factor", 0.9, 1.0, 0.95, 0.01)
utility_incomers = st.sidebar.slider("Utility Incomers", 1, 3, 1, 1)

# Reset button
if st.sidebar.button("🔄 Reset to Defaults"):
    st.experimental_rerun()

# Main calculation function
def calculate_bus_counts():
    results = {}
    warnings = []
    
    # Step 1: Load derivation
    if it_mw is not None:
        calc_total_mw = adjusted_pue * it_mw
        calc_it_mw = it_mw
    else:
        calc_total_mw = total_mw
        calc_it_mw = total_mw / adjusted_pue
    
    non_it_mw = calc_total_mw - calc_it_mw
    
    # Apply cooling type adjustment
    cooling_multiplier = 1.0
    if cooling_type == "Liquid-cooled":
        cooling_multiplier = 1.2
        
    # Apply geographic factor
    geo_multiplier = 1.0
    if geo_factor == "Cold":
        geo_multiplier = 0.9
    elif geo_factor == "Hot/Humid":
        geo_multiplier = 1.1
    
    mech_mw = mech_fraction * non_it_mw * cooling_multiplier * geo_multiplier
    house_mw = non_it_mw - (mech_mw / (cooling_multiplier * geo_multiplier))
    
    # Step 2: Base counts (N configuration)
    lv_it_pcc = math.ceil(calc_it_mw / lv_bus_mw)
    lv_mech_mcc = math.ceil(mech_mw / lv_bus_mw)
    lv_house_pcc = math.ceil(house_mw / lv_bus_mw)
    lv_total = lv_it_pcc + lv_mech_mcc + lv_house_pcc
    
    ups_lineups = math.ceil(calc_it_mw / ups_lineup)
    ups_output_buses = ups_lineups
    
    pdus_total = math.ceil(calc_it_mw / pdu_mva)
    
    tx_count_n = math.ceil(calc_total_mw / (transformer_mva * power_factor))
    
    mv_buses = mv_base + (utility_incomers - 1)
    
    # Voltage level adjustments
    voltage_additions = 0
    if voltage_levels > 2:
        voltage_additions = (voltage_levels - 2) * (tx_count_n + 1)
    
    # Generator additions
    generator_additions = backup_gens * 2  # ATS buses
    
    # Core bus count (N configuration)
    buses_core_n = (mv_buses + tx_count_n + lv_total + 
                   ups_output_buses + pdus_total + 
                   voltage_additions + generator_additions)
    
    # Step 3: Redundancy adjustments
    if redundancy == "N (Base)":
        total_buses = buses_core_n * expansion_factor
        redundancy_factor = 1.0
    elif redundancy == "Tier III (N+1)":
        tx_count_adj = tx_count_n + 1
        buses_adj = (mv_buses + tx_count_adj + lv_total + 
                    ups_output_buses + pdus_total + 
                    voltage_additions + generator_additions)
        total_buses = buses_adj * expansion_factor * 1.15
        redundancy_factor = 1.15
    else:  # Tier IV (2N)
        mv_2n = mv_buses * 2
        tx_2n = tx_count_n * 2
        lv_2n = lv_total * 2
        ups_2n = ups_output_buses * 2
        pdus_2n = pdus_total * 1.5  # Not fully duplicated
        extras_2n = (voltage_additions + generator_additions) * 2
        
        buses_2n = mv_2n + tx_2n + lv_2n + ups_2n + pdus_2n + extras_2n
        total_buses = buses_2n * expansion_factor
        redundancy_factor = 2.0
    
    # Round final result
    total_buses = math.ceil(total_buses)
    
    # Warnings
    if total_buses > 500 and calc_total_mw < 20:
        warnings.append("⚠️ Bus count seems high for facility size. Review parameters.")
    if pdus_total > 500:
        warnings.append("⚠️ PDU count exceeds 500. Consider larger PDU blocks.")
    if calc_it_mw / calc_total_mw < 0.3:
        warnings.append("⚠️ IT load fraction is low. Check PUE value.")
    
    # Store results
    results = {
        'calc_total_mw': calc_total_mw,
        'calc_it_mw': calc_it_mw,
        'non_it_mw': non_it_mw,
        'mech_mw': mech_mw,
        'house_mw': house_mw,
        'lv_it_pcc': lv_it_pcc,
        'lv_mech_mcc': lv_mech_mcc,
        'lv_house_pcc': lv_house_pcc,
        'lv_total': lv_total,
        'ups_lineups': ups_lineups,
        'ups_output_buses': ups_output_buses,
        'pdus_total': pdus_total,
        'tx_count_n': tx_count_n,
        'mv_buses': mv_buses,
        'voltage_additions': voltage_additions,
        'generator_additions': generator_additions,
        'total_buses': total_buses,
        'warnings': warnings,
        'redundancy_factor': redundancy_factor
    }
    
    return results

# Calculate results
results = calculate_bus_counts()

# Display results
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Results Summary")
    
    # Key metrics
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Total Buses", f"{results['total_buses']:,}")
    with metric_cols[1]:
        st.metric("IT Load", f"{results['calc_it_mw']:.1f} MW")
    with metric_cols[2]:
        st.metric("Total Load", f"{results['calc_total_mw']:.1f} MW")
    with metric_cols[3]:
        st.metric("Effective PUE", f"{adjusted_pue:.2f}")
    
    # Detailed breakdown table
    st.subheader("🔧 Component Breakdown")
    
    breakdown_data = {
        'Component': [
            'MV Buses',
            'Transformers (MV→LV)',
            'LV IT Buses (PCC)',
            'LV Mechanical Buses (MCC)',
            'LV House/Aux Buses',
            'UPS Output Buses',
            'PDUs',
            'Voltage Level Additions',
            'Generator Transfer Switches',
            'Redundancy Adjustment',
            'Expansion Factor'
        ],
        'Count': [
            results['mv_buses'],
            results['tx_count_n'],
            results['lv_it_pcc'],
            results['lv_mech_mcc'],
            math.ceil(results['house_mw'] / lv_bus_mw),
            results['ups_output_buses'],
            results['pdus_total'],
            results['voltage_additions'],
            results['generator_additions'],
            f"×{results['redundancy_factor']:.2f}",
            f"×{expansion_factor:.2f}"
        ],
        'Explanation': [
            f"Base {mv_base} + {utility_incomers-1} utility incomers",
            f"{results['calc_total_mw']:.1f} MW ÷ {transformer_mva} MVA",
            f"{results['calc_it_mw']:.1f} MW ÷ {lv_bus_mw} MW",
            f"{results['mech_mw']:.1f} MW ÷ {lv_bus_mw} MW",
            f"{results['house_mw']:.1f} MW ÷ {lv_bus_mw} MW",
            f"{results['ups_lineups']} UPS lineups",
            f"{results['calc_it_mw']:.1f} MW ÷ {pdu_mva} MVA",
            f"{voltage_levels-2} extra voltage levels" if voltage_levels > 2 else "None",
            f"{backup_gens} generators × 2 ATS buses" if backup_gens > 0 else "None",
            redundancy,
            "Future growth allowance"
        ]
    }
    
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.header("📈 Visualization")
    
    # Pie chart of bus distribution
    bus_categories = {
        'MV System': results['mv_buses'] + results['voltage_additions'],
        'Transformers': results['tx_count_n'],
        'LV Distribution': results['lv_total'],
        'UPS Systems': results['ups_output_buses'],
        'PDUs': results['pdus_total'],
        'Generators': results['generator_additions']
    }
    
    # Filter out zero values
    bus_categories = {k: v for k, v in bus_categories.items() if v > 0}
    
    if bus_categories:
        fig_pie = px.pie(
            values=list(bus_categories.values()),
            names=list(bus_categories.keys()),
            title="Bus Distribution by Category"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Load breakdown
    st.subheader("⚡ Load Breakdown")
    load_data = {
        'Load Type': ['IT Load', 'Mechanical', 'House/Aux'],
        'MW': [results['calc_it_mw'], results['mech_mw'], results['house_mw']],
        'Percentage': [
            results['calc_it_mw']/results['calc_total_mw']*100,
            results['mech_mw']/results['calc_total_mw']*100,
            results['house_mw']/results['calc_total_mw']*100
        ]
    }
    
    fig_bar = px.bar(
        load_data, 
        x='Load Type', 
        y='MW',
        title="Load Distribution",
        text='MW',
        color='Load Type'
    )
    fig_bar.update_traces(texttemplate='%{text:.1f} MW', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# Warnings
if results['warnings']:
    st.header("⚠️ Validation Warnings")
    for warning in results['warnings']:
        st.warning(warning)

# Sensitivity analysis
st.header("🎯 Sensitivity Analysis")

sens_col1, sens_col2 = st.columns(2)

with sens_col1:
    st.subheader("PUE Impact")
    pue_range = [pue - 0.2, pue - 0.1, pue, pue + 0.1, pue + 0.2]
    bus_counts_pue = []
    
    for test_pue in pue_range:
        if it_mw is not None:
            test_total = max(test_pue, 1.1) * it_mw
        else:
            test_total = total_mw
        
        # Simplified calculation for sensitivity
        test_buses = math.ceil((test_total / transformer_mva * power_factor + 
                              results['lv_total'] + results['ups_output_buses'] + 
                              results['pdus_total']) * results['redundancy_factor'] * expansion_factor)
        bus_counts_pue.append(test_buses)
    
    sens_df_pue = pd.DataFrame({
        'PUE': pue_range,
        'Estimated Buses': bus_counts_pue
    })
    
    fig_sens_pue = px.line(sens_df_pue, x='PUE', y='Estimated Buses', 
                          title='Bus Count vs PUE Sensitivity',
                          markers=True)
    fig_sens_pue.add_vline(x=pue, line_dash="dash", line_color="red", 
                          annotation_text="Current PUE")
    st.plotly_chart(fig_sens_pue, use_container_width=True)

with sens_col2:
    st.subheader("Load Impact")
    if it_mw is not None:
        base_load = it_mw
        load_label = "IT Load (MW)"
    else:
        base_load = total_mw
        load_label = "Total Load (MW)"
    
    load_range = [base_load * 0.5, base_load * 0.75, base_load, 
                  base_load * 1.25, base_load * 1.5]
    bus_counts_load = []
    
    for test_load in load_range:
        if it_mw is not None:
            test_total = adjusted_pue * test_load
        else:
            test_total = test_load
        
        test_buses = math.ceil((test_total / transformer_mva * power_factor + 
                              math.ceil(test_load / lv_bus_mw) * 3 + 
                              math.ceil(test_load / ups_lineup) + 
                              math.ceil(test_load / pdu_mva)) * 
                              results['redundancy_factor'] * expansion_factor)
        bus_counts_load.append(test_buses)
    
    sens_df_load = pd.DataFrame({
        load_label: load_range,
        'Estimated Buses': bus_counts_load
    })
    
    fig_sens_load = px.line(sens_df_load, x=load_label, y='Estimated Buses',
                           title=f'Bus Count vs {load_label} Sensitivity',
                           markers=True)
    fig_sens_load.add_vline(x=base_load, line_dash="dash", line_color="red",
                           annotation_text="Current Load")
    st.plotly_chart(fig_sens_load, use_container_width=True)

# Export functionality
st.header("💾 Export Results")

export_col1, export_col2 = st.columns(2)

with export_col1:
    # CSV export
    export_df = pd.DataFrame([{
        'Parameter': 'Total Estimated Buses',
        'Value': results['total_buses'],
        'Unit': 'count'
    }, {
        'Parameter': 'IT Load',
        'Value': round(results['calc_it_mw'], 2),
        'Unit': 'MW'
    }, {
        'Parameter': 'Total Facility Load',
        'Value': round(results['calc_total_mw'], 2),
        'Unit': 'MW'
    }, {
        'Parameter': 'Effective PUE',
        'Value': round(adjusted_pue, 2),
        'Unit': 'ratio'
    }, {
        'Parameter': 'Redundancy Level',
        'Value': redundancy,
        'Unit': 'tier'
    }, {
        'Parameter': 'Data Center Type',
        'Value': dc_type,
        'Unit': 'category'
    }])
    
    csv = export_df.to_csv(index=False)
    st.download_button(
        label="📄 Download CSV Report",
        data=csv,
        file_name=f"dc_bus_estimate_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

with export_col2:
    # Summary text export
    summary_text = f"""
DATA CENTER BUS COUNT ESTIMATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

INPUTS:
- Starting Point: {input_type}
- Load: {it_mw if it_mw else total_mw} MW
- PUE: {pue} (Adjusted: {adjusted_pue:.2f})
- Data Center Type: {dc_type}
- Redundancy: {redundancy}
- Cooling: {cooling_type}
- Climate: {geo_factor}

RESULTS:
- Total Estimated Buses: {results['total_buses']:,}
- IT Load: {results['calc_it_mw']:.1f} MW
- Total Load: {results['calc_total_mw']:.1f} MW
- Mechanical Load: {results['mech_mw']:.1f} MW

BREAKDOWN:
- MV Buses: {results['mv_buses']}
- Transformers: {results['tx_count_n']}
- LV Buses: {results['lv_total']}
- UPS Buses: {results['ups_output_buses']}
- PDUs: {results['pdus_total']}

VALIDATION:
{chr(10).join(results['warnings']) if results['warnings'] else 'No warnings detected.'}
"""
    
    st.download_button(
        label="📋 Download Text Summary",
        data=summary_text,
        file_name=f"dc_bus_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown("**References:** Uptime Institute Data Center Standards,Reliability Standards, Industry General Practices")
st.markdown("*Developed for professional electrical engineering applications. Validate results against specific project requirements.*")
st.markdown("*Developed By: Abhishek D*")
