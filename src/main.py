import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import pm4py

# Import our custom modules
from process_mining.discovery import ProcessDiscovery
from process_mining.performance import PerformanceAnalyzer
from process_mining.statistics import ProcessStatistics
from ai.gemini import GeminiInterface
from ai.insights import InsightGenerator
from visualization.process_maps import ProcessMapVisualizer
from visualization.charts import ChartGenerator
from utils.data_processing import EventLogProcessor
from utils.config import load_config

def initialize_session_state():
    """Initialize session state variables"""
    if 'event_log' not in st.session_state:
        st.session_state.event_log = None
    if 'process_model' not in st.session_state:
        st.session_state.process_model = None
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

def render_upload_page():
    """Render the file upload page"""
    st.header("Upload Event Log")
    
    # Initialize EventLogProcessor
    processor = EventLogProcessor()
    
    uploaded_file = st.file_uploader("Choose a CSV or XES file", type=["csv", "xes"])
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "csv":
            try:
                # Read CSV and show column mapping
                df = pd.read_csv(uploaded_file)
                st.subheader("CSV Column Mapping")
                
                # Display raw data sample
                st.write("Raw Data Sample:")
                st.write(df.head())
                
                # Get column mappings from user
                col1, col2 = st.columns(2)
                with col1:
                    case_id_col = st.selectbox("Select Case ID column", df.columns)
                    activity_col = st.selectbox("Select Activity column", df.columns)
                    timestamp_col = st.selectbox("Select Timestamp column", df.columns)
                
                with col2:
                    st.write("Optional Columns:")
                    resource_col = st.selectbox("Select Resource column (optional)", ["None"] + list(df.columns))
                    cost_col = st.selectbox("Select Cost column (optional)", ["None"] + list(df.columns))
                
                if st.button("Process CSV"):
                    # Create column mapping
                    column_mapping = {
                        case_id_col: 'case:concept:name',
                        activity_col: 'concept:name',
                        timestamp_col: 'time:timestamp'
                    }
                    
                    # Add optional columns if selected
                    if resource_col != "None":
                        column_mapping[resource_col] = 'org:resource'
                    if cost_col != "None":
                        column_mapping[cost_col] = 'cost'
                    
                    # Rename columns to PM4Py format
                    df = df.rename(columns=column_mapping)
                    
                    try:
                        # Process the event log
                        event_log = processor.convert_csv_to_event_log(df)
                        st.session_state.event_log = event_log
                        
                        # Show success message and processed data
                        st.success("CSV file successfully processed!")
                        st.subheader("Processed Event Log Sample")
                        
                        # Convert event log back to DataFrame for display
                        processed_df = pm4py.convert_to_dataframe(event_log)
                        st.write(processed_df.head())
                        
                        # Show event log statistics
                        st.subheader("Event Log Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Cases", len(set(processed_df['case:concept:name'])))
                        with col2:
                            st.metric("Total Events", len(processed_df))
                        with col3:
                            st.metric("Unique Activities", len(set(processed_df['concept:name'])))
                            
                    except Exception as e:
                        st.error(f"Error converting to event log: {str(e)}")
                        st.error("Please ensure your data is in the correct format and try again.")
            except Exception as e:
                st.error(f"Error loading CSV file: {e}")
        
        elif file_extension == "xes":
            try:
                log = pm4py.read_xes(uploaded_file)
                st.session_state.event_log = log
                st.success("XES file successfully loaded!")
                
                # Show sample of loaded data
                st.subheader("Sample of Loaded Data")
                st.write(pd.DataFrame(pm4py.convert_to_dataframe(log)[0:5]))
            except Exception as e:
                st.error(f"Error loading XES file: {e}")
        else:
            st.error("Unsupported file format. Please upload a CSV or XES file.")

