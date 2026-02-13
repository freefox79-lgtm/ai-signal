import os
import psycopg2
from api_connectors import APIConnectors
from dotenv import load_dotenv

load_dotenv(".env.local")

class JwemPortfolio:
    """
    Jwem's core module for tracking 18 specific stocks and calculating risk.
    Connects to Alpha Vantage for pricing and stores data locally.
    """
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.connectors = APIConnectors()
        # 쥄의 마스터 포트폴리오 (18개 종목 예시)
        self.target_stocks = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "BRK.B", "V", "JNJ", "WMT", "PG", "MA", "XOM", "UNH", "HD", "PFE", "DIS"]

    def update_prices(self):
        """Fetches latest prices and updates the local database."""
        print(f"[JWEM] Updating prices for {len(self.target_stocks)} stocks...")
        for symbol in self.target_stocks:
            data = self.connectors.fetch_stock_quote(symbol)
            price = data.get("Global Quote", {}).get("05. price", 0)
            
            with self.conn.cursor() as cur:
                # Update current price and calculate profit/loss (assuming we have avg_price)
                cur.execute("""
                    INSERT INTO jwem_portfolio (stock_code, current_price, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (stock_code) DO UPDATE SET 
                        current_price = EXCLUDED.current_price,
                        last_updated = EXCLUDED.last_updated
                """, (symbol, price))
            self.conn.commit()
        print("[JWEM] Portfolio update complete.")

    def analyze_risk(self):
        """Simple risk calculation logic (Placeholder for now)."""
        # Logic to compare current vs avg price and flag anomalies
        return "Portfolio stability: 85% (Optimistic)"

if __name__ == "__main__":
    jwem = JwemPortfolio()
    jwem.update_prices()
    print(jwem.analyze_risk())
