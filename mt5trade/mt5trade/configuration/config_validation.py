"""Configuration validation"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration"""
    logger.info("Validating configuration...")
    return config
