from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import scraper  
import wandb

wandb.init(project="FinBERT_Stock_Sentiment_Analysis")

app = FastAPI(title="FinBERT Stock Sentiment API")

model_path = "./finbert_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

labels = ["negative", "neutral", "positive"]

scraped_data = []


@app.get("/")
def home():
    return {"message": "Welcome to FinBERT Sentiment API!"}


@app.get("/scrape")
def scrape_news():
    global scraped_data
    scraped_data = scraper.scrape_all()
    return {"count": len(scraped_data), "headlines": scraped_data[:10]}  # show sample


@app.get("/predict")
def predict_sentiment():
    if not scraped_data:
        return {"error": "No headlines found. Run /scrape first!"}

    results = []

    for headline in scraped_data:
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred_label = labels[torch.argmax(probs)]
        confidence = torch.max(probs).item()

        results.append({
            "headline": headline,
            "sentiment": pred_label,
            "confidence": round(confidence, 3)
        })

        wandb.log({
            "headline": headline,
            "predicted_label": pred_label,
            "confidence": confidence
        })

    return {"predictions": results}
