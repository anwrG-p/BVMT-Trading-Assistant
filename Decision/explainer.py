import google.generativeai as genai
import os

class PortfolioExplainer:
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        """
        Initialize the Explainer using Google Gemini.
        """
        self.api_key = api_key if api_key else os.getenv('GEMINI_API_KEY')
        self.model_name = model
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            print("Warning: No API Key provided for Gemini.")
            self.model = None

    def generate_explanation(self, portfolio_weights, confidence_scores, persona):
        
        # 1. Construct the Prompt based on Persona
        prompt = self._construct_prompt(portfolio_weights, confidence_scores, persona)
        
        # 2. Call the LLM
        print("\n--- Generating Explanation with Gemini... ---")
        
        if not self.model:
            return "[Error] No API Key configured. Cannot generate explanation."
            
        try:
            response = self.model.generate_content(prompt)
            # Check if response is valid
            if response.text:
                return response.text
            else:
                return "Gemini returned an empty response."
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return "[Note] AI Explanation unavailable: API Quota Exceeded (Free Tier). Optimization results above are valid."
            else:
                print(f"[Error] Gemini API: {e}")
                return f"Failed to generate explanation. Error: {e}"

    def _construct_prompt(self, weights, scores, persona):
        prompt = f"""
        You are a financial advisor for a '{persona}' investor.
        
        Task: Explain the following portfolio allocation decision.
        
        Data:
        - Portfolio Allocation: {weights}
        - AI Confidence Scores: {scores}
        
        """
        
        if persona == "Available" or persona == "Conservative": 
            prompt += """
            Tone: Professional, risk-averse, reassuring.
            Focus: Highlight stability, low volatility, and why these choices minimize downside risk.
            """
        elif persona == "Aggressive": 
            prompt += """
            Tone: Exciting, growth-oriented, forward-looking.
            Focus: Highlight potential for high returns, growth opportunities, and why we are "betting" on these assets despite risks.
            """
            
        prompt += "\nExplain 'Why' we chose these stocks in 2-3 sentences."
        return prompt

# Example Usage
if __name__ == "__main__":
    explainer = PortfolioExplainer(api_key="AIzaSyD_YIpoubkm_ET4IbTJD4stqKdlzhS58aE")
    
    # Dummy data
    weights = {'AAPL': 0.4, 'GOOG': 0.6}
    scores = {'AAPL': 85, 'GOOG': 92}
    
    # Test Persona 1
    print("\n--- Explanation for Ahmed (Conservative) ---")
    explainer.generate_explanation(weights, scores, persona="Conservative")
    
    # Test Persona 2
    print("\n--- Explanation for Leila (Aggressive) ---")
    explainer.generate_explanation(weights, scores, persona="Aggressive")
