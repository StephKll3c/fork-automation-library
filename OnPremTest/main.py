from sekoia_automation.module import Module

from onprem_test.collect import CollectAssets
from onprem_test.connector import OnPremTestAssetsConnector

if __name__ == "__main__":
    module = Module()
    module.register(OnPremTestAssetsConnector, "onprem_test_assets_connector")
    module.register(CollectAssets, "onprem_test_collect_assets")
    module.run()
