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

    _SALES_ENDPOINT = "https://nft-sales-service.dappradar.com/v2/"
    _TOKEN_SALES_ENDPOINT = (
        "https://nft-balance-api.dappradar.com/transactions/ethereum/"
    )

    def __init__(self):
        self._session = Session()

    def _request(self, endpoint: str, method: str, path: str, **kwargs) -> Any:
        print(f"Processing: {endpoint + path}")
        request = Request(method, endpoint + path, **kwargs)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _get(
        self, endpoint: str, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        return self._request(endpoint, "GET", path, params=params)

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
        collections: str,
    ):
        payload = {
            "limit": limit,
            "page": page,
            "currency": currency,
            "sort": sort,
            "order": order,
            "collections": collections,
        }
        response = self._get(
            self._SALES_ENDPOINT, f"/sale/{resolution}", params=payload
        )
        return response

    def _get_historical_token_sales_data(
        self,
        contract_address: str,
        token_id: str,
        page: int,
        results_per_page: int,
        fiat: str,
    ):
        payload = {
            "page": page,
            "resultsPerPage": results_per_page,
            "fiat": fiat,
        }
        response = self._get(
            self._TOKEN_SALES_ENDPOINT, f"{contract_address}/{token_id}",
params=payload
        )
        print(response)
        return response

    def collate_historical_data(
        self,
        resolution: str,
        limit: int,
        page: int,
        currency: str,
        sort: str,
        order: str,
        collections: str,
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

    def collate_historical_token_sales_data(
        self,
        contract_address: str,
        token_id: str,
        page: int,
        results_per_page: int,
        fiat: str,
    ):
        token_sales_data = list()

        response = self._get_historical_token_sales_data(
            contract_address, token_id, page, results_per_page, fiat
        )

        page = response["page"]
        page_count = response["pageCount"]

        token_sales_data.extend(response["data"])

        page += 1

        while page < page_count:
            response = self._get_historical_token_sales_data(
                contract_address, token_id, page, results_per_page, fiat
            )
            token_sales_data.extend(response["data"])

            page += 1

        token_sales_data = pd.DataFrame(token_sales_data)

        return token_sales_data


if __name__ == "__main__":
    """
    Example for Bored Ape Yacht Club
    """
    dapp = DappRadar()
    sales_data = dapp.collate_historical_token_sales_data(
        contract_address="0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        token_id="69",
        page=1,
        results_per_page=25,
        fiat="USD",
    )
    print(sales_data.head(10))
