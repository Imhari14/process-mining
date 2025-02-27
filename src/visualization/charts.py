import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
import pm4py

class ChartGenerator:
    def __init__(self):
        pass

    def create_cycle_time_chart(self, cycle_times):
        """
        Create a combined box plot and scatter plot of cycle times.
        """
        try:
            df = pd.DataFrame(cycle_times, columns=['Case ID', 'Duration (hours)'])
            
            # Create a figure with secondary y-axis
            fig = go.Figure()
            
            # Add box plot
            fig.add_trace(go.Box(
                y=df['Duration (hours)'],
                name='Distribution',
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ))
            
            # Add scatter plot for individual cases
            fig.add_trace(go.Scatter(
                x=df['Case ID'],
                y=df['Duration (hours)'],
                mode='markers',
                name='Individual Cases',
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Case Cycle Times',
                yaxis_title='Duration (hours)',
                showlegend=True,
                boxmode='group'
            )
            
            st.plotly_chart(fig)
            return fig
        except Exception as e:
            st.error(f"Error creating cycle time chart: {e}")
            return None

    def create_activity_frequency_chart(self, activity_stats):
        """
        Create a bar chart of activity frequencies with hover information.
        """
        try:
            df = pd.DataFrame(list(activity_stats.items()), 
                            columns=['Activity', 'Frequency'])
            df = df.sort_values('Frequency', ascending=True)
            
            fig = go.Figure(go.Bar(
                x=df['Frequency'],
                y=df['Activity'],
                orientation='h',
                text=df['Frequency'],
                textposition='auto',
            ))
            
            fig.update_layout(
                title='Activity Frequencies',
                xaxis_title='Frequency',
                yaxis_title='Activity',
                height=max(400, len(df) * 30)  # Adjust height based on number of activities
            )
            
            st.plotly_chart(fig)
            return fig
        except Exception as e:
            st.error(f"Error creating activity frequency chart: {e}")
            return None

    def create_performance_timeline(self, event_log):
        """
        Create an interactive timeline showing case durations and activities.
        """
        try:
            # Convert to dataframe if needed
            if not isinstance(event_log, pd.DataFrame):
                df = pm4py.convert_to_dataframe(event_log)
            else:
                df = event_log

            # Ensure timestamp is datetime
            if not pd.api.types.is_datetime64_any_dtype(df['time:timestamp']):
                df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
            
            # Calculate case durations
            durations = df.groupby('case:concept:name').agg({
                'time:timestamp': ['min', 'max']
            }).reset_index()
            
            # Rename columns
            durations.columns = ['case:concept:name', 'start_time', 'end_time']
            durations['duration'] = (durations['end_time'] - 
                                   durations['start_time']).dt.total_seconds() / 3600
            
            # Create timeline visualization
            fig = go.Figure()
            
            # Add cases as Gantt chart bars
            for idx, row in durations.iterrows():
                fig.add_trace(go.Bar(
                    name=f"Case {row['case:concept:name']}",
                    x=[row['duration']],
                    y=[row['case:concept:name']],
                    orientation='h',
                    marker=dict(
                        color='rgba(0,100,200,0.7)',
                        line=dict(color='rgba(0,100,200,1.0)', width=2)
                    ),
                    hovertext=[f"Duration: {row['duration']:.2f} hours<br>"
                              f"Start: {row['start_time']}<br>"
                              f"End: {row['end_time']}"],
                    hoverinfo='text'
                ))
            
            fig.update_layout(
                title='Case Duration Timeline',
                xaxis_title='Duration (hours)',
                yaxis_title='Case ID',
                showlegend=False,
                height=max(400, len(durations) * 30)
            )
            
            st.plotly_chart(fig)
            return fig
        except Exception as e:
            st.error(f"Error creating performance timeline: {e}")
            return None
