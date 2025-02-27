import os
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from environment variables.
    """
    load_dotenv()

    config = {
        # API Keys
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),

        # Process Mining Settings
        'PM4PY_SETTINGS': {
            'CASE_ID_KEY': 'case:concept:name',
            'ACTIVITY_KEY': 'concept:name',
            'TIMESTAMP_KEY': 'time:timestamp',
            'RESOURCE_KEY': 'org:resource'
        },

        # Visualization Settings
        'VISUALIZATION': {
            'PROCESS_MAP': {
                'FORMAT': 'png',
                'SHOW_FREQUENCY': True
            },
            'CHARTS': {
                'THEME': 'plotly',
                'COLOR_PALETTE': 'Set3'
            }
        },

        # Performance Settings
        'PERFORMANCE': {
            'TIMEUNIT': 'hours',
            'AGGREGATE_METHOD': 'mean'
        }
    }

    # Validate required configuration
    if not config['GEMINI_API_KEY']:
        raise ValueError(
            "Gemini API key not found. Please add GEMINI_API_KEY to your .env file"
        )

    return config
