from typing import Final
import random
from dataclasses import dataclass

# === Simulation Core Parameters ===
NODE_COUNT: Final[int] = 5
NODE_IDS: Final[list[str]] = [f"node_{i}" for i in range(NODE_COUNT)]
RANDOM_SEED: Final[int] = 42  # For reproducible simulations

# === Timing Configuration ===
HEARTBEAT_INTERVAL: Final[float] = 0.5  # seconds
ELECTION_TIMEOUT_RANGE: Final[tuple[float, float]] = (1.0, 2.0)  # min/max seconds

# === Failure Injection Settings ===
MESSAGE_LOSS_RATE: Final[float] = 0.05  # 5% packet loss
NODE_FAILURE_RATE: Final[float] = 0.01  # 1% chance of node failure per heartbeat
MESSAGE_DELAY_RANGE: Final[tuple[float, float]] = (0.01, 0.1)  # min/max seconds

# === Debug/Logging Configuration ===
VERBOSE_LOGGING: Final[bool] = True
DEBUG_MODE: Final[bool] = False

# Initialize random generator with fixed seed for reproducibility
random.seed(RANDOM_SEED)

@dataclass
class Config:
    """Configuration class for the simulation."""
    node_count: int = NODE_COUNT
    message_drop_rate: float = MESSAGE_LOSS_RATE
    node_failure_rate: float = NODE_FAILURE_RATE
    min_latency: float = MESSAGE_DELAY_RANGE[0]
    max_latency: float = MESSAGE_DELAY_RANGE[1]
    heartbeat_interval: float = HEARTBEAT_INTERVAL
    election_timeout_min: float = ELECTION_TIMEOUT_RANGE[0]
    election_timeout_max: float = ELECTION_TIMEOUT_RANGE[1]
    verbose_logging: bool = VERBOSE_LOGGING
    debug_mode: bool = DEBUG_MODE
    
    # Add alias for compatibility
    @property
    def drop_rate(self) -> float:
        return self.message_drop_rate

def validate_config() -> None:
    """Validate configuration parameters."""
    if not (0 <= MESSAGE_LOSS_RATE <= 1):
        raise ValueError("MESSAGE_LOSS_RATE must be between 0 and 1")
    if not (0 <= NODE_FAILURE_RATE <= 1):
        raise ValueError("NODE_FAILURE_RATE must be between 0 and 1")
    if not (0 < HEARTBEAT_INTERVAL < 10):
        raise ValueError("HEARTBEAT_INTERVAL must be between 0 and 10 seconds")
    if not (ELECTION_TIMEOUT_RANGE[0] < ELECTION_TIMEOUT_RANGE[1]):
        raise ValueError("ELECTION_TIMEOUT_RANGE must be a valid range")