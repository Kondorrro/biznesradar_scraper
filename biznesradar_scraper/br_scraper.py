import numpy as np
import pandas as pd
import re
from functools import cached_property
from datetime import datetime

from .helpers.launch_page import LaunchPage

BR_URL = "https://www.biznesradar.pl/"


class BrScraper:

    def __init__(self, ticker):
        self._ticker = ticker
        self.clear_data()

    def clear_data(self):
        self._financials_annual_data = pd.DataFrame()

    @property
    def ticker(self):
        return self._ticker

    @staticmethod
    def _parse_report_dates(page):
        raw = page.query_selector("#profile-finreports > table > tbody > tr:nth-child(1)")
        content = raw.text_content().replace("\t", "").replace("\n", "")
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

    def financials(self, quarterly=False):
        if quarterly:
            raise NotImplemented
            url += ",Q"

        url = f"{BR_URL}raporty-finansowe-rachunek-zyskow-i-strat/{self.ticker}"

        with LaunchPage(url) as page:
            popup_selector = "body > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button"
            page.wait_for_selector(popup_selector)
            page.query_selector(popup_selector).click()

            report_dates = self._parse_report_dates(page)
            revenue = self._parse_revenue(page)

        self._financials_annual_data["Revenue"] = pd.DataFrame(revenue)
        self._financials_annual_data["dates"] = report_dates
        self._financials_annual_data.set_index("dates", inplace=True)
        self._financials_annual_data.sort_index(ascending=False, inplace=True)

        # if quarterly:
        #     df['quarter'] = 'Q' + df.index.quarter.astype(str)

        return self._financials_annual_data
