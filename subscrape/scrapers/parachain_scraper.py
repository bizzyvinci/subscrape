__author__ = 'Tommi Enenkel @alice_und_bob'

import logging
from subscrape.apis.subscan_base import SubscanBase

# A generic scraper for parachains
class ParachainScraper:
    """Scrape a substrate-based (non-EVM) chain for transactions/accounts of interest."""

    def __init__(self, api):
        self.logger = logging.getLogger("ParachainScraper")
        self.api: SubscanBase = api

    async def scrape(self, operations, chain_config) -> int:
        """Performs all the operations it was given by determining the operation and then calling the corresponding 
        method.
        
        :param operations: A dict of operations and it's subdicts
        :type operations: dict
        :param chain_config: the `ScrapeConfig` to bubble down configuration properties
        :type chain_config: ScrapeConfig
        :return: the number of items scraped
        """
        items_scraped = 0

        for operation in operations:
            if operation.startswith("_"):
                continue

            if operation == "extrinsics":
                modules = operations[operation]
                items_scraped += await self.scrape_module_calls(modules, chain_config, self.api.fetch_extrinsics_index)
            elif operation == "extrinsics-list":
                extrinsics_list = operations[operation]
                items_scraped += await self.api.fetch_extrinsics(extrinsics_list)
            elif operation == "events":
                modules = operations[operation]
                items_scraped += await self.scrape_module_calls(modules, chain_config, self.api.fetch_events_index)
            elif operation == "events-list":
                events_list = operations[operation]
                items_scraped += await self.api.fetch_events(events_list)
            elif operation == "transfers":
                accounts = operations[operation]
                items_scraped += await self.scrape_transfers(accounts, chain_config)
            else:
                self.logger.error(f"config contained an operation that does not exist: {operation}")            
                exit
        
        return items_scraped

    async def scrape_module_calls(self, modules, chain_config, fetch_function) -> int:
        """
        Scrapes all module calls that belong to the list of accounts.

        :param modules: dict of extrinsic modules to look for, like `system`, `utility`, etc
        :type modules: dict
        :param chain_config: the `ScrapeConfig`
        :type chain_config: ScrapeConfig
        :param fetch_function: the method to call to scrape extrinsics vs events etc
        :type fetch_function: function
        :return: the number of items scraped
        """
        items_scraped = 0
        extrinsic_config = chain_config.create_inner_config(modules)

        for module in modules:
            # ignore metadata
            if module.startswith("_"):
                continue

            calls = modules[module]
            module_config = extrinsic_config.create_inner_config(calls)
            
            for call in calls:
                # ignore metadata
                if call.startswith("_"):
                    continue

                # deduce config
                if type(calls) is dict:
                    call_config = module_config.create_inner_config(calls[call])
                else:
                    call_config = module_config

                # config wants us to skip this call?
                if call_config.skip:
                    self.logger.info(f"Config asks to skip {module} {call}")
                    continue

                # go
                items_scraped += await fetch_function(module, call, call_config)
        return items_scraped

    def scrape_transfers(self, accounts, chain_config) -> int:
        """
        Scrapes all transfers that belong to the list of accounts.
        
        :param accounts: A dict of accounts on their names
        :type accounts: dict
        :param chain_config: the `ScrapeConfig`
        :type chain_config: ScrapeConfig
        :return: the number of items scraped
        """
        items_scraped = 0
        accounts_config = chain_config.create_inner_config(accounts)

        for account in accounts:
            # ignore metadata
            if account.startswith("_"):
                continue
            
            # deduce config
            if type(account) is dict:
                account_config = accounts_config.create_inner_config(accounts[account])
            else:
                account_config = accounts_config

            # config wants us to skip this call?
            if account_config.skip:
                self.logger.info(f"Config asks to skip account {account}")
                continue

            items_scraped += self.api.fetch_transfers(account, account_config)



"""

    def fetch_addresses(self):
        assert(len(self.addresses) == 0)

        file_path = self.db_path + "addresses.json"
        if os.path.exists(file_path):
            self.logger.warn(f"{file_path} already exists. Skipping.")
            return

        self.logger.info("Fetching accounts from " + self.endpoint)

        method = "/api/v2/scan/accounts"
        url = self.endpoint + method

        self.api.iterate_pages(url, self.process_account, list_key="list")

        file_path = self.db_path + "addresses.json"
        payload = json.dumps(self.addresses)
        file = io.open(file_path, "w")
        file.write(payload)
        file.close()


        def process_account(self, account):
        account_display = account["account_display"]
        address = account_display["address"]
        self.addresses.append(address)
        return True


"""