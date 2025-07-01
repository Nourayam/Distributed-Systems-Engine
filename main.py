
#!/usr/bin/env python3
# Entry point for the DSS Raft simulator.

# This module provides a command-line interface for running Raft consensus simulations
# with support for chaos engineering experiments and service discovery integration.

import argparse
import logging
import sys
from typing import List

from nodes.raft_node import RaftNode
from simulation.simulation import Simulation
from simulation.event_logger import EventLogger
from simulation.message_queue import MessageQueue
from simulation.failure_injector import FailureInjector
from simulation.simulation_events import Event, EventType
from config import Config


def main():
    """Main entry point for the Raft simulator."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Raft consensus simulator')
    parser.add_argument('--max_time', type=float, default=60.0,
                       help='Maximum simulation time in seconds')
    parser.add_argument('--nodes', type=int, default=5,
                       help='Number of Raft nodes in the cluster')
    parser.add_argument('--chaos', action='store_true',
                       help='Enable chaos testing')
    parser.add_argument('--chaos_scenario', type=str,
                       choices=['network_partition', 'leader_failure',
                                'log_corruption', 'clock_skew', 'disk_failure'],
                       default='network_partition',
                       help='Chaos testing scenario to execute')
    parser.add_argument('--chaos_duration', type=int, default=30,
                       help='Duration of chaos event in seconds')
    parser.add_argument('--service_discovery', action='store_true',
                       help='Enable Consul service discovery integration')
    parser.add_argument('--config_file', type=str, default=None,
                       help='Optional path to config file')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)

    # Load configuration
    try:
        config = Config()
        if args.config_file:
            config.load_from_file(args.config_file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Initialize core simulation components
    sim = Simulation()
    elog = EventLogger()
    mq = MessageQueue(config, sim)
    fi = FailureInjector(sim)

    # Create Raft nodes
    nodes: List[RaftNode] = []
    for node_id in range(args.nodes):
        node = RaftNode(
            node_id=node_id,
            config=config,
            simulation=sim,
            message_queue=mq,
            event_logger=elog
        )
        nodes.append(node)
        # Schedule initial timeout
        timeout = config.get_random_election_timeout()
        evt = Event(
            timestamp=timeout,
            event_type=EventType.TIMEOUT,
            data={'node_id': node_id}
        )
        sim.schedule_event(evt)

    # Set up chaos engineering if enabled
    if args.chaos:
        from simulation.chaos import ChaosMonkey
        chaos = ChaosMonkey(nodes[0])  # Target first node by default
        chaos.run_test(scenario=args.chaos_scenario, duration=args.chaos_duration)

    # Set up service discovery if enabled
    if args.service_discovery:
        from integration.consul import ServiceDiscoveryIntegration
        for node in nodes:
            sd = ServiceDiscoveryIntegration(node)
            sd.register_node()
            sd.start_cluster_watcher()

    # Run the simulation
    logger.info(f"Starting simulation with {args.nodes} nodes for {args.max_time} seconds")
    try:
        sim.run(until=args.max_time)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        sys.exit(1)

    # Print results
    print("\n=== Simulation Results ===")
    print("Node ID | Term | Role | Commit Index")
    for node in nodes:
        print(f"{node.node_id:7} | {node.current_term:4} | {node.role:4} | {node.commit_index:12}")

    print("\n=== First 20 Events ===")
    for event in elog.get_events()[:20]:
        print(event)


if __name__ == "__main__":
    main()
