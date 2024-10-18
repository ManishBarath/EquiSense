from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# Load model & tokenizer from local folder
model_path = "finbert_model"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)


tokenizer = AutoTokenizer.from_pretrained("finbert_model")
print("Tokenizer loaded successfully!")
print(tokenizer(["Company reports profits"]))


model.eval()

# Sample headline
headline = "Company X reports strong profits"

# Tokenize
inputs = tokenizer([headline], padding=True, truncation=True, return_tensors='pt')

# Predict
with torch.no_grad():
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1).numpy()

# Find predicted sentiment
sentiment_idx = np.argmax(probs[0])
sentiment = ["Positive", "Negative", "Neutral"][sentiment_idx]
confidence = float(max(probs[0]))

print(f"Headline: {headline}")
print(f"Sentiment: {sentiment}, Confidence: {confidence:.2f}")
