import airbrake as _a
import logging as _l

_l.basicConfig(level=_l.INFO)
logger = _l.getLogger(__name__)
_airbrake_logger = _a.getLogger(api_key="1001b69b71a13ef204b4a8ac1e38d9ad", project_id=157356)
logger.exception = _airbrake_logger.exception

# logger.exception("Bad math.")

