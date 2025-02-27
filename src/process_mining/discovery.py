import pm4py

class ProcessDiscovery:
    def __init__(self):
        pass

    def discover_process_map(self, event_log):
        """
        Discover a process map from the event log using the Alpha algorithm.
        """
        try:
            net, initial_marking, final_marking = pm4py.discover_petri_net_alpha(event_log)
            return net, initial_marking, final_marking
        except Exception as e:
            raise ValueError(f"Error in process map discovery: {str(e)}")

    def discover_bpmn_model(self, event_log):
        """
        Discover a BPMN model from the event log using the Inductive Miner.
        """
        try:
            bpmn_model = pm4py.discover_bpmn_inductive(event_log)
            return bpmn_model
        except Exception as e:
            raise ValueError(f"Error in BPMN discovery: {str(e)}")

    def discover_dfg(self, event_log):
        """
        Discover a Directly-Follows Graph (DFG) from the event log.
        """
        try:
            # Get start and end activities first
            start_activities = pm4py.get_start_activities(event_log)
            end_activities = pm4py.get_end_activities(event_log)
            
            # Get the DFG with frequency
            dfg = pm4py.discover_directly_follows_graph(event_log)
            
            # Convert frequency to dictionary for compatibility
            dfg_dict = {(k[0], k[1]): v for k, v in dfg.items()}
            
            return dfg_dict, start_activities, end_activities
        except Exception as e:
            raise ValueError(f"Error in DFG discovery: {str(e)}")
