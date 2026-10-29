# word-cloud-generator
A Python Streamlit application that generates word clouds from text

# Word Cloud Generator

A beginner-friendly Python mini-project built with Streamlit.

## Features
- Paste text or upload a `.txt` file
- Remove common English stop words
- Add your own words to ignore
- Choose word-cloud colors and background
- View word frequencies in a chart and table
- Download the word cloud as PNG and counts as CSV
- Clear pasted text and the latest results

## Run on Windows
Open PowerShell in this project folder and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## How it works
The app cleans the text, removes stop words, counts remaining words with Python's `Counter`, and uses the `wordcloud` library to create an image.

Note: the Clear button clears pasted text and generated results. If you uploaded a file, remove it from the file uploader separately.
