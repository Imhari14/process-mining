import pandas as pd
import pm4py
import numpy as np

class EventLogProcessor:
    def __init__(self):
        pass

    def convert_csv_to_event_log(self, df):
        """
        Convert a pandas DataFrame to PM4Py event log format with enhanced attributes.
        """
        try:
            # Check and process required columns
            required_columns = {
                'case:concept:name': str,
                'concept:name': str,
                'time:timestamp': 'datetime64[ns]',
                'org:resource': str
            }
            
            # Validate required columns
            for col, dtype in required_columns.items():
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
                if dtype == 'datetime64[ns]':
                    if not pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S')
                else:
                    df[col] = df[col].astype(dtype)

            # Sort by case ID and timestamp
            df = df.sort_values(['case:concept:name', 'time:timestamp'])
            
            # Calculate additional metrics
            case_groups = df.groupby('case:concept:name')
            
            # Add case duration
            df['case_duration'] = case_groups['time:timestamp'].transform(
                lambda x: (x.max() - x.min()).total_seconds() / 3600
            )
            
            # Add activity wait time
            df['wait_time'] = case_groups['time:timestamp'].transform(
                lambda x: x.diff().dt.total_seconds() / 3600
            )
            
            # Add case complexity score (based on number of events and duration)
            complexity_scores = case_groups.agg({
                'time:timestamp': 'count',
                'case_duration': 'first'
            })
            complexity_scores['complexity_score'] = (
                (complexity_scores['time:timestamp'] / complexity_scores['time:timestamp'].max()) * 0.5 +
                (complexity_scores['case_duration'] / complexity_scores['case_duration'].max()) * 0.5
            )
            df = df.merge(
                complexity_scores['complexity_score'],
                left_on='case:concept:name',
                right_index=True
            )
            
            # Convert to event log format
            try:
                parameters = {
                    pm4py.utils.constants.PARAMETER_CONSTANT_CASEID_KEY: 'case:concept:name',
                    pm4py.utils.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: 'concept:name',
                    pm4py.utils.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: 'time:timestamp'
                }
                
                event_log = pm4py.convert_to_event_log(df, parameters=parameters)
                
                if len(event_log) == 0:
                    raise ValueError("Converted event log is empty")
                    
            except Exception as e:
                raise ValueError(f"Failed to convert DataFrame to event log: {str(e)}")
            
            return event_log
            
        except Exception as e:
            raise ValueError(f"Error converting CSV to event log: {e}")

    def clean_event_log(self, event_log):
        """
        Clean and preprocess the event log with enhanced filtering.
        """
        try:
            # Convert to DataFrame for advanced cleaning
            df = pm4py.convert_to_dataframe(event_log)
            
            # Remove cases with missing critical attributes
            critical_cols = ['case:concept:name', 'concept:name', 'time:timestamp', 'org:resource']
            df = df.dropna(subset=critical_cols)
            
            # Remove cases with invalid timestamps (future dates or too old)
            current_time = pd.Timestamp.now()
            df = df[
                (df['time:timestamp'] <= current_time) & 
                (df['time:timestamp'] >= current_time - pd.Timedelta(days=365))
            ]
            
            # Remove cases with suspicious patterns (e.g., zero duration)
            case_durations = df.groupby('case:concept:name')['time:timestamp'].agg(['min', 'max'])
            valid_cases = case_durations[case_durations['max'] > case_durations['min']].index
            df = df[df['case:concept:name'].isin(valid_cases)]
            
            # Convert back to event log
            cleaned_log = pm4py.convert_to_event_log(df)
            return cleaned_log
            
        except Exception as e:
            raise ValueError(f"Error cleaning event log: {e}")

    def extract_case_attributes(self, event_log):
        """
        Extract enhanced case-level attributes from the event log.
        """
        try:
            df = pm4py.convert_to_dataframe(event_log)
            case_attributes = {}
            
            for case_id, case_data in df.groupby('case:concept:name'):
                # Basic temporal metrics
                start_time = case_data['time:timestamp'].min()
                end_time = case_data['time:timestamp'].max()
                duration = (end_time - start_time).total_seconds() / 3600
                
                # Process metrics
                unique_activities = len(case_data['concept:name'].unique())
                unique_resources = len(case_data['org:resource'].unique())
                total_cost = case_data['costs'].sum() if 'costs' in case_data.columns else None
                
                # Advanced metrics
                if 'claim_value' in case_data.columns:
                    avg_claim_value = case_data['claim_value'].mean()
                else:
                    avg_claim_value = None
                
                if 'risk_level' in case_data.columns:
                    risk_level = case_data['risk_level'].iloc[0]
                else:
                    risk_level = None
                
                attributes = {
                    'temporal': {
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration_hours': duration
                    },
                    'process': {
                        'num_events': len(case_data),
                        'unique_activities': unique_activities,
                        'unique_resources': unique_resources,
                        'total_cost': total_cost
                    },
                    'business': {
                        'claim_value': avg_claim_value,
                        'risk_level': risk_level,
                        'activities_sequence': list(case_data['concept:name'])
                    }
                }
                
                case_attributes[case_id] = attributes
            
            return case_attributes
            
        except Exception as e:
            raise ValueError(f"Error extracting case attributes: {e}")
