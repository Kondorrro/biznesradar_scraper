import re
from datetime import datetime

import pandas as pd

from .helpers.launch_page import LaunchPage

BR_URL = "https://www.biznesradar.pl/"


class BrScraper:

    QUARTERS_MAP = {
        "Q1": "03-31",
        "Q2": "06-30",
        "Q3": "09-30",
        "Q4": "12-31"
    }

    def __init__(self, ticker):
        self._ticker = ticker
        self.clear_data()

    def clear_data(self):
        self._financials_annual_data = pd.DataFrame()
        self._financials_quarterly_data = pd.DataFrame()

    @property
    def ticker(self):
        return self._ticker

    def _parse_report_dates(self, page, quarterly=False):
        raw = page.query_selector("#profile-finreports > table > tbody > tr:nth-child(1)")
        content = raw.text_content().replace("\t", "").replace("\n", "")

        if quarterly:
            dates = []
            raw_dates = re.findall(r"(\d{4}/\w{2})", content)
            for raw_date in raw_dates:
                year, qr = raw_date.split("/")
                dates.append(f"{year}-{self.QUARTERS_MAP[qr]}")
            dates = pd.to_datetime(dates)
        else:
            dates = pd.to_datetime(re.findall(r"(\d{4})", content))
            today = pd.Timestamp(datetime.now().date())
            dates = dates.append(pd.DatetimeIndex([today]))

        return dates

    @staticmethod
    def _parse_revenue(page):
        raw = page.query_selector("#profile-finreports > table > tbody > tr:nth-child(3)")
        columns = raw.query_selector_all("td")
        data = []
        for c in columns:
            result = re.search(r"(\d{1,})", c.text_content().replace(" ", ""))
            if result:
                data.append(int(result.group(0)))

        return data

    def financials_annual(self):
        if not self._financials_annual_data.empty:
            return self._financials_annual_data
        self._financials_annual_data = self._financials()
        return self._financials_annual_data

    def financials_quarterly(self):
        if not self._financials_quarterly_data.empty:
            return self._financials_quarterly_data
        self._financials_quarterly_data = self._financials(quarterly=True)
        return self._financials_quarterly_data

    def _financials(self, quarterly=False):
        url = f"{BR_URL}raporty-finansowe-rachunek-zyskow-i-strat/{self.ticker}"

        if quarterly:
            url += ",Q"

        with LaunchPage(url) as page:
            popup_selector = "body > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button"
            page.wait_for_selector(popup_selector)
            page.query_selector(popup_selector).click()

            report_dates = self._parse_report_dates(page, quarterly=quarterly)
            revenue = self._parse_revenue(page)

        df = pd.DataFrame({"Revenue": revenue})
        df["dates"] = report_dates
        df.set_index("dates", inplace=True)
        df.sort_index(ascending=False, inplace=True)

        if quarterly:
            df['quarter'] = 'Q' + df.index.quarter.astype(str)

        return df
