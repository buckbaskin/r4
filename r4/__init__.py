import r4.client
import r4.intermediate

import airbrake
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_airbrake_logger = airbrake.getLogger(api_key="1001b69b71a13ef204b4a8ac1e38d9ad", project_id=157356)
logger.exception = airbrake_logger.exception

# logger.exception("Bad math.")
