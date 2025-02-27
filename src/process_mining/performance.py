import pm4py

class PerformanceAnalyzer:
    def __init__(self):
        pass

    def calculate_cycle_time(self, event_log):
        """
        Calculate the cycle time for each case in the event log.
        """
        # Convert to dataframe for easier manipulation
        df = pm4py.convert_to_dataframe(event_log)
        
        # Calculate cycle time for each case
        cycle_times = []
        for case_id in df['case:concept:name'].unique():
            case_data = df[df['case:concept:name'] == case_id]
            start_time = case_data['time:timestamp'].min()
            end_time = case_data['time:timestamp'].max()
            duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
            cycle_times.append((case_id, duration))
        
        return cycle_times

    def calculate_waiting_time(self, event_log):
        """
        Calculate the waiting time between activities.
        """
        # Convert to dataframe for easier manipulation
        df = pm4py.convert_to_dataframe(event_log)
        df = df.sort_values(['case:concept:name', 'time:timestamp'])
        
        # Calculate waiting times between activities
        waiting_times = {}
        for case_id in df['case:concept:name'].unique():
            case_data = df[df['case:concept:name'] == case_id].reset_index()
            for i in range(len(case_data)-1):
                activity = case_data.loc[i, 'concept:name']
                next_activity = case_data.loc[i+1, 'concept:name']
                wait_time = (case_data.loc[i+1, 'time:timestamp'] - 
                           case_data.loc[i, 'time:timestamp']).total_seconds() / 3600
                
                key = f"{activity} → {next_activity}"
                if key not in waiting_times:
                    waiting_times[key] = []
                waiting_times[key].append(wait_time)
        
        # Calculate average waiting times
        avg_waiting_times = {k: sum(v)/len(v) for k, v in waiting_times.items()}
        return avg_waiting_times

    def calculate_sojourn_time(self, event_log):
        """
        Calculate the time spent in each activity.
        """
        # Convert to dataframe
        df = pm4py.convert_to_dataframe(event_log)
        
        # Group by activity and calculate statistics
        activity_times = {}
        for activity in df['concept:name'].unique():
            activity_data = df[df['concept:name'] == activity]
            activity_times[activity] = {
                'count': len(activity_data),
                'avg_timestamp': activity_data['time:timestamp'].mean(),
                'min_timestamp': activity_data['time:timestamp'].min(),
                'max_timestamp': activity_data['time:timestamp'].max()
            }
            
        return activity_times
