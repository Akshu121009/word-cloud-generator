import re
from collections import Counter
from io import BytesIO

import streamlit as st
from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk


# Basic page settings
st.set_page_config(page_title="Word Cloud Generator", page_icon="☁️", layout="wide")


@st.cache_resource
def load_stop_words():
    """Load common English words that usually do not add much meaning."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


def clean_and_count(text, extra_words):
    """Clean the text and count the useful words."""
    text = text.lower()
    words = re.findall(r"\b[a-z]+\b", text)

    # Copy the list so custom words do not change the shared stop-word list.
    blocked_words = set(load_stop_words())
    for word in extra_words.split(","):
        word = word.strip().lower()
        if word:
            blocked_words.add(word)

    useful_words = [
        word for word in words
        if word not in blocked_words and len(word) > 1
    ]
    return Counter(useful_words)


def make_wordcloud(word_counts, color_theme, background):
    """Create the word cloud and return it as a PNG image."""
    cloud = WordCloud(
        width=1200,
        height=600,
        background_color=background,
        colormap=color_theme,
        max_words=120,
        collocations=False,
        random_state=42,
    ).generate_from_frequencies(word_counts)

    image_buffer = BytesIO()
    cloud.to_image().save(image_buffer, format="PNG")
    image_buffer.seek(0)
    return image_buffer.getvalue()


def reset_results():
    """Clear the typed text and the last generated results."""
    for key in ("document_text", "extra_words", "word_counts", "word_cloud_png", "source_text"):
        st.session_state.pop(key, None)


st.title("☁️ Word Cloud Generator")
st.write(
    "Paste some text and find out which words appear most often. "
    "The most frequent words will appear larger in the word cloud."
)

with st.sidebar:
    st.header("Word Cloud Options")
    color_theme = st.selectbox(
        "Choose word colors",
        ["viridis", "plasma", "cool", "autumn", "winter", "Set2"],
        index=0,
    )
    background = st.selectbox(
        "Choose background",
        ["white", "black", "lightyellow"],
        index=0,
    )
    top_n = st.slider("Number of words in the table", 5, 30, 15)
    extra_words = st.text_input(
        "Words to ignore (optional)",
        key="extra_words",
        placeholder="e.g. college, project",
        help="Separate extra words with commas.",
    )

st.subheader("1. Add your text")
typed_text = st.text_area(
    "Paste text here",
    height=200,
    key="document_text",
    placeholder="Paste an article, class notes, or a paragraph...",
)
uploaded_file = st.file_uploader(
    "Or choose a plain-text file (.txt)",
    type=["txt"],
    key="uploaded_file",
)

text_to_analyze = typed_text
if uploaded_file is not None:
    try:
        uploaded_text = uploaded_file.getvalue().decode("utf-8-sig")
        if uploaded_text.strip():
            text_to_analyze = uploaded_text
            st.caption(f"Using uploaded file: {uploaded_file.name}")
        else:
            st.warning("The selected file is empty.")
    except UnicodeDecodeError:
        st.error("This file could not be read. Save it as UTF-8 text and try again.")
        text_to_analyze = ""

col_generate, col_reset = st.columns([3, 1])
with col_generate:
    generate_clicked = st.button(
        "Generate Word Cloud",
        type="primary",
        use_container_width=True,
    )
with col_reset:
    st.button(
        "Clear text and results",
        on_click=reset_results,
        use_container_width=True,
        help="Clears pasted text and the last results. Remove an uploaded file separately if one is selected.",
    )

if generate_clicked:
    if not text_to_analyze.strip():
        st.warning("Please paste some text or choose a .txt file first.")
    else:
        counts = clean_and_count(text_to_analyze, extra_words)
        if not counts:
            st.warning("No useful words were found. Try more text or remove some words from the ignore list.")
        else:
            st.session_state["word_counts"] = counts
            st.session_state["word_cloud_png"] = make_wordcloud(
                counts, color_theme, background
            )
            st.session_state["source_text"] = text_to_analyze

if "word_counts" in st.session_state:
    counts = st.session_state["word_counts"]
    png_image = st.session_state["word_cloud_png"]
    top_words = counts.most_common(top_n)

    st.divider()
    st.subheader("2. Your Word Cloud")
    st.image(png_image, use_container_width=True)
    st.download_button(
        "Download word cloud as PNG",
        data=png_image,
        file_name="word_cloud.png",
        mime="image/png",
    )

    st.subheader("3. Word Frequency")
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Total words counted", sum(counts.values()))
    metric_b.metric("Different words", len(counts))
    metric_c.metric("Most common word", top_words[0][0])

    st.caption("The table and chart show how often each word appears after cleaning.")
    st.bar_chart(
        { "Frequency": {word: frequency for word, frequency in top_words} },
        y="Frequency",
    )
    st.dataframe(
        [{"Word": word, "Frequency": frequency} for word, frequency in top_words],
        use_container_width=True,
        hide_index=True,
    )

    csv_text = "Word,Frequency\n" + "\n".join(
        f"{word},{frequency}" for word, frequency in counts.most_common()
    )
    st.download_button(
        "Download word counts as CSV",
        data=csv_text.encode("utf-8"),
        file_name="word_frequencies.csv",
        mime="text/csv",
    )

with st.expander("How this project works"):
    st.markdown(
        """
        1. The app changes the text to lowercase.
        2. It splits the text into words.
        3. It removes common English words and any extra words you choose.
        4. `Counter` counts how many times each word appears.
        5. `WordCloud` draws frequent words larger than less frequent words.
        6. The app displays the word cloud, chart, and frequency table.
        """
    )
