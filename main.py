
class ChaosMonkey:
    def __init__(self, raft_node: RaftNode):
        self.node = raft_node
        self.failure_modes = {
            'network_partition': self._simulate_partition,
            'leader_failure': self._kill_leader,
            'log_corruption': self._corrupt_log,
            'clock_skew': self._introduce_clock_skew,
            'disk_failure': self._simulate_disk_failure
        }
        self.chaos_active = False

    def run_test(self, scenario: str, duration: int = 60):
        """Execute chaos scenario with automatic recovery"""
        if scenario not in self.failure_modes:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        self.chaos_active = True
        logger.warning(f"🚀 Starting chaos test: {scenario}")
        
        # Run failure injection
        self.failure_modes[scenario]()
        
        # Monitor cluster behavior
        start_time = time.time()
        while time.time() - start_time < duration and self.chaos_active:
            self._verify_safety_properties()
            time.sleep(5)
        
        # Automatic recovery
        self._restore_normal_operation()
        logger.warning("✅ Chaos test completed")

    def _simulate_partition(self):
        """Simulate network partition by dropping messages"""
        def _filtered_send(to_node, msg):
            if random.random() < 0.7:  # 70% packet loss
                return False
            return original_send(to_node, msg)
        
        # Monkey patch the RPC sender
        self.original_send = self.node.rpc_send
        self.node.rpc_send = _filtered_send

    def _kill_leader(self):
        """Force current leader to step down"""
        if self.node.is_leader():
            # Leader suddenly becomes unresponsive
            self.node.stop_responding = True
        else:
            # Kill leader RPCs to this node
            leader = self.node.cluster.get_leader()
            self.node.cluster.blacklist[leader] = time.time() + 30

    def _corrupt_log(self):
        """Introduce log corruption in a random node"""
        target = random.choice(self.node.cluster.nodes)
        if target == self.node.id:
            # Corrupt our own log
            corrupt_index = random.randint(0, len(self.node.log.entries)-1)
            self.node.log.entries[corrupt_index].term = 9999
        else:
            # Send corrupted log to follower
            self.node.rpc_send(target, 
                InstallSnapshotRequest(
                    term=9999,  # Invalid term
                    last_index=999999,
                    data=b'corrupted'
                ))

    def _verify_safety_properties(self):
        """Ensure no safety violations occurred"""
        # 1. Check for split-brain
        leaders = set()
        for node in self.node.cluster.nodes:
            if node.leader_id:
                leaders.add(node.leader_id)
        if len(leaders) > 1:
            self.chaos_active = False
            raise SafetyViolation("Split-brain detected!")
        
        # 2. Verify log consistency
        committed = self.node.log.commit_index
        for entry in self.node.log.entries[:committed]:
            if not self._validate_entry(entry):
                self.chaos_active = False
                raise SafetyViolation("Log corruption detected!")

    def _restore_normal_operation(self):
        """Undo all chaos injections"""
        if hasattr(self, 'original_send'):
            self.node.rpc_send = self.original_send
        self.node.stop_responding = False
        self.node.cluster.blacklist.clear()
