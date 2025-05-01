from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config import *


def analyze_text(data):
    """Анализируем текст и определяем сентимент"""
    full_data = ""
    wb = openpyxl.load_workbook("scrapping.xlsx")
    sheet = wb["Tbank"]

    for row in range(2, 10):
        cell_name = f"C{row}"
        text = sheet[cell_name].value
        full_data += text + "\n"

    words = word_tokenize(full_data)
    stop_words = set(stopwords.words("russian"))
    freq_table = {}

    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        freq_table[word] = freq_table.get(word, 0) + 1

    sentences = sent_tokenize(full_data)
    sentence_value = {}

    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                sentence_value[sentence] = sentence_value.get(sentence, 0) + freq

    average = sum(sentence_value.values()) / len(sentence_value)
    summary = " ".join(
        sentence for sentence in sentences
        if sentence in sentence_value and sentence_value[sentence] > (SUMMARY_THRESHOLD * average)
    )

    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(summary)

    if sentiment_scores["neg"] > sentiment_scores["pos"]:
        recommendation = "NOT WORTH INVESTING"
        result_color = "#FF3333"
    elif sentiment_scores["neg"] < sentiment_scores["pos"]:
        recommendation = "WORTH INVESTING"
        result_color = "#33FF33"
    else:
        recommendation = "NEUTRAL"
        result_color = PRIMARY_COLOR

    fig = plt.figure(figsize=(8, 4), facecolor=SECONDARY_COLOR)
    ax = fig.add_subplot(facecolor=SECONDARY_COLOR)

    sns.barplot(
        x=list(sentiment_scores.keys()),
        y=list(sentiment_scores.values()),
        palette=["#FF3333", PRIMARY_COLOR, "#33FF33", "#888888"]
    )

    plt.title("Sentiment Analysis", color=TEXT_COLOR)
    plt.ylabel("Score", color=TEXT_COLOR)
    plt.xlabel("Sentiment", color=TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)

    for spine in ax.spines.values():
        spine.set_edgecolor(PRIMARY_COLOR)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return {
        "summary": summary,
        "sentiment": sentiment_scores,
        "recommendation": recommendation,
        "result_color": result_color,
        "plot_image": img_base64
    }