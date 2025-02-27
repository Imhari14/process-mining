import pm4py
import matplotlib.pyplot as plt
import streamlit as st

class ProcessMapVisualizer:
    def __init__(self):
        pass

    def visualize_process_map(self, net, initial_marking, final_marking):
        """
        Visualize a process map using PM4Py and matplotlib.
        """
        try:
            # Set visualization parameters
            parameters = {
                "format": "png",
                "bgcolor": "white",
                "rankdir": "LR",  # Left to right layout
                "ranksep": "0.5",  # Space between ranks
                "fontsize": "12",  # Font size
                "nodesep": "0.5"   # Space between nodes
            }
            
            # Create Petri net visualization
            gviz = pm4py.visualization.petri_net.visualizer.apply(
                net, initial_marking, final_marking,
                parameters=parameters,
                variant=pm4py.visualization.petri_net.visualizer.Variants.FREQUENCY
            )
            
            # Display the visualization
            st.graphviz_chart(gviz)
            
            # Show additional information
            st.subheader("Process Model Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Places:", len(net.places))
                st.write("Transitions:", len(net.transitions))
            with col2:
                st.write("Arcs:", len(net.arcs))
                st.write("Initial Places:", len(initial_marking))
            
            return gviz
        except Exception as e:
            st.error(f"Error visualizing process map: {e}")
            return None

    def visualize_dfg(self, dfg, start_activities, end_activities):
        """
        Visualize a Directly-Follows Graph (DFG) using PM4Py and matplotlib.
        """
        try:
            # Convert start/end activities to list if they're dictionaries
            start_acts = list(start_activities.keys()) if isinstance(start_activities, dict) else list(start_activities)
            end_acts = list(end_activities.keys()) if isinstance(end_activities, dict) else list(end_activities)
            
            # Create DFG visualization
            parameters = {
                "format": "png",
                "bgcolor": "white",
                "rankdir": "LR",
                "start_activities": start_acts,
                "end_activities": end_acts,
            }
            
            gviz = pm4py.visualization.dfg.visualizer.apply(
                dfg,
                log=None,
                parameters=parameters
            )
            
            # Display the visualization
            st.graphviz_chart(gviz)
            
            # Show additional information
            st.subheader("DFG Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Start Activities:", len(start_activities))
                st.write("End Activities:", len(end_activities))
            with col2:
                st.write("Total Activities:", len(set(act for (act, _) in dfg.keys()) | set(act for (_, act) in dfg.keys())))
                st.write("Total Connections:", len(dfg))
            
            return gviz
        except Exception as e:
            st.error(f"Error visualizing DFG: {e}")
            return None
