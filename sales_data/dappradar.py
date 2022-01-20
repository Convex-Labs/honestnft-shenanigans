import pandas as pd

from requests import Request, Session, Response
from typing import Optional, Dict, Any


class DappRadar:
    """
    Historical sales API from DappRadar.

    Resolution -> hour, day, week, month, all
    Limit -> results per call
    Page -> Pagination
    Currency -> USD
    Sort -> Sort by field
    Order -> asc, desc
    Collections -> contract address
    """

    _ENDPOINT = "https://nft-sales-service.dappradar.com/v2/"

    def __init__(self):
        self._session = Session()

    def _request(self, method: str, path: str, **kwargs) -> Any:
        print(f"Processing: {self._ENDPOINT + path}")
        request = Request(method, self._ENDPOINT + path, **kwargs)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    @staticmethod
    def _process_response(response: Response) -> Any:
        try:
            data = response.json()
            return data
        except ValueError:
            response.raise_for_status()
            raise

    def _get_historical_sales_data(
            self,
            resolution: str,
            limit: int,
            page: int,
            currency: str,
            sort: str,
            order: str,
            collections: str
    ):
        response = self._get(
            f"/sale/{resolution}?limit={limit}&page={page}&currency={currency}&sort={sort}&order={order}&collections={collections}"
        )
        return response

    def collate_historical_data(
            self,
            resolution: str,
            limit: int,
            page: int,
            currency: str,
            sort: str,
            order: str,
            collections: str
    ):
        sales_data = list()

        response = self._get_historical_sales_data(
            resolution, limit, page, currency, sort, order, collections
        )

        page = response["page"]
        page_count = response["pageCount"]

        while page < page_count:
            response = self._get_historical_sales_data(
                resolution, limit, page, currency, sort, order, collections
            )
            sales_data.extend(response["results"])

            page += 1

        sales_data = pd.DataFrame(sales_data)

        return sales_data


if __name__ == "__main__":
    """
    Example for Bored Ape Yacht Club
    """
    dapp = DappRadar()
    sales_data = dapp.collate_historical_data(
        resolution="week",
        limit=15,
        page=1,
        currency="USD",
        sort="soldAt",
        order="desc",
        collections="0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
    )
    print(sales_data.head(10))
