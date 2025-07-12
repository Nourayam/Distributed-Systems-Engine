import random
import logging
from datetime import timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.simulation import Simulation

logger = logging.getLogger(__name__)


@dataclass
class FailureConfig:
    """Configuration for failure injection parameters"""
    message_drop_prob: float = 0.01
    message_duplicate_prob: float = 0.005
    node_crash_prob: float = 0.001
    network_partition_prob: float = 0.002
    max_delay_ms: int = 1000


class FailureInjector:
    """Main class for injecting failures into the distributed system simulation"""
    
    def __init__(self, simulation: 'Simulation', config: Optional[FailureConfig] = None):
        self.simulation = simulation
        self.config = config if config else FailureConfig()
        self.active_failures: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.FailureInjector")
        
        self.logger.info(f"Failure injector initialised with config: {self.config}")

    def inject_message_failure(self, message: Any) -> Optional[Any]:
        """Potentially alter or drop a message based on configured probabilities"""
        rand = random.random()
        
        if rand < self.config.message_drop_prob:
            self.logger.debug(f"Dropping message: {message}")
            return None
            
        if rand < self.config.message_drop_prob + self.config.message_duplicate_prob:
            self.logger.debug(f"Duplicating message: {message}")
            return [message, message]
            
        return message

    def should_crash_node(self, node_id: str) -> bool:
        """Determine if a node should crash based on configured probability"""
        if random.random() < self.config.node_crash_prob:
            self.logger.info(f"Injecting node crash for node: {node_id}")
            self.active_failures[f"crash_{node_id}"] = True
            return True
        return False

    def should_partition_network(self) -> bool:
        """Determine if a network partition should occur"""
        if random.random() < self.config.network_partition_prob:
            self.logger.info("Injecting network partition")
            return True
        return False

    def get_message_delay(self) -> timedelta:
        """Get a random message delay duration"""
        delay_ms = random.randint(0, self.config.max_delay_ms)
        return timedelta(milliseconds=delay_ms)

    def inject_node_crash(self, node_id: str, recovery_time: Optional[float] = None) -> None:
        """Inject a node crash with optional recovery"""
        from simulation.simulation_events import Event, EventType
        
        # Schedule crash event
        crash_event = Event(
            event_type=EventType.NODE_CRASH,
            timestamp=self.simulation.current_time,
            data={'node_id': node_id}
        )
        self.simulation.schedule_event(crash_event)
        
        # Schedule recovery if specified
        if recovery_time:
            recovery_event = Event(
                event_type=EventType.NODE_RECOVER,
                timestamp=self.simulation.current_time + recovery_time,
                data={'node_id': node_id}
            )
            self.simulation.schedule_event(recovery_event)
            
        self.logger.info(f"Scheduled crash for node {node_id}" + 
                        (f" with recovery in {recovery_time}s" if recovery_time else ""))

    def inject_network_partition(self, partition_groups: list, duration: float) -> None:
        """Inject a network partition separating nodes into groups"""
        self.logger.info(f"Injecting network partition: {partition_groups} for {duration}s")
        
        # TODO: Implement network partition logic
        # This would modify message routing between groups
        pass

    def get_active_failures(self) -> Dict[str, Any]:
        """Get information about currently active failures"""
        return self.active_failures.copy()