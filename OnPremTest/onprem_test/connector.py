"""Cloud mode of the test connector: only logs, the on-prem path is what is tested"""

import time

from sekoia_automation.connector import Connector


class OnPremTestAssetsConnector(Connector):
    def run(self) -> None:
        while self.running:
            self.log("On-prem test connector running in the cloud: nothing to collect")
            time.sleep(3600)
