#!/usr/bin/env python3
import argparse
import logging
import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from simulation.simulation import EventDrivenSimulator
from nodes.raft_node import RaftNode

def main():
   #Main entry point for the Raft simulator 
    parser = argparse.ArgumentParser(description='Raft consensus simulator')
    parser.add_argument('--max_time', type=float, default=60.0,
                       help='Maximum simulation time in seconds')
    parser.add_argument('--nodes', type=int, default=5,
                       help='Number of Raft nodes in the cluster')
    parser.add_argument('--chaos', action='store_true',
                       help='Enable chaos testing')
    parser.add_argument('--chaos_scenario', type=str,
                       choices=['network_partition', 'leader_failure'],
                       default='network_partition',
                       help='Chaos testing scenario to execute')
    parser.add_argument('--chaos_duration', type=int, default=30,
                       help='Duration of chaos event in seconds')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)

    # Simulation configuration
    config = {
        'node_count': args.nodes,
        'message_drop_rate': 0.1,
        'min_latency': 0.1,
        'max_latency': 0.5,
        'node_class': RaftNode
    }

    # Create simulator with Raft nodes
    sim = EventDrivenSimulator(config)
    
    # Inject chaos if enabled
    if args.chaos:
        if args.chaos_scenario == 'network_partition':
            # Partition first 2 nodes from others
            sim.inject_failure(
                'partition',
                node_ids=[0, 1],
                duration=args.chaos_duration
            )
        elif args.chaos_scenario == 'leader_failure':
            # Crash the first node (likely leader)
            sim.inject_failure(
                'crash',
                node_id=0,
                recovery_time=args.chaos_duration
            )

    # Run the simulation
    logger.info(f"Starting simulation with {args.nodes} Raft nodes for {args.max_time} seconds")
    try:
        sim.run(max_time=args.max_time)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        sys.exit(1)

    # Print results
    print("\n=== Simulation Results ===")
    print("Node ID | Term | Role | Commit Index")
    for node_id, node in sim.nodes.items():
        print(f"{node_id:7} | {node.term:4} | {node.state.name:8} | {node.commit_index:12}")

    print("\n=== First 20 Events ===")
    for event in sim.event_log[:20]:
        print(f"{event['time']:.2f}s: {event['type']} - {event['data']}")


if __name__ == "__main__":
    main()