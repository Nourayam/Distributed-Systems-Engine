#!/usr/bin/env python3
import argparse
import logging
import sys
import os
import time
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from config import Config, validate_config
from simulation.simulation import Simulation
from nodes.raft_node import RaftNode
from failure.failure_injector import FailureInjector


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )


def create_simulation_config(args) -> Config:
    """Create simulation configuration from command line arguments"""
    config = Config()
    config.node_count = args.nodes
    config.message_drop_rate = args.message_drop_rate
    config.verbose_logging = args.verbose
    config.debug_mode = args.debug
    return config


def inject_chaos_scenarios(sim: Simulation, injector: FailureInjector, args) -> None:
    """Inject chaos testing scenarios based on arguments"""
    if not args.chaos:
        return
        
    logger = logging.getLogger("chaos")
    
    if args.chaos_scenario == 'network_partition':
        logger.info("Injecting network partition scenario")
        # Crash nodes to simulate partition
        injector.inject_node_crash("0", recovery_time=args.chaos_duration)
        injector.inject_node_crash("1", recovery_time=args.chaos_duration)
        
    elif args.chaos_scenario == 'leader_failure':
        logger.info("Injecting leader failure scenario")
        # Crash the first node (likely to become leader)
        injector.inject_node_crash("0", recovery_time=args.chaos_duration)
        
    elif args.chaos_scenario == 'rolling_failures':
        logger.info("Injecting rolling failures scenario")
        # Crash nodes in sequence
        for i in range(min(2, args.nodes)):
            delay = i * (args.chaos_duration / 3)
            recovery_time = args.chaos_duration - delay
            # Schedule crash with delay
            def delayed_crash(node_id: str, recovery: float):
                injector.inject_node_crash(node_id, recovery_time=recovery)
            
            # This is a simplified version - in real implementation you'd schedule this properly
            injector.inject_node_crash(str(i), recovery_time=recovery_time)


def print_simulation_results(sim: Simulation) -> None:
    """Print detailed simulation results"""
    print("\n" + "="*60)
    print("SIMULATION RESULTS")
    print("="*60)
    
    # Node states
    print(f"{'Node ID':<8} {'State':<10} {'Term':<6} {'Alive':<6} {'Log Size':<10}")
    print("-" * 60)
    
    for node_id, node in sim.nodes.items():
        if hasattr(node, 'get_state_info'):
            info = node.get_state_info()
            print(f"{info['node_id']:<8} {info['state']:<10} {info['current_term']:<6} "
                  f"{info['alive']:<6} {info['log_length']:<10}")
        else:
            print(f"{node_id:<8} {'UNKNOWN':<10} {'?':<6} {node.is_alive():<6} {'?':<10}")
    
    # Find leader
    leaders = [node for node in sim.nodes.values() 
              if hasattr(node, 'state') and node.state.name == 'LEADER']
    
    print(f"\nLeader: {leaders[0].node_id if leaders else 'None'}")
    if leaders:
        leader = leaders[0]
        print(f"Leader term: {leader.current_term}")
        print(f"Leader log size: {len(leader.log)}")
        print(f"Leader commit index: {leader.commit_index}")
    
    # Event summary
    print(f"\nTotal events processed: {len(sim.event_log)}")
    print(f"Simulation time: {sim.current_time:.2f} seconds")
    
    # Show recent events
    print(f"\nRecent events (last 10):")
    for event in sim.event_log[-10:]:
        print(f"  {event['timestamp']:.2f}s: {event['type']}")


def main():
    """Main entry point for the Raft simulator"""
    parser = argparse.ArgumentParser(description='Raft consensus simulator')
    parser.add_argument('--max_time', type=float, default=60.0,
                       help='Maximum simulation time in seconds')
    parser.add_argument('--nodes', type=int, default=5,
                       help='Number of Raft nodes in the cluster')
    parser.add_argument('--message_drop_rate', type=float, default=0.1,
                       help='Message drop rate (0.0 to 1.0)')
    parser.add_argument('--chaos', action='store_true',
                       help='Enable chaos testing')
    parser.add_argument('--chaos_scenario', type=str,
                       choices=['network_partition', 'leader_failure', 'rolling_failures'],
                       default='network_partition',
                       help='Chaos testing scenario to execute')
    parser.add_argument('--chaos_duration', type=float, default=10.0,
                       help='Duration of chaos event in seconds')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        validate_config()
        
        # Create simulation configuration
        config = create_simulation_config(args)
        
        # Create simulation
        sim = Simulation(config)
        
        # Create Raft nodes
        logger.info(f"Creating {args.nodes} Raft nodes")
        for i in range(args.nodes):
            node = RaftNode(str(i), sim)
            logger.debug(f"Created node {i}")
        
        # Create failure injector
        injector = FailureInjector(sim)
        
        # Inject chaos scenarios
        inject_chaos_scenarios(sim, injector, args)
        
        # Run simulation
        logger.info(f"Starting simulation for {args.max_time} seconds")
        start_time = time.time()
        
        try:
            sim.run(max_time=args.max_time)
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        
        end_time = time.time()
        logger.info(f"Simulation completed in {end_time - start_time:.2f} real seconds")
        
        # Print results
        print_simulation_results(sim)
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()