import flet as ft
from scraper import get_stock_list, scrape_stock_data
from analyzer import analyze_text
from config import *


class StockAnalysisApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_ui()

    def setup_ui(self):
        """Настраиваем интерфейс"""
        self.page.title = "Stock Analysis"
        self.page.bgcolor = BG_COLOR
        self.page.padding = 20
        self.page.scroll = "auto"

        # Элементы UI
        self.header = ft.Text(
            "Stock Sentiment Analysis",
            size=24,
            color=PRIMARY_COLOR,
            weight="bold"
        )

        self.dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(stock) for stock in get_stock_list()],
            label="Select a stock",
            width=400,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR,
            bgcolor=SECONDARY_COLOR
        )

        self.analyze_btn = ft.ElevatedButton(
            text="Analyze",
            bgcolor=PRIMARY_COLOR,
            color=BG_COLOR,
            on_click=self.analyze_stock
        )

        self.results_column = ft.Column(expand=True, spacing=20)

        self.page.add(
            ft.Column([
                self.header,
                ft.Row([self.dropdown, self.analyze_btn], alignment="center"),
                self.results_column
            ], spacing=30)
        )

    def analyze_stock(self, e):
        if not self.dropdown.value:
            self.show_snackbar("Please select a stock first!")
            return

        self.results_column.controls.clear()
        self.show_loading()

        try:
            url, _ = scrape_stock_data(self.dropdown.value)

            url_link = ft.Text(
                f"Analyzing: {self.dropdown.value}",
                size=16,
                color=PRIMARY_COLOR,
                weight="bold"
            )

            url_link.on_click = lambda e: self.open_url(url)

            analysis_result = analyze_text(_)

            self.display_results(url_link, analysis_result)

        except Exception as ex:
            self.show_error(str(ex))

        self.page.update()

    def display_results(self, url_link, result):
        self.results_column.controls.clear()

        self.results_column.controls.extend([
            url_link,
            ft.Image(
                src_base64=result["plot_image"],
                width=600,
                height=300,
                fit=ft.ImageFit.CONTAIN
            ),
            self.create_sentiment_row("Positive", result["sentiment"]["pos"], "#33FF33"),
            self.create_sentiment_row("Negative", result["sentiment"]["neg"], "#FF3333"),
            self.create_sentiment_row("Neutral", result["sentiment"]["neu"], PRIMARY_COLOR),
            ft.Text(
                f"Recommendation: {result['recommendation']}",
                size=20,
                color=result["result_color"],
                weight="bold"
            ),
            ft.ElevatedButton(
                "View Detailed Analysis",
                bgcolor=PRIMARY_COLOR,
                color=BG_COLOR,
                on_click=lambda e: self.open_file("summary.txt")
            )
        ])

    def create_sentiment_row(self, label, value, color):
        return ft.Row([
            ft.Text(f"{label}: ", color=TEXT_COLOR, size=16),
            ft.Text(f"{value * 100:.1f}%", color=color, size=16, weight="bold")
        ])

    def show_loading(self):
        self.results_column.controls.append(
            ft.Row([ft.ProgressRing(color=PRIMARY_COLOR)], alignment="center")
        )
        self.page.update()

    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def show_error(self, message):
        self.results_column.controls.clear()
        self.results_column.controls.append(
            ft.Text(f"Error: {message}", color="#FF3333")
        )
        self.page.update()

    @staticmethod
    def open_url(url):
        import webbrowser
        webbrowser.open(url)

    @staticmethod
    def open_file(filename):
        import webbrowser
        import os
        if os.path.exists(filename):
            webbrowser.open(filename)