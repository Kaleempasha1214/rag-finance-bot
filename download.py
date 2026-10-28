from sec_edgar_downloader import Downloader

dl = Downloader("Kaleem Pasha", "kaleemsknk1214@email.com", "data")
for t in ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]:
    dl.get("10-K", t, limit=3, download_details=True)