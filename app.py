import tkinter as tk
from tkinter import ttk, messagebox, Label, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import seaborn as sns
from PIL import ImageTk, Image
from parse import get_stock_list, scrape_stock_data, get_stock_chart
from NLTK import analyze_text


class StockAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap(default="favicon.ico")
        self.root.title("Analysis")
        self.root.geometry("1150x800")

        self.setup_ui()

    def setup_ui(self):
        self.stocklist = get_stock_list()

        self.btn_showlist = Label(self.root, text="Choose stock for analysis", font="Serif 12")
        self.btn_showlist.grid(column=0, row=0, padx=20)

        self.combobox = ttk.Combobox(self.root, values=self.stocklist)
        self.combobox.grid(column=0, row=1, pady=10, padx=20)

        self.btn_startanalysis = ttk.Button(
            self.root,
            text="Start analysis",
            command=self.check_combo,
            width=20
        )
        self.btn_startanalysis.grid(column=0, row=2, pady=8, padx=20)

    def check_combo(self):
        if self.combobox.get() == "":
            messagebox.showinfo("Nothing selected", "Please, select a stock")
            return

        stock_name = self.combobox.get()
        url = scrape_stock_data(stock_name)

        self.lbl_startanalysis = Label(
            self.root,
            text=url,
            font="Serif 12",
            fg="Blue",
            cursor="hand2"
        )
        self.lbl_startanalysis.bind("<Button-1>", lambda e: self.open_link(url))
        self.lbl_startanalysis.grid(column=1, row=0, padx=60)

        analysis_result = analyze_text()

        pos_ratio = str(analysis_result["sentiment_scores"].get("pos"))
        neg_ratio = str(analysis_result["sentiment_scores"].get("neg"))
        neu_ratio = str(analysis_result["sentiment_scores"].get("neu"))

        stock_mood_text = f"Positive ratio: {pos_ratio}\nNegative ratio: {neg_ratio}\nNeutral ratio: {neu_ratio}"
        self.stock_mood = Label(self.root, text=stock_mood_text, font="Serif 14")
        self.stock_mood.grid(column=1, row=2, padx=10)

        self.worthing = Label(
            self.root,
            text="Result is: " + analysis_result["worthing_text"],
            font="Serif 12"
        )
        self.worthing.grid(column=1, row=4, padx=10, pady=10)

        self.plot_sentiment_scores(analysis_result["sentiment_scores"])

        chart_path = get_stock_chart(stock_name)
        self.show_stock_chart(chart_path)

        self.check_analysis = ttk.Button(
            self.root,
            text="Check analysis",
            command=self.open_analysis,
            width=20
        )
        self.check_analysis.grid(column=0, row=4, padx=10)

    def open_link(self, url):
        webbrowser.open_new(url)

    def plot_sentiment_scores(self, sentiment_scores):
        plt.figure(figsize=(4.5, 2.5))
        sns.barplot(x=list(sentiment_scores.keys()), y=list(sentiment_scores.values()))
        plt.title("Sentiment scores")
        plt.ylabel("Score")
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=5, padx=40, pady=50)

    def show_stock_chart(self, image_path):
        frame = Frame(self.root, width=300, height=300, bg="white")
        frame.grid(column=1, row=5)

        image = Image.open(image_path)
        image = image.resize((250, 250), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        self.image_label = Label(frame, image=photo_image)
        self.image_label.image = photo_image  # Keep a reference
        self.image_label.grid(column=1, row=5)

    def open_analysis(self):
        webbrowser.open("summary.txt")


if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalysisApp(root)
    root.mainloop()