import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiInterface:
    def __init__(self):
        # Configure the Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-001')

    def generate_response(self, prompt):
        """
        Generate a response from the Gemini API based on the given prompt.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

# Example usage:
if __name__ == '__main__':
    gemini = GeminiInterface()
    response = gemini.generate_response("What is process mining?")
    print(response)
