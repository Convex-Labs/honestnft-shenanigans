import json
import time
import glob
import requests

from sales_data.dappradar import DappRadar


class SalesData:
    def __init__(self):
        self.opensea_url = "https://api.opensea.io/api/v1/collection/%s"
        self.collections_file_path = "collections/eth_contracts.json"
        self.collections = self._import_collections()
        self.dapp = DappRadar()

    def _import_collections(self):
        with open(self.collections_file_path, "r") as json_file:
            collections = json.load(json_file)
        return collections

    def _get_existing_contracts(self):
        files = glob.glob("csv/*.csv")
        contracts = [file.split("\\")[-1].split(".")[0] for file in files]
        return contracts

    def _get_collection_slugs(self):
        slugs = list()
        for collection in self.collections["data"]["rankings"]["edges"]:
            slugs.append(collection["node"]["slug"])
        return slugs

    def _get_contract_addresses(self):
        slugs = self._get_collection_slugs()
        contract_addresses = list()
        for slug in slugs:
            try:
                url = self.opensea_url % slug
                print(url)
                response = requests.get(url).json()
                contract_addresses.append(
                    response["collection"]["primary_asset_contracts"][0]["address"]
                )
            except:
                continue
        return contract_addresses

    def _get_sales_data(self, contract_address):
        sales_data = self.dapp.collate_historical_data(
            resolution="week",
            limit=15,
            page=1,
            currency="USD",
            sort="soldAt",
            order="desc",
            collections=contract_address,
        )
        return sales_data

    def _get_token_sales_data(self, contract_address, token_id):
        token_sales_data = self.dapp.collate_historical_token_sales_data(
            contract_address, token_id, page=1, results_per_page=25, fiat="USD"
        )
        return token_sales_data

    @staticmethod
    def _write_to_csv(sales_data, contract_address):
        sales_data.to_csv(f"csv/{contract_address}.csv", index=False)

    @staticmethod
    def _write_token_to_csv(token_sales_data, contract_address, token_id):
        token_sales_data.to_csv(f"csv/{contract_address}_{token_id}.csv", index=False)

    def collate_sales_data(self):
        contract_addresses = self._get_contract_addresses()
        existing_contracts = self._get_existing_contracts()
        for contract in contract_addresses:
            if contract not in existing_contracts:
                print(contract)
                sales_data = self._get_sales_data(contract)
                self._write_to_csv(sales_data, contract)
                time.sleep(1)

    def collate_token_sales_data(self):
        contract_addresses = self._get_contract_addresses()
        for contract in contract_addresses:
            for token_id in ["1", "69", "420"]:
                token_sales_data = self._get_token_sales_data(contract, token_id)
                if token_sales_data is not None:
                    self._write_token_to_csv(token_sales_data, contract, token_id)
                time.sleep(1)


if __name__ == "__main__":
    collate = SalesData()
    collate.collate_token_sales_data()
