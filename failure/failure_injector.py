# Failure injector for testing distributed system robustness.

# This module introduces various types of failures into the simulation environment
# to test system fault tolerance and recovery mechanisms.

from typing import Optional, Dict, Any
import random
import logging
from datetime import timedelta
from dataclasses import dataclass

# Configure module-level logger
logger = logging.getLogger(__name__)

@dataclass
class FailureConfig:
    #Configuration for failure injection parameters
    message_drop_prob: float = 0.01
    message_duplicate_prob: float = 0.005
    node_crash_prob: float = 0.001
    network_partition_prob: float = 0.002
    max_delay_ms: int = 1000

class FailureInjector:
    #Main class for injecting failures into the distributed system simulation
    
    # Responsibilities:
    # - Randomly drop or duplicate messages in-transit
    # - Simulate node crashes and reboots
    # - Model network partitions and message delays
    # - Log all injected failures

    
    def __init__(self, config: Optional[FailureConfig] = None):
        self.config = config if config else FailureConfig()
        self.active_failures: Dict[str, Any] = {}
        logger.info("Failure injector initialized with config: %s", self.config)

    def inject_message_failure(self, message: Any) -> Optional[Any]:
        
        #Potentially alter or drop a message based on configured probabilities.
        
        # Returns:
        #     The original message, a duplicate, or None if message should be dropped.
        rand = random.random()
        
        if rand < self.config.message_drop_prob:
            logger.debug("Dropping message: %s", message)
            return None
            
        if rand < self.config.message_drop_prob + self.config.message_duplicate_prob:
            logger.debug("Duplicating message: %s", message)
            return [message, message]
            
        return message

    def should_crash_node(self, node_id: str) -> bool:
        #Determine if a node should crash based on configured probability
        if random.random() < self.config.node_crash_prob:
            logger.info("Injecting node crash for node: %s", node_id)
            self.active_failures[f"crash_{node_id}"] = True
            return True
        return False

    def should_partition_network(self) -> bool:
        #Determine if a network partition should occur
        if random.random() < self.config.network_partition_prob:
            logger.info("Injecting network partition")
            return True
        return False

    def get_message_delay(self) -> timedelta:
        #Get a random message delay duration
        delay_ms = random.randint(0, self.config.max_delay_ms)
        return timedelta(milliseconds=delay_ms)

# TODO: Add integration with simulation clock/event queue
# TODO: Implement recovery timers for node crashes
# TODO: Add failure traceability system for timeline reconstruction
