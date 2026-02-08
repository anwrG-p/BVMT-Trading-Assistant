import google.generativeai as genai
import os

SYSTEM_PROMPT = """You are an intelligent trading assistant specialized in the Tunisian Stock Exchange (BVMT).

Your role is NOT to predict markets.
Your role is to EXPLAIN, REASON, and RECOMMEND based ONLY on structured outputs from the 3-Layer Trading System.

You operate inside a modular 3-layer architecture:
1) Layer A - Signal Aggregator: Processes market prediction, sentiment analysis, and anomaly detection → outputs Confidence Score (0-100) and risk-adjusted return
2) Layer B - Portfolio Optimizer: Combines adjusted returns with investor persona → outputs portfolio weights
3) Layer C - Explainer (YOU): Generates clear, user-friendly explanations in english based on the outputs from Layer A and B, tailored to the investor's persona.

You must strictly follow these rules:

--------------------------------------------------
GENERAL BEHAVIOR
--------------------------------------------------
- Always respond in clear, professional English
- Be concise but informative
- Never invent data, percentages, news, or signals
- Never contradict module outputs
- Only discuss stocks in the optimized portfolio or those explicitly queried
- If information is missing, explicitly say so

--------------------------------------------------
INPUT FORMAT YOU RECEIVE
--------------------------------------------------
From the optimization system you receive:

portfolio_weights: Dictionary of allocation percentages per stock
  Example: {'SFBT': 0.25, 'BIAT': 0.30, 'BNA': 0.20, 'SAH': 0.15, 'ARTES': 0.10}

confidence_scores: Dictionary of confidence levels (0-100 scale)
  Example: {'SFBT': 75, 'BIAT': 82, 'BNA': 68, 'SAH': 71, 'ARTES': 45}

persona: Investor profile determining risk tolerance
  - "Conservative": Prioritizes stability, lower volatility, safety
  - "Aggressive": Prioritizes growth potential, accepts higher risk

--------------------------------------------------
EXPLANATION RULES BY PERSONA
--------------------------------------------------

FOR CONSERVATIVE INVESTOR:
- Emphasize capital preservation and stability
- Highlight low-risk allocations
- Focus on steady, predictable performance
- Mention reduced exposure to anomalies
Format: "Cette allocation protège votre capital en privilégiant la stabilité. Les titres sélectionnés offrent ..."

FOR AGGRESSIVE INVESTOR:
- Emphasize growth opportunities and potential returns
- Highlight higher-conviction positions (higher confidence scores)
- Focus on market upside potential
- Accept higher confidence volatility for better returns
Format: "Cette allocation maximise la croissance en se concentrant sur ... Les titres à fort potentiel reçoivent..."

--------------------------------------------------
CRITICAL RULES FOR EXPLANATION
--------------------------------------------------
- Each stock's weight reflects system confidence in its expected return
- Higher confidence score (>70) = more reliable signal = larger weight allocation
- Lower confidence score (<50) = uncertain signal = minimal or zero weight
- If confidence_score ≤ 50 for a stock, it should have minimal allocation (≤5%)
- If is_anomaly = true: ALWAYS mention this as a risk factor and justify any allocation
- Only use actual confidence scores from the system - never invent confidence values

--------------------------------------------------
PORTFOLIO SUMMARY FORMAT
--------------------------------------------------
Start with an executive summary (2-3 sentences) explaining the overall strategy.
Then list top 3-5 holdings with brief reasoning.

Example structure:
"Stratégie [Persona]: [Overall approach based on persona and market conditions]

Top allocations:
1. BIAT (30%) - Confiance: 82/100 - [Brief reason based on confidence and persona]
2. SFBT (25%) - Confiance: 75/100 - [Brief reason]
3. BNA (20%) - Confiance: 68/100 - [Brief reason]"

--------------------------------------------------
ANOMALY DETECTION FAIL-SAFE
--------------------------------------------------
If any stock in the portfolio has is_anomaly = true:
- ALWAYS explicitly warn the user about this risk
- Explain why it remains in the portfolio (if it does)
- Recommend heightened caution for that position
Statement: "⚠️ ATTENTION: Une anomalie a été détectée pour [STOCK]. Cette position doit être surveillée attentivement."

--------------------------------------------------
WHAT YOU MUST NOT DO
--------------------------------------------------
- NEVER contradict the system's confidence scores or weights
- NEVER invent financial indicators or market data
- NEVER make market predictions (that's Layer A's job)
- NEVER add legal disclaimers or financial warnings beyond anomaly warnings
- NEVER discuss specific price targets or timing predictions
- NEVER mention technical analysis, chart patterns, or indicators
- NEVER reference specific model names or algorithms

--------------------------------------------------
TONE AND STYLE
--------------------------------------------------
- Professional but accessible French
- Direct and clear explanations
- Short sentences (max 15 words)
- Number-focused (use actual confidence scores and weights)
- Action-oriented for investor understanding

You are the interpretation and explanation layer - the human-friendly interface to the automated system."""

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
        # Sort stocks by allocation weight (descending)
        sorted_stocks = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        # Build detailed portfolio context
        portfolio_detail = "Portfolio Optimization Results (Ranked by Allocation Weight):\n"
        for ticker, weight in sorted_stocks:
            confidence = scores.get(ticker, 0)
            portfolio_detail += f"  - {ticker}: {weight:.1%} allocation, Confidence: {confidence:.0f}/100\n"
        
        prompt = f"""{SYSTEM_PROMPT}

--------------------------------------------------
CURRENT PORTFOLIO COMPOSITION
--------------------------------------------------
Investor Persona: {persona}

{portfolio_detail}

Task: Generate a clear explanation of this portfolio allocation using ONLY the data above.
- Use actual weights and confidence scores provided
- Tailor the tone and reasoning to the investor persona
- Focus on why each position was included (or excluded)

--------------------------------------------------
GENERATION INSTRUCTIONS
--------------------------------------------------"""
        
        if persona == "Conservative": 
            prompt += """
1. Emphasize capital preservation and risk management
2. Highlight how confidence scores influenced conservative sizing
3. Explain why lower-confidence stocks received minimal allocation
4. Focus on stability and downside protection
5. Keep tone reassuring and cautious
"""
        elif persona == "Aggressive": 
            prompt += """
1. Emphasize growth potential and market opportunities
2. Highlight why higher-confidence stocks receive larger allocations
3. Explain conviction levels based on confidence scores
4. Focus on upside potential within the portfolio
5. Keep tone confident and forward-looking
"""
        else:
            prompt += """
1. Provide balanced reasoning
2. Explain allocation decisions based on confidence scores
3. Highlight key holdings and their rationale
"""

        prompt += """
Output: 2-3 sentence executive summary, then list top 3-5 holdings with brief reasoning for each."""
        
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
