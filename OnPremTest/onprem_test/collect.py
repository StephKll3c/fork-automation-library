"""Collect action of the on-prem test connector: a checkpoint, a page count, assets and a failure on demand"""

import json
import time
from datetime import UTC, datetime

import requests
from sekoia_automation.action import Action
from sekoia_automation.asset_connector.models.connector import AssetList
from sekoia_automation.asset_connector.models.ocsf.base import Metadata, Product
from sekoia_automation.asset_connector.models.ocsf.device import (
    Device,
    DeviceOCSFModel,
    DeviceTypeId,
    DeviceTypeStr,
)

CHECKPOINT = "checkpoint.json"
DEVICES_PER_PAGE = 2


class CollectAssets(Action):
    def run(self, arguments: dict) -> dict:
        if arguments.get("fail"):
            raise RuntimeError("Collect failed on purpose (fail=true)")

        # The connector storage: the checkpoint must survive from one run to the next
        checkpoint = self.data_path / CHECKPOINT
        page = json.loads(checkpoint.read_text())["page"] + 1 if checkpoint.exists() else 1
        pages = int(arguments.get("pages") or 3)
        has_more = page < pages

        pushed = self._push_assets(arguments)
        # A finished sync starts over on the next tick
        checkpoint.write_text(json.dumps({"page": page if has_more else 0}))

        self._push_log(arguments, f"Collected page {page}/{pages}: {pushed} assets, has_more={has_more}")
        return {"page": page, "assets": pushed, "has_more": has_more}

    def _push_assets(self, arguments: dict) -> int:
        """Push the two test devices, as a cloud asset connector does, with the configuration's API key"""
        api_key = arguments.get("sekoia_api_key")
        base_url = arguments.get("sekoia_base_url")
        if not api_key or not base_url:
            self.log("No API key or base URL: assets not pushed", level="warning")
            return 0
        now = time.time()
        items = [
            DeviceOCSFModel(
                activity_id=2,
                activity_name="Collect",
                category_name="Discovery",
                category_uid=5,
                class_name="Device Inventory Info",
                class_uid=5001,
                device=Device(
                    type_id=DeviceTypeId.DESKTOP,
                    type=DeviceTypeStr.DESKTOP,
                    # The same two devices on every page and every sync: updated, never multiplied
                    uid=f"onprem-test-{index}",
                    hostname=f"onprem-test-{index}",
                ),
                time=now,
                metadata=Metadata(product=Product(name="On-prem test", vendor_name="Sekoia.io"), version="1.6.0"),
                severity="Informational",
                severity_id=1,
                type_name="Device Inventory Info: Collect",
                type_uid=500102,
            )
            for index in range(1, DEVICES_PER_PAGE + 1)
        ]
        response = requests.post(
            f"{base_url.rstrip('/')}/api/v2/asset-management/asset-connector/{arguments['asset_connector_uuid']}",
            json=AssetList(version=1, items=items).model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        self.log(f"Assets pushed: HTTP {response.status_code}")
        response.raise_for_status()
        return len(items)

    def _push_log(self, arguments: dict, message: str) -> None:
        """Push one log with the configuration token, as the connector would"""
        token = arguments.get("connector_configuration_token")
        api_url = arguments.get("api_url")
        if not token or not api_url:
            self.log("No token or API URL: connector log not pushed", level="warning")
            return
        response = requests.post(
            f"{api_url.rstrip('/')}/connector-configurations/{arguments['asset_connector_uuid']}/logs",
            json={"logs": [{"level": "info", "message": message, "date": datetime.now(UTC).isoformat()}]},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        self.log(f"Connector log pushed: HTTP {response.status_code}")
