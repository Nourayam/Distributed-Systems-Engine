Let me expand on **cluster membership changes** and **network partition handling**, as these are crucial for production systems that need to scale and remain available during failures.

## 5. Cluster Membership Changes (Joint Consensus)

```python
class RaftNode:
    def __init__(self, node_id: int, config: RaftConfig):
        # Existing initialization...
        self.configurations = {
            'current': config.cluster_nodes,  # Set of {node_id: address}
            'next': None,                     # Pending configuration
        }
        self.config_log_index = 0             # Index of last config change

    def handle_configuration_change(self, new_config: Dict):
        """
        Initiate cluster configuration change using joint consensus.
        
        Args:
            new_config: Dictionary of {node_id: address} for new configuration
        """
        if self.state != 'leader':
            raise NotLeaderError("Only leader can change configuration")
            
        # Create configuration entry for joint consensus (C_old + C_new)
        joint_config = {
            'old': self.configurations['current'],
            'new': new_config
        }
        
        entry = {
            'term': self.current_term,
            'index': len(self.log) + 1,
            'command': {
                'type': 'config_change',
                'config': joint_config
            }
        }
        
        self.log.append(entry)
        self.replicate_log()
        
    def apply_configuration_change(self, entry: Dict):
        """
        Apply a configuration change entry from the log.
        Implements the joint consensus protocol.
        """
        config = entry['command']['config']
        
        if isinstance(config, dict) and 'old' in config:
            # Joint consensus stage
            self.configurations['next'] = config['new']
            self.config_log_index = entry['index']
            
            # Replicate to both old and new configurations
            self.update_replication_targets(
                set(config['old'].keys()) | set(config['new'].keys())
            )
        else:
            # Final single configuration stage
            self.configurations['current'] = config
            self.configurations['next'] = None
            self.config_log_index = entry['index']
            
            # Only replicate to new configuration
            self.update_replication_targets(set(config.keys()))
            
    def update_replication_targets(self, node_ids: Set[int]):
        """Update which nodes we should replicate to"""
        for node_id in node_ids:
            if node_id != self.node_id:
                self.next_index[node_id] = len(self.log) + 1
                self.match_index[node_id] = 0
                
    def can_reach_quorum(self, index: int) -> bool:
        """
        Check if a log entry has been replicated to a quorum,
        considering both old and new configurations during transition.
        """
        if self.configurations['next'] is None:
            # Single configuration
            voters = set(self.configurations['current'].keys())
            quorum_size = (len(voters) // 2) + 1
        else:
            # Joint consensus requires both old and new quorums
            old_voters = set(self.configurations['current'].keys())
            new_voters = set(self.configurations['next'].keys())
            quorum_size = max(
                (len(old_voters) // 2) + 1,
                (len(new_voters) // 2) + 1
            )
            voters = old_voters | new_voters
            
        # Count replicas including self
        count = 1  # leader always has entry
        for node_id in voters:
            if node_id != self.node_id and self.match_index[node_id] >= index:
                count += 1
                
        return count >= quorum_size
```

## 6. Network Partition Handling

```python
class RaftNode:
    def __init__(self, node_id: int, config: RaftConfig):
        # Existing initialization...
        self.last_contact_time = {}  # node_id: last successful contact time
        self.quorum_timeout = 5.0    # Time without quorum before stepping down
        
    def detect_partition(self):
        """
        Detect if we're in a network partition and potentially step down.
        Runs periodically in a background thread.
        """
        while True:
            time.sleep(1.0)
            if self.state == 'leader':
                if not self.has_quorum_contact():
                    self.logger.warning("Lost contact with quorum - stepping down")
                    self.convert_to_follower()
                    
    def has_quorum_contact(self) -> bool:
        """Check if we've recently contacted a quorum of nodes"""
        if self.configurations['next'] is None:
            voters = set(self.configurations['current'].keys())
        else:
            voters = (set(self.configurations['current'].keys()) | 
                     set(self.configurations['next'].keys()))
        
        quorum_size = (len(voters) // 2) + 1
        active_nodes = 1  # count self
        
        now = time.time()
        for node_id in voters:
            if (node_id != self.node_id and 
                now - self.last_contact_time.get(node_id, 0) < self.quorum_timeout):
                active_nodes += 1
                
        return active_nodes >= quorum_size
        
    def handle_append_entries_response(self, sender_id: int, success: bool):
        """Update last contact time when receiving responses"""
        self.last_contact_time[sender_id] = time.time()
        # Rest of existing response handling...
        
    def handle_partition_recovery(self):
        """
        Special handling when recovering from a network partition.
        """
        # 1. Check if our log is stale compared to new leader
        if self.state == 'candidate' and self.election_timeout_elapsed():
            self.start_election()  # Normal election
            
        # 2. If we were leader but partitioned, we might need to roll back
        elif self.state == 'leader' and not self.has_quorum_contact():
            self.convert_to_follower()
            
        # 3. Check for configuration changes we might have missed
        self.catch_up_on_missed_configurations()
        
    def catch_up_on_missed_configurations(self):
        """Check log for any configuration changes we might have missed"""
        # In a real implementation, you'd scan the log for missed config entries
        # and update your configuration state accordingly
        pass