def main():
    # Load environment variables
    load_dotenv()
    
    # Set page config
    st.set_page_config(
        page_title="Process Mining + AI Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("Process Mining + AI Analytics Platform")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choose a page",
            ["Upload & Process", "Process Discovery", "Performance Analysis", 
             "Statistical Analysis", "AI Insights"]
        )
    
    # Main content based on selected page
    if page == "Upload & Process":
        render_upload_page()
    elif page == "Process Discovery":
        if st.session_state.event_log is not None:
            st.header("Process Discovery")
            
            # Initialize components
            discovery = ProcessDiscovery()
            visualizer = ProcessMapVisualizer()
            
            # Discovery options
            discovery_type = st.selectbox(
                "Select Discovery Type",
                ["Petri Net", "BPMN", "DFG"]
            )
            
            if discovery_type == "Petri Net":
                try:
                    net, initial_marking, final_marking = discovery.discover_process_map(st.session_state.event_log)
                    visualizer.visualize_process_map(net, initial_marking, final_marking)
                except Exception as e:
                    st.error(f"Error in process discovery: {e}")
            
            elif discovery_type == "BPMN":
                try:
                    bpmn_model = discovery.discover_bpmn_model(st.session_state.event_log)
                    st.write("BPMN model generated successfully")
                except Exception as e:
                    st.error(f"Error in BPMN discovery: {e}")
            
            elif discovery_type == "DFG":
                try:
                    dfg, start_activities, end_activities = discovery.discover_dfg(st.session_state.event_log)
                    visualizer.visualize_dfg(dfg, start_activities, end_activities)
                except Exception as e:
                    st.error(f"Error in DFG discovery: {e}")
        else:
            st.warning("Please upload an event log first")

    elif page == "Performance Analysis":
        if st.session_state.event_log is not None:
            st.header("Performance Analysis")
            
            # Initialize components
            performance = PerformanceAnalyzer()
            charts = ChartGenerator()
            
            try:
                # Calculate performance metrics
                cycle_time = performance.calculate_cycle_time(st.session_state.event_log)
                waiting_time = performance.calculate_waiting_time(st.session_state.event_log)
                sojourn_time = performance.calculate_sojourn_time(st.session_state.event_log)
                
                # Display metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Cycle Time Analysis")
                    charts.create_cycle_time_chart(cycle_time)
                
                with col2:
                    st.subheader("Activity Waiting Times")
                    st.write(waiting_time)
                
                st.subheader("Process Timeline")
                charts.create_performance_timeline(st.session_state.event_log)
            
            except Exception as e:
                st.error(f"Error in performance analysis: {e}")
        else:
            st.warning("Please upload an event log first")

    elif page == "Statistical Analysis":
        if st.session_state.event_log is not None:
            st.header("Statistical Analysis")
            
            # Initialize components
            stats = ProcessStatistics()
            charts = ChartGenerator()
            
            try:
                # Get all statistics
                case_stats = stats.get_case_statistics(st.session_state.event_log)
                activity_stats = stats.get_activity_statistics(st.session_state.event_log)
                resource_stats = stats.get_resource_statistics(st.session_state.event_log)
                process_kpis = stats.get_process_kpis(st.session_state.event_log)
                
                # Display Process Overview
                st.subheader("Process Overview")
                kpi_cols = st.columns(4)
                with kpi_cols[0]:
                    st.metric("Total Cases", process_kpis['process']['total_cases'])
                with kpi_cols[1]:
                    st.metric("Total Events", process_kpis['process']['total_events'])
                with kpi_cols[2]:
                    st.metric("Avg Duration (hrs)", f"{process_kpis['time']['avg_case_duration']:.1f}")
                with kpi_cols[3]:
                    st.metric("Events per Case", f"{process_kpis['process']['events_per_case']:.1f}")
                
                # Case Analysis
                st.subheader("Case Analysis")
                case_tabs = st.tabs(["Overview", "Performance", "Business Metrics"])
                
                with case_tabs[0]:
                    st.write("Case Duration Distribution")
                    case_durations = [(case, stats['temporal']['duration_hours']) 
                                    for case, stats in case_stats.items()]
                    charts.create_cycle_time_chart(case_durations)
                
                with case_tabs[1]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Resource Utilization")
                        resource_data = pd.DataFrame(
                            [(r, stats['workload']['total_activities']) 
                             for r, stats in resource_stats.items()],
                            columns=['Resource', 'Activities']
                        )
                        st.bar_chart(resource_data.set_index('Resource'))
                    
                    with col2:
                        st.write("Activity Distribution")
                        charts.create_activity_frequency_chart(
                            {act: stats['frequency']['total_occurrences'] 
                             for act, stats in activity_stats.items()}
                        )
                
                with case_tabs[2]:
                    if 'business' in process_kpis:
                        business_cols = st.columns(2)
                        with business_cols[0]:
                            st.metric("Total Claim Value", 
                                    f"${process_kpis['business']['total_claim_value']:,.2f}")
                            st.metric("Avg Claim Value",
                                    f"${process_kpis['business']['avg_claim_value']:,.2f}")
                        with business_cols[1]:
                            st.metric("Total Process Cost",
                                    f"${process_kpis['business']['total_process_cost']:,.2f}")
                            st.metric("Avg Process Cost",
                                    f"${process_kpis['business']['avg_process_cost']:,.2f}")
                    else:
                        st.info("No business metrics available in the event log")
                
                # Resource Analysis
                st.subheader("Resource Analysis")
                resource_tabs = st.tabs(["Workload", "Performance"])
                
                with resource_tabs[0]:
                    for resource, stats in resource_stats.items():
                        with st.expander(f"Resource: {resource}"):
                            rcol1, rcol2 = st.columns(2)
                            with rcol1:
                                st.metric("Total Activities", stats['workload']['total_activities'])
                                st.metric("Unique Cases", stats['workload']['unique_cases'])
                            with rcol2:
                                st.metric("Active Hours", f"{stats['time']['active_hours']:.1f}")
                                if 'performance' in stats and 'total_cost' in stats['performance']:
                                    st.metric("Total Cost", f"${stats['performance']['total_cost']:,.2f}")
                
                with resource_tabs[1]:
                    if any('costs' in stats['performance'] for stats in resource_stats.values()):
                        performance_data = pd.DataFrame([
                            {
                                'Resource': r,
                                'Total Cost': stats['performance'].get('total_cost', 0),
                                'Avg Cost': stats['performance'].get('avg_cost_per_activity', 0)
                            }
                            for r, stats in resource_stats.items()
                        ])
                        st.write("Resource Cost Analysis")
                        st.dataframe(performance_data)
                    else:
                        st.info("No cost information available for resources")
                
            except Exception as e:
                st.error(f"Error in statistical analysis: {e}")
                st.error("Details:", str(e))
        else:
            st.warning("Please upload an event log first")

    elif page == "AI Insights":
        if st.session_state.event_log is not None:
            st.header("AI Insights")
            
            try:
                # Initialize AI components
                gemini = GeminiInterface()
                insights = InsightGenerator(gemini)
                
                # Generate insights
                process_insights = insights.generate_process_insights(
                    str(st.session_state.event_log),
                    "Process model analysis"  # Placeholder for process model
                )
                
                # Display insights
                st.subheader("Process Insights")
                st.write(process_insights)
                
                # Interactive query section
                st.subheader("Ask Questions")
                user_query = st.text_input("Ask a question about the process:")
                if user_query:
                    answer = insights.generate_conversational_analysis(
                        user_query,
                        str(st.session_state.event_log)
                    )
                    st.write("Answer:", answer)
                
            except Exception as e:
                st.error(f"Error generating insights: {e}")
        else:
            st.warning("Please upload an event log first")

if __name__ == "__main__":
    main()