```

**Chaos Test Scenarios Table**:

| Scenario | Description | Verification Metric |
|----------|-------------|---------------------|
| Network Partition | 70% packet loss between nodes | Cluster should maintain availability or fail cleanly |
| Leader Failure | Random leader termination | New leader should be elected within election timeout |
| Log Corruption | Injected bad entries | Should detect and recover via snapshot transfer |
| Clock Skew | ±500ms clock changes | Lease mechanism should prevent stale reads |
| Disk Failure | Writes fail randomly | Should continue operating in degraded mode |

## Service Discovery Integration

Modern service discovery integration for dynamic Raft clusters:

```python
class ServiceDiscoveryIntegration:
    def __init__(self, raft_node: RaftNode, consul_host: str = 'localhost:8500'):
        self.node = raft_node
        self.consul = ConsulClient(consul_host)
        self.service_name = "raft-cluster"
        self.registration_id = f"{self.service_name}-{self.node.id}"
        self.watch_thread = None

    def register_node(self):
        """Register node with service discovery"""
        service = AgentService(
            id=self.registration_id,
            name=self.service_name,
            address=self.node.host,
            port=self.node.port,
            tags=[
                f"raft_id:{self.node.id}",
                f"status:{'leader' if self.node.is_leader() else 'follower'}"
            ],
            check=AgentCheck(
                tcp=f"{self.node.host}:{self.node.port}",
                interval="10s",
                timeout="5s",
                deregister="30s"
            )
        )
        self.consul.agent.service.register(service)

    def start_cluster_watcher(self):
        """Monitor cluster membership changes"""
        self.watch_thread = threading.Thread(
            target=self._watch_services,
            daemon=True
        )
        self.watch_thread.start()

    def _watch_services(self):
        """Background thread watching for membership changes"""
        last_index = None
        while True:
            try:
                index, services = self.consul.catalog.services(
                    index=last_index,
                    wait="5m"
                )
                if index != last_index:
                    self._update_cluster_membership(services)
                    last_index = index
            except ConsulException as e:
                logger.error(f"Service watch failed: {e}")
                time.sleep(5)

    def _update_cluster_membership(self, services):
        """Reconfigure cluster based on discovered nodes"""
        if self.service_name not in services:
            return

        # Get current healthy members
        healthy_nodes = []
        for node in self.consul.health.service(self.service_name)[1]:
            if all(check['Status'] == 'passing' for check in node['Checks']):
                tags = {t.split(':')[0]: t.split(':')[1] 
                       for t in node['Service']['Tags'] if ':' in t}
                healthy_nodes.append({
                    'id': tags['raft_id'],
                    'address': f"{node['Service']['Address']}:{node['Service']['Port']}",
                    'is_leader': tags.get('status') == 'leader'
                })

        # Update cluster configuration
        current_members = {m.id for m in self.node.cluster.members}
        discovered_members = {n['id'] for n in healthy_nodes}
        
        # Nodes to add
        for new_id in discovered_members - current_members:
            node = next(n for n in healthy_nodes if n['id'] == new_id)
            self.node.add_member(node['id'], node['address'])
        
        # Nodes to remove
        for dead_id in current_members - discovered_members:
            self.node.remove_member(dead_id)

        # Leader status update
        leaders = [n['id'] for n in healthy_nodes if n['is_leader']]
        if len(leaders) == 1 and leaders[0] != self.node.cluster.leader_id:
            self.node.cluster.update_leader(leaders[0])

    def update_leader_status(self):
        """Update service discovery when leadership changes"""
        self.consul.agent.service.register(
            id=self.registration_id,
            name=self.service_name,
            tags=[
                f"raft_id:{self.node.id}",
                f"status:{'leader' if self.node.is_leader() else 'follower'}"
            ]
        )
```

**Integration Architecture**:

```
┌───────────────────────┐    ┌───────────────────────┐
│      Raft Cluster     │    │   Service Discovery   │
│                       │    │   (Consul/Etcd/ZK)    │
│ ┌─────┐ ┌─────┐ ┌─────┐    │                       │
│ │Node1│ │Node2│ │Node3│◄───┤  • Membership        │
│ └─────┘ └─────┘ └─────┐    │  • Health Checks     │
│           ▲            │    │  • Leader Tracking   │
│           │            │    └───────────────────────┘
└───────────│────────────┘
            │
            ▼
┌───────────────────────┐
│   Chaos Engineering   │
│   Framework           │
│                       │
│ • Failure Injection   │
│ • Safety Verification │
│ • Automatic Recovery  │
└───────────────────────┘
```

## Combined Implementation Example

Here's how these systems integrate with your Raft node:

```python
class ProductionRaftNode(RaftNode):
    def __init__(self, node_id: str, consul_host: str):
        super().__init__(node_id)
        self.sd = ServiceDiscoveryIntegration(self, consul_host)
        self.chaos = ChaosMonkey(self)
        
        # Register periodic tasks
        self.tasks = [
            PeriodicTask(60, self.sd.register_node),
            PeriodicTask(300, self.run_chaos_test)
        ]
    
    def run_chaos_test(self):
        """Run random chaos test in production (controlled)"""
        if random.random() < 0.1:  # 10% chance to run test
            scenario = random.choice([
                'network_partition',
                'leader_failure',
                'log_corruption'
            ])
            self.chaos.run_test(scenario, duration=30)
    
    def on_leader_change(self, is_leader: bool):
        """Hook for leadership changes"""
        super().on_leader_change(is_leader)
        self.sd.update_leader_status()
        
        if is_leader:
            # Leaders monitor cluster health more aggressively
            self.tasks.append(PeriodicTask(10, self.check_cluster_health))
    
    def check_cluster_health(self):
        """Leader-specific health checks"""
        unhealthy = []
        for member in self.cluster.members:
            last_contact = time.time() - member.last_contact_time
            if last_contact > self.election_timeout:
                unhealthy.append(member.id)
        
        if unhealthy:
            logger.warning(f"Unhealthy members: {unhealthy}")
            # Potentially trigger reconfiguration
```

**Key Benefits**:
1. **Resilience Testing**: Automated verification of fault tolerance
2. **Dynamic Membership**: Automatic handling of node failures/additions
3. **Observability**: Real-time tracking of cluster state
4. **Self-Healing**: Automatic recovery from many failure scenarios

Would you like me to dive deeper into any specific aspect, such as:
- Implementing a more sophisticated network partition simulator?
- Adding Prometheus metrics to the chaos tests?
- Handling secure TLS communication with service discovery?
- Implementing a canary deployment pattern for Raft configuration changes?