class InsightGenerator:
    def __init__(self, gemini_interface):
        self.gemini_interface = gemini_interface

    def generate_process_insights(self, event_log, process_model):
        """
        Generate insights about the process based on the event log and process model.
        """
        prompt = f"Analyze the following process model and event log to identify bottlenecks, inefficiencies, and areas for improvement. {process_model} {event_log}"
        insights = self.gemini_interface.generate_response(prompt)
        return insights

    def generate_kpi_recommendations(self, event_log):
        """
        Generate KPI recommendations based on the event log.
        """
        prompt = f"Based on the following event log, recommend relevant KPIs for process monitoring and improvement. {event_log}"
        kpis = self.gemini_interface.generate_response(prompt)
        return kpis

    def generate_conversational_analysis(self, query, event_log):
        """
        Generate a conversational analysis based on the given query and event log.
        """
        prompt = f"Answer the following question about the event log: {query} {event_log}"
        answer = self.gemini_interface.generate_response(prompt)
        return answer
