import flet as ft
from gui import StockAnalysisApp

def main(page: ft.Page):
    app = StockAnalysisApp(page)

if __name__ == "__main__":
    ft.app(target=main)