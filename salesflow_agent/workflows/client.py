"""Zeebe workflow client for lead qualification."""

import logging
import os

from pyzeebe import ZeebeClient, create_insecure_channel

logger = logging.getLogger(__name__)


class WorkflowClient:
    """Client for interacting with Zeebe workflow engine."""

    def __init__(self):
        address = os.environ.get("ZEEBE_ADDRESS", "localhost:26500")
        try:
            channel = create_insecure_channel(hostname=address.split(":")[0], port=int(address.split(":")[1]))
            self.client = ZeebeClient(channel)
            self._available = True
            logger.info(f"Zeebe client connected to {address}")
        except Exception as e:
            self._available = False
            logger.warning(f"Zeebe not available at {address}: {e}")

    @property
    def available(self) -> bool:
        return self._available

    async def start_lead_qualification(self, lead_data: dict) -> int | None:
        """Start a lead qualification workflow instance."""
        if not self._available:
            logger.warning("Zeebe not available — cannot start workflow")
            return None

        try:
            result = await self.client.run_process(
                bpmn_process_id="lead-qualification",
                variables=lead_data,
            )
            logger.info(f"Workflow started: instance_key={result}")
            return result
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}")
            return None
