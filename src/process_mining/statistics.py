import pm4py
import pandas as pd
import numpy as np
from collections import defaultdict

class ProcessStatistics:
    def __init__(self):
        pass

    def get_case_statistics(self, event_log):
        """
        Get comprehensive statistics about cases in the event log.
        """
        df = pm4py.convert_to_dataframe(event_log)
        cases = {}
        
        # Group by case
        for case_id, case_data in df.groupby('case:concept:name'):
            # Temporal metrics
            temporal = {
                'start_time': case_data['time:timestamp'].min(),
                'end_time': case_data['time:timestamp'].max(),
                'duration_hours': (case_data['time:timestamp'].max() - 
                                 case_data['time:timestamp'].min()).total_seconds() / 3600
            }
            
            # Process metrics
            process = {
                'num_events': len(case_data),
                'unique_activities': len(case_data['concept:name'].unique()),
                'unique_resources': len(case_data['org:resource'].unique()),
                'activities': case_data['concept:name'].tolist()
            }
            
            # Performance metrics
            performance = {
                'avg_activity_duration': temporal['duration_hours'] / process['num_events'],
                'resource_handovers': len(case_data['org:resource'].unique()) - 1
            }
            
            # Business metrics
            business = {}
            if 'request_type' in case_data.columns:
                business['request_type'] = case_data['request_type'].iloc[0]
            if 'claim_category' in case_data.columns:
                business['claim_category'] = case_data['claim_category'].iloc[0]
            if 'customer_segment' in case_data.columns:
                business['customer_segment'] = case_data['customer_segment'].iloc[0]
            if 'claim_value' in case_data.columns:
                business['claim_value'] = case_data['claim_value'].iloc[0]
            if 'risk_level' in case_data.columns:
                business['risk_level'] = case_data['risk_level'].iloc[0]
            
            # Combine all metrics
            cases[case_id] = {
                'temporal': temporal,
                'process': process,
                'performance': performance,
                'business': business
            }
        
        return cases

    def get_activity_statistics(self, event_log):
        """
        Get detailed statistics about activities in the event log.
        """
        df = pm4py.convert_to_dataframe(event_log)
        activities = {}
        
        # Group by activity
        for activity, activity_data in df.groupby('concept:name'):
            # Frequency metrics
            frequency = {
                'total_occurrences': len(activity_data),
                'unique_cases': len(activity_data['case:concept:name'].unique()),
                'unique_resources': len(activity_data['org:resource'].unique())
            }
            
            # Time metrics
            time_metrics = {
                'min_timestamp': activity_data['time:timestamp'].min(),
                'max_timestamp': activity_data['time:timestamp'].max(),
                'avg_duration': activity_data.groupby('case:concept:name')['time:timestamp'].agg(lambda x: (x.max() - x.min()).total_seconds() / 3600).mean()
            }
            
            # Resource distribution
            resource_dist = activity_data['org:resource'].value_counts().to_dict()
            
            # Performance metrics
            if 'costs' in activity_data.columns:
                performance = {
                    'total_cost': activity_data['costs'].sum(),
                    'avg_cost': activity_data['costs'].mean(),
                    'min_cost': activity_data['costs'].min(),
                    'max_cost': activity_data['costs'].max()
                }
            else:
                performance = {}
            
            activities[activity] = {
                'frequency': frequency,
                'time': time_metrics,
                'resources': resource_dist,
                'performance': performance
            }
        
        return activities

    def get_resource_statistics(self, event_log):
        """
        Get detailed statistics about resources in the event log.
        """
        df = pm4py.convert_to_dataframe(event_log)
        resources = {}
        
        # Group by resource
        for resource, resource_data in df.groupby('org:resource'):
            # Workload metrics
            workload = {
                'total_activities': len(resource_data),
                'unique_cases': len(resource_data['case:concept:name'].unique()),
                'unique_activities': len(resource_data['concept:name'].unique())
            }
            
            # Time metrics
            time_metrics = {
                'first_activity': resource_data['time:timestamp'].min(),
                'last_activity': resource_data['time:timestamp'].max(),
                'active_hours': (resource_data['time:timestamp'].max() - 
                               resource_data['time:timestamp'].min()).total_seconds() / 3600
            }
            
            # Activity distribution
            activity_dist = resource_data['concept:name'].value_counts().to_dict()
            
            # Performance metrics
            performance = {}
            if 'costs' in resource_data.columns:
                performance.update({
                    'total_cost': resource_data['costs'].sum(),
                    'avg_cost_per_activity': resource_data['costs'].mean()
                })
            
            resources[resource] = {
                'workload': workload,
                'time': time_metrics,
                'activities': activity_dist,
                'performance': performance
            }
        
        return resources

    def get_process_kpis(self, event_log):
        """
        Calculate key performance indicators (KPIs) for the process.
        """
        df = pm4py.convert_to_dataframe(event_log)
        kpis = {}
        
        # Time-based KPIs
        case_durations = df.groupby('case:concept:name')['time:timestamp'].agg(['min', 'max'])
        case_durations['duration'] = (case_durations['max'] - case_durations['min']).dt.total_seconds() / 3600
        
        kpis['time'] = {
            'avg_case_duration': case_durations['duration'].mean(),
            'median_case_duration': case_durations['duration'].median(),
            'min_case_duration': case_durations['duration'].min(),
            'max_case_duration': case_durations['duration'].max()
        }
        
        # Process KPIs
        kpis['process'] = {
            'total_cases': len(df['case:concept:name'].unique()),
            'total_events': len(df),
            'unique_activities': len(df['concept:name'].unique()),
            'unique_resources': len(df['org:resource'].unique()),
            'events_per_case': len(df) / len(df['case:concept:name'].unique())
        }
        
        # Business KPIs
        if 'claim_value' in df.columns and 'costs' in df.columns:
            kpis['business'] = {
                'total_claim_value': df.groupby('case:concept:name')['claim_value'].first().sum(),
                'total_process_cost': df['costs'].sum(),
                'avg_claim_value': df.groupby('case:concept:name')['claim_value'].first().mean(),
                'avg_process_cost': df['costs'].mean()
            }
        
        return kpis
