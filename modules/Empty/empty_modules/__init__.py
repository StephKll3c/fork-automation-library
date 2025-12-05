import logging

from sekoia_automation.module import Module

from empty_modules.models import EmptyModuleConfiguration


logger = logging.getLogger(__name__)


class EmptyModule(Module):
    configuration: EmptyModuleConfiguration

    def run(self) -> None:
        # Log a simple greeting before deferring to the default behaviour.
        logger.info("hello")
        super().run()
