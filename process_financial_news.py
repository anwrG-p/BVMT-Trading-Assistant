import logging
import time
from src.nlp_engine.sentiment_analyzer import FinancialSentimentEngine
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("sentiment_analysis.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    input_path = os.path.join("data", "raw", "tustex_news.csv")
    output_path = os.path.join("data", "processed", "financial_sentiment_index.csv")
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    logger.info(f"Starting sentiment analysis pipeline...")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    
    start_time = time.time()
    try:
        engine = FinancialSentimentEngine()
        engine.run_analysis(input_path, output_path)
        elapsed = time.time() - start_time
        logger.info(f"Analysis complete in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
