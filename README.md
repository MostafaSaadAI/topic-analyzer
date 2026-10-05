# Topic Analyzer

Collects news about any topic and analyzes its sentiment in Arabic and English, with an interactive dashboard.

## What it does
- Collects articles from NewsAPI and RSS feeds
- Cleans text and removes duplicate stories (RapidFuzz)
- Scores sentiment with a multilingual XLM-RoBERTa model (no translation step)
- Stores results in SQLite so the dataset grows over time
- Streamlit dashboard: sentiment split, articles per day, trend, tone by source, top keywords

## Setup
```bash
git clone https://github.com/YOUR_USERNAME/topic-analyzer.git
cd topic-analyzer
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create a `.env` file with your own NewsAPI key (free at newsapi.org):

```
NEWSAPI_KEY=your_key_here
```


## Run
```bash
python collect.py "Artificial Intelligence"
streamlit run app.py
```

The first run downloads the model (about 1 GB each for two files).

## Evaluation
```bash
python evaluate.py --export
python evaluate.py
```
Label the exported file by hand, save it as `data/labeled_sample.csv`, then run the second command to compare VADER with the transformer.

## Limitations
- Sentiment measures the tone of a headline, not its stance toward a topic.
- Analysis uses headlines plus a short description, not the full article.
- The free NewsAPI plan only covers the last ~29 days.

## Tech stack
Python, Hugging Face Transformers, PyTorch, Streamlit, Plotly, SQLite, Pandas
