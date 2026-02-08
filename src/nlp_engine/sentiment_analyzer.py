import pandas as pd
import re
import torch
import logging
from transformers import pipeline
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialSentimentEngine:
    """
    A professional Financial Sentiment Engine using multilingual transformers.
    """
    
    # Financial terms to PRESERVE during stopword filtering
    CRITICAL_FINANCIAL_TERMS = {
        'hausse', 'baisse', 'croissance', 'déficit', 'inflation', 'taux', 'bct', 
        'banque', 'marché', 'bourse', 'investisseur', 'risque', 'profit', 'perte',
        'chiffre', 'affaires', 'dette', 'crédit', 'obligataire', 'action', 'dividende',
        'revenue', 'bénéfice', 'gain', 'perte', 'stabilité', 'volatilité'
    }

    # Tunisian Banks and Currency Entities
    ENTITIES = {
        'TND': r'\b(tnd|dinar|dt)\b',
        'BCT': r'\b(bct|banque centrale)\b',
        'BIAT': r'\b(biat|banque internationale arabe de tunisie)\b',
        'BNA': r'\b(bna|banque nationale agricole)\b',
        'STB': r'\b(stb|société tunisienne de banque)\b',
        'BH': r'\b(bh|banque de l\'habitat)\b',
        'Attijari': r'\b(attijari)\b',
        'BT': r'\b(bt|banque de tunisie)\b',
        'UIB': r'\b(uib|union internationale de banques)\b',
        'UBCI': r'\b(ubci)\b',
        'ATB': r'\b(atb|arab tunisian bank)\b',
        'Amen Bank': r'\b(amen bank)\b'
    }

    def __init__(self, model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"):
        """
        Initialize the sentiment engine with a transformer model.
        Switched to XLM-RoBERTa for better Arabic/French support.
        """
        logger.info(f"Loading sentiment model: {model_name}...")
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            self.pipeline = pipeline(
                "sentiment-analysis", 
                model=model_name, 
                tokenizer=model_name,
                device=self.device
            )
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess(self, text: str) -> str:
        """
        Strip non-textual characters (emojis) and clean text.
        """
        if not isinstance(text, str):
            return ""
        
        # Remove emojis (surrogates)
        clean_text = text.encode('utf-16', 'surrogatepass').decode('utf-16')
        
        # Regex for emoji ranges (simplified)
        emoji_pattern = re.compile(
            u"(\ud83d[\ude00-\ude4f])|"  # emoticons
            u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
            u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
            u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
            u"(\ud83c[\udde0-\uddff])"   # flags (iOS)
            "+", flags=re.UNICODE)
        
        clean_text = emoji_pattern.sub(r'', clean_text)
        
        # Normalize whitespace
        clean_text = " ".join(clean_text.split())
        
        return clean_text

    def analyze_entity_sentiment(self, text: str) -> Dict[str, str]:
        """
        Detect entities.
        """
        text_lower = text.lower()
        detected_entities = {}
        
        for entity_name, pattern in self.ENTITIES.items():
            if re.search(pattern, text_lower):
                detected_entities[entity_name] = "Mentioned"
                
        return detected_entities

    def _map_labels_to_sentiment(self, label: str, score: float) -> Dict[str, Union[float, str]]:
        """
        Map XLM-R labels (LABEL_0, LABEL_1, LABEL_2) or (Negative, Neutral, Positive) to our format.
        CardiffNLP model outputs: 
        LABEL_0 -> Negative
        LABEL_1 -> Neutral
        LABEL_2 -> Positive
        """
        # Sometimes pipeline returns "LABEL_0", sometimes "negative" depending on config.
        # Let's handle both or check config. usually cardiffnlp maps to Label_0 etc if no id2label.
        # But let's assume standard mapping for this model:
        # 0: Negative, 1: Neutral, 2: Positive
        
        label_map = {
            "LABEL_0": {"label": "Bearish", "polarity": 0.0},
            "LABEL_1": {"label": "Neutral", "polarity": 0.5},
            "LABEL_2": {"label": "Bullish", "polarity": 1.0},
            "negative": {"label": "Bearish", "polarity": 0.0},
            "neutral":  {"label": "Neutral", "polarity": 0.5},
            "positive": {"label": "Bullish", "polarity": 1.0}
        }
        
        # Handle case-insensitive mapping just in case
        clean_label = label.upper() if "LABEL" in label else label.lower()
        
        sentiment = label_map.get(clean_label)
        if not sentiment:
            # Fallback if unknown label
            logger.warning(f"Unknown label received: {label}")
            return {"label": "Neutral", "polarity": 0.5}
            
        return sentiment

    def analyze_text(self, text: str, source: str = "General") -> Dict[str, Union[float, str]]:
        """
        Analyze text and return structured sentiment.
        """
        cleaned_text = self.preprocess(text)
        if not cleaned_text:
            return {"polarity": 0.5, "label": "Neutral", "confidence": 0.0, "weight": 1.0, "entities": []}

        # Truncate text
        cleaned_text = cleaned_text[:1500]

        # Run pipeline
        try:
            result = self.pipeline(cleaned_text, truncation=True, max_length=512)[0]
            # Result example: {'label': 'LABEL_2', 'score': 0.98}
            
            mapped = self._map_labels_to_sentiment(result['label'], result['score'])
            polarity = mapped['polarity']
            label = mapped['label']
            confidence = result['score']

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"polarity": 0.5, "label": "Neutral", "confidence": 0.0, "weight": 1.0, "entities": []}

        # Macro-Economic Weighting for BCT
        weight = 1.5 if "bct" in source.lower() or "banque centrale" in source.lower() else 1.0

        # Entity detection
        entities = self.analyze_entity_sentiment(cleaned_text)

        return {
            "polarity": polarity,
            "label": label,
            "confidence": confidence,
            "weight": weight,
            "entities": list(entities.keys())
        }

    def run_analysis(self, input_path: str, output_path: str):
        """
        Process CSV file and save results.
        """
        logger.info(f"Reading data from {input_path}")
        try:
            df = pd.read_csv(input_path)
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return

        if 'full_text' not in df.columns:
            logger.error("Column 'full_text' not found in CSV.")
            return

        results = []
        
        logger.info(f"Analyzing {len(df)} rows...")
        for index, row in df.iterrows():
            text = str(row['full_text'])
            title = str(row.get('title', ''))
            # Combine title and text for better context? Usually yes.
            full_content = f"{title}. {text}"
            
            # Determine source for weighting (heuristic based on text or explicit source col if exists)
            # Assuming text content determines if it's BCT related if no source col
            source = "BCT" if "banque centrale" in full_content.lower() or "bct" in full_content.lower() else "General"
            
            sentiment = self.analyze_text(full_content, source=source)
            
            results.append({
                "date": row.get('date', ''),
                "title": title,
                "polarity": sentiment['polarity'],
                "label": sentiment['label'],
                "confidence": sentiment['confidence'],
                "weight": sentiment['weight'],
                "entity_sentiment": ",".join(sentiment['entities'])
            })
            
            if (index + 1) % 10 == 0:
                logger.info(f"Processed {index + 1} rows")

        result_df = pd.DataFrame(results)
        result_df.to_csv(output_path, index=False)
        logger.info(f"Sentiment analysis saved to {output_path}")

if __name__ == "__main__":
    # Test run
    engine = FinancialSentimentEngine()
    test_text = "La BCT a décidé de maintenir le taux directeur inchangé. C'est une décision prudente."
    print(engine.analyze_text(test_text, source="BCT"))
