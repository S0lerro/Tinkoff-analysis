from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import openpyxl


def analyze_text():
    wb = openpyxl.load_workbook("scrapping.xlsx")
    sheet = wb["Tbank"]
    full_data = ""
    for row in range(2, 10):
        cell_name = "{} {}".format("C", row)
        formated_cell_name = cell_name.replace(" ", "")
        text = sheet[formated_cell_name].value
        full_data += text + "\n"

    words = word_tokenize(full_data)
    stop_words = set(stopwords.words("russian"))
    freqTable = dict()

    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(full_data)
    sentence_value = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq

    sumValues = 0
    for sentence in sentence_value:
        sumValues += sentence_value[sentence]

    summary = ""
    average = int(sumValues / len(sentence_value))

    for sentence in sentences:
        if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)):
            summary += " " + sentence

    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(summary)

    if sentiment_scores.get("neg") > sentiment_scores.get("pos"):
        worthing_text = "NOT WORTH"
    elif sentiment_scores.get("neg") < sentiment_scores.get("pos"):
        worthing_text = "WORTH"
    elif sentiment_scores.get("neg") or sentiment_scores.get("pos") < sentiment_scores.get("neu"):
        worthing_text = "NEUTRAL"

    return {
        "sentiment_scores": sentiment_scores,
        "worthing_text": worthing_text,
        "summary": summary
    }