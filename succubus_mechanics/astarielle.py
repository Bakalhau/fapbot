import datetime

# Variáveis configuráveis
DAILY_REDUCTION_HOURS = 2
PRICE_INFLATION_PERCENTAGE = 20

class Astarielle:
    @staticmethod
    def apply_daily_reduction(last_daily: datetime.datetime) -> datetime.datetime:
        return last_daily - datetime.timedelta(hours=DAILY_REDUCTION_HOURS)

    @staticmethod
    def apply_price_inflation(original_price: int) -> int:
        inflation_factor = 1 + (PRICE_INFLATION_PERCENTAGE / 100)
        return int(original_price * inflation_factor)
