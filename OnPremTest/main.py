from sekoia_automation.module import Module

from onprem_test.collect import CollectAssets, CollectAssetsFailing
from onprem_test.connector import OnPremTestAssetsConnector

if __name__ == "__main__":
    module = Module()
    module.register(OnPremTestAssetsConnector, "onprem_test_assets_connector")
    module.register(OnPremTestAssetsConnector, "onprem_test_failing_assets_connector")
    module.register(CollectAssets, "onprem_test_collect_assets")
    module.register(CollectAssetsFailing, "onprem_test_collect_assets_failing")
    module.run()
