from src.nlp_engine.sentiment_analyzer import FinancialSentimentEngine
import logging

# Configure basic logging to console
logging.basicConfig(level=logging.INFO)

def test_sentiment_engine():
    print("Initializing Engine...")
    engine = FinancialSentimentEngine()

    test_cases = [
        # French - Bullish
        {
            "text": "La croissance économique de la Tunisie est en forte hausse de 3% cette année.",
            "source": "General",
            "expected_label": ["Bullish", "Very Bullish"]
        },
        # French - Bearish
        {
            "text": "Le déficit budgétaire s'aggrave et l'inflation atteint des sommets inquiétants.",
            "source": "General",
            "expected_label": ["Bearish", "Very Bearish"]
        },
        # BCT weighting check
        {
            "text": "La Banque Centrale de Tunisie maintient son taux directeur pour stabiliser l'inflation.",
            "source": "BCT", # Should trigger weighting
            "expected_weight": 1.5
        },
        # Entity Detection
        {
            "text": "La BIAT a réalisé un bénéfice record alors que le TND se stabilise face à l'euro.",
            "source": "General",
            "check_entities": True
        },
        # Arabic check (MSA) - If supported
        {
            "text": "سجلت البورصة التونسية ارتفاعا ملحوظا اليوم.",
             "source": "General",
             # Just checking it runs without error really, as nlptown is mostly Western langs
             "check_run": True
        }
    ]

    print("\n--- Running Tests ---")
    for i, case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {case['text'][:50]}...")
        try:
            result = engine.analyze_text(case['text'], source=case.get('source', 'General'))
            print(f"Result: {result}")
            
            if 'expected_label' in case:
                assert result['label'] in case['expected_label'], f"Expected {case['expected_label']}, got {result['label']}"
                print("Label Check: PASSED")
            
            if 'expected_weight' in case:
                assert result['weight'] == case['expected_weight'], f"Expected weight {case['expected_weight']}, got {result['weight']}"
                print("Weight Check: PASSED")

            if case.get('check_entities'):
                assert 'BIAT' in result['entities'], "Failed to detect BIAT"
                assert 'TND' in result['entities'], "Failed to detect TND"
                print("Entity Check: PASSED")
                
        except AssertionError as e:
            print(f"FAILED: {e}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_sentiment_engine()
