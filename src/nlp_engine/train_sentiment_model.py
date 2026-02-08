import pandas as pd
import torch
import logging
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import Dataset
from typing import Dict, List, Optional
from sentiment_analyzer import FinancialSentimentEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentTrainer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment", output_dir: str = "models/bvmt_sentiment_model"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
        # Use the engine's list of entities and terms for filtering
        self.financial_terms = FinancialSentimentEngine.CRITICAL_FINANCIAL_TERMS
        self.entities = FinancialSentimentEngine.ENTITIES

    def load_and_preprocess_data(self, file_path: str) -> Dataset:
        """
        Load data from CSV, filter for relevance, and convert to HuggingFace Dataset.
        """
        logger.info(f"Loading data from {file_path}")
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("CSV must contain 'text' and 'label' columns.")

        # 1. Filter: Keep only rows relevant to BVMT/Finance
        # We join terms and entity regexes to check existence
        # Check if text contains any financial term or entity
        # Creating a simple keyword list check for efficiency (regex is safer but slower, let's mix)
        
        logger.info(f"Initial dataset size: {len(df)}")
        
        # Simple keyword check for now
        relevant_keywords = list(self.financial_terms) + list(self.entities.keys())
        
        def is_relevant(text):
            text_lower = str(text).lower()
            return any(term in text_lower for term in relevant_keywords)

        # Apply filtering
        df = df[df['text'].apply(is_relevant)]
        logger.info(f"Dataset size after relevance filtering: {len(df)}")

        # 2. Cleaning: Use the engine's preprocess method (static or instantiated)
        # Since preprocess is an instance method and doesn't rely on self state much (just regex), 
        # we can instantiate a temporary engine or copy the logic. 
        # Better: Instantiate engine to reuse logic.
        engine = FinancialSentimentEngine(model_name=self.model_name) 
        
        df['text'] = df['text'].apply(engine.preprocess)
        
        # Drop empty strings
        df = df[df['text'].str.strip() != ""]
        logger.info(f"Dataset size after cleaning: {len(df)}")
        
        if df.empty:
            raise ValueError("No valid data remaining after filtering and cleaning.")

        # Convert to HF Dataset
        # Map labels if they are strings (Bearish, Neutral, Bullish) -> 0, 1, 2
        # Assuming label col is already 0, 1, 2 or needs mapping.
        # Let's inspect first element type if possible, or force mapping if strings.
        if df['label'].dtype == 'object':
             label_map = {"Bearish": 0, "Negative": 0, "Neutral": 1, "Bullish": 2, "Positive": 2}
             df['label'] = df['label'].map(label_map)
             df = df.dropna(subset=['label']) # Drop unknown labels
             df['label'] = df['label'].astype(int)

        dataset = Dataset.from_pandas(df)
        return dataset

    def tokenize_function(self, examples):
        return self.tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

    def train(self, data_path: str, epochs: int = 3, batch_size: int = 8, smoke_test: bool = False):
        dataset = self.load_and_preprocess_data(data_path)
        
        tokenized_datasets = dataset.map(self.tokenize_function, batched=True)
        
        # Split
        if len(tokenized_datasets) > 10:
             train_test = tokenized_datasets.train_test_split(test_size=0.2)
             train_dataset = train_test['train']
             eval_dataset = train_test['test']
        else:
            # Too small for split (e.g. dummy data)
            train_dataset = tokenized_datasets
            eval_dataset = tokenized_datasets

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs if not smoke_test else 1,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            weight_decay=0.01,
            learning_rate=2e-5,
            eval_strategy="epoch" if len(dataset) > 10 else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if len(dataset) > 10 else False,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=10,
            use_cpu=not torch.cuda.is_available(),
            save_steps=500 if not smoke_test else 10 # frequent saves for test? No, save_strategy epoch handles it.
        )
        
        # If smoke test, reduce steps
        if smoke_test:
            training_args.max_steps = 2
            logger.info("Running in SMOKE TEST mode (2 steps)")

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=DataCollatorWithPadding(tokenizer=self.tokenizer),
        )

        logger.info("Starting training...")
        trainer.train()
        
        logger.info(f"Saving model to {self.output_dir}")
        trainer.save_model(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        logger.info("Training complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True, help="Path to labeled CSV")
    parser.add_argument("--smoke_test", action="store_true", help="Run a quick smoke test")
    args = parser.parse_args()

    trainer = SentimentTrainer()
    trainer.train(data_path=args.data_path, smoke_test=args.smoke_test)
