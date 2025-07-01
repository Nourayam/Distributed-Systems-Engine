from __future__ import annotations
from typing import Dict, List, Optional, Any
import random
import time
from enum import Enum, auto
from nodes.base_node import Node
from simulation.simulation_events import Event, EventType


class RaftState(Enum):
    #Enum representing the possible states of a Raft node
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()


class RaftNode(Node):
    #Implementation of a node using the Raft consensus algorithm
    
    # Constants for Raft timing (in milliseconds)
    ELECTION_TIMEOUT_MIN = 150
    ELECTION_TIMEOUT_MAX = 300
    HEARTBEAT_INTERVAL = 50
    
    def __init__(self, node_id: str, peers: List[str]):
        
        # Initialise a Raft node.
        
        # Args:
        #     node_id: Unique identifier for this node
        #     peers: List of peer node IDs in the cluster
        
        super().__init__(node_id, peers)
        
        # Persistent state (should be stored on disk in a real implementation)
        self.current_term: int = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []  # Each entry has 'term' and 'command'
        
        # Volatile state
        self.commit_index: int = 0
        self.last_applied: int = 0
        self.state: RaftState = RaftState.FOLLOWER
        
        # Leader state (reinitialized after election)
        self.next_index: Dict[str, int] = {}  # For each peer, index of next log entry to send
        self.match_index: Dict[str, int] = {}  # For each peer, index of highest known replicated entry
        
        # Election timeout tracking
        self.election_timeout: float = self._random_election_timeout()
        self.last_heartbeat_time: float = time.time()
        
        # If leader, schedule regular heartbeats
        if self.state == RaftState.LEADER:
            self._schedule_heartbeat()
    
    def _random_election_timeout(self) -> float:
        #Generate a random election timeout within the configured range
        return random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX) / 1000.0
    
    def become_follower(self, term: int) -> None:
        
        # Transition to follower state.
        
        # Args:
        #     term: The new current term (must be >= current_term)
        
        assert term >= self.current_term, "Term cannot decrease"
        self.current_term = term
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self._reset_election_timeout()
    
    def become_candidate(self) -> None:
        #Transition to candidate state and start a new election
        self.current_term += 1
        self.state = RaftState.CANDIDATE
        self.voted_for = self.node_id  # Vote for self
        
        # Request votes from all peers
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1]['term'] if self.log else 0
        
        vote_request = {
            'type': 'RequestVote',
            'term': self.current_term,
            'candidate_id': self.node_id,
            'last_log_index': last_log_index,
            'last_log_term': last_log_term
        }
        
        for peer in self.peers:
            self.send_message(peer, vote_request)
        
        self._reset_election_timeout()
    
    def become_leader(self) -> None:
        #Transition to leader state and initialize leader-specific state
        self.state = RaftState.LEADER
        
        # Initialise leader state
        next_idx = len(self.log)
        self.next_index = {peer: next_idx for peer in self.peers}
        self.match_index = {peer: 0 for peer in self.peers}
        
        # Send initial empty AppendEntries (heartbeat)
        self._send_heartbeats()
        self._schedule_heartbeat()
    
    def _reset_election_timeout(self) -> None:
    #Reset the election timeout to a new random value
        self.election_timeout = self._random_election_timeout()
        self.last_heartbeat_time = time.time()
    
    def _schedule_heartbeat(self) -> None:
        #Schedule the next heartbeat if this node is the leader
        if self.state == RaftState.LEADER:
            self.schedule_event(
                Event(
                    EventType.TIMER,
                    self.node_id,
                    {'type': 'Heartbeat'},
                    delay=self.HEARTBEAT_INTERVAL / 1000.0
                )
            )
    
    def _send_heartbeats(self) -> None:
        #Send AppendEntries messages to all followers (heartbeat if no entries)
        for peer in self.peers:
            next_idx = self.next_index[peer]
            prev_log_index = next_idx - 1
            prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 else 0
            entries = self.log[next_idx:] if next_idx < len(self.log) else []
            
            append_entries = {
                'type': 'AppendEntries',
                'term': self.current_term,
                'leader_id': self.node_id,
                'prev_log_index': prev_log_index,
                'prev_log_term': prev_log_term,
                'entries': entries,
                'leader_commit': self.commit_index
            }
            
            self.send_message(peer, append_entries)
    
    def _check_election_timeout(self) -> None:
        #Check if election timeout has elapsed and start new election if needed.
        if (time.time() - self.last_heartbeat_time) > self.election_timeout:
            if self.state != RaftState.LEADER:
                self.become_candidate()
    
    def _update_commit_index(self) -> None:
        
        # Update commit index based on match_index of followers.
        
        # If there exists an N such that N > commit_index and a majority of
        # match_index[i] ≥ N and log[N].term == current_term, set commit_index = N.
        
        if self.state != RaftState.LEADER:
            return
        
        # Get all match indices (including leader's own log length)
        match_indices = sorted(list(self.match_index.values()) + [len(self.log) - 1])
        majority_index = match_indices[len(match_indices) // 2]
        
        if (majority_index > self.commit_index and 
                self.log[majority_index]['term'] == self.current_term):
            self.commit_index = majority_index
            self._apply_committed_entries()
    
    def _apply_committed_entries(self) -> None:
        #Apply all committed entries that haven't been applied yet
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            self.apply(entry)
    
    def apply(self, entry: Dict[str, Any]) -> None:
        
        # Apply a committed log entry to the state machine (stub implementation).
        
        # Args:
        #     entry: The log entry to apply (contains 'term' and 'command')
        
        # In a real implementation, this would apply the command to the state machine
        print(f"Node {self.node_id} applying command: {entry['command']}")
    
    def handle_message(self, event: Event) -> None:
        
        # Handle an incoming message or timer event.
        
        # Args:
        #     event: The event to handle
        
        data = event.data
        
        if data['type'] == 'RequestVote':
            self._handle_request_vote(event.source, data)
        elif data['type'] == 'RequestVoteResponse':
            self._handle_request_vote_response(event.source, data)
        elif data['type'] == 'AppendEntries':
            self._handle_append_entries(event.source, data)
        elif data['type'] == 'AppendEntriesResponse':
            self._handle_append_entries_response(event.source, data)
        elif data['type'] == 'Heartbeat':
            self._handle_heartbeat_timer()
    
    def _handle_request_vote(self, candidate_id: str, data: Dict[str, Any]) -> None:
        
        # Handle a RequestVote RPC.
        
        # Args:
        #     candidate_id: ID of the candidate requesting the vote
        #     data: The RequestVote message contents
        
        term = data['term']
        granted = False
        
        # Reply False if term < currentTerm
        if term < self.current_term:
            pass
        # If votedFor is null or candidateId, and candidate's log is at least as up-to-date as ours
        elif (self.voted_for is None or self.voted_for == candidate_id):
            last_log_index = len(self.log) - 1
            last_log_term = self.log[-1]['term'] if self.log else 0
            
            if (data['last_log_term'] > last_log_term or 
                (data['last_log_term'] == last_log_term and 
                 data['last_log_index'] >= last_log_index)):
                granted = True
                self.become_follower(term)
                self.voted_for = candidate_id
        
        response = {
            'type': 'RequestVoteResponse',
            'term': self.current_term,
            'vote_granted': granted
        }
        self.send_message(candidate_id, response)
    
    def _handle_request_vote_response(self, voter_id: str, data: Dict[str, Any]) -> None:
    
        # Handle a RequestVoteResponse RPC.
        
        # Args:
        #     voter_id: ID of the voter
        #     data: The RequestVoteResponse message contents
        
        if self.state != RaftState.CANDIDATE:
            return
        
        term = data['term']
        if term > self.current_term:
            self.become_follower(term)
            return
        
        if data['vote_granted']:
            # Count votes and become leader if majority
            votes = sum(1 for peer in self.peers 
                       if self.received_votes.get(peer, False)) + 1  # +1 for self-vote
            
            if votes > len(self.peers) / 2:
                self.become_leader()
    
    def _handle_append_entries(self, leader_id: str, data: Dict[str, Any]) -> None:
        
        # Handle an AppendEntries RPC (heartbeat or log replication).
        
        # Args:
        #     leader_id: ID of the leader sending the entries
        #     data: The AppendEntries message contents
        
        term = data['term']
        success = False
        
        if term < self.current_term:
            pass  # Reply False if term < currentTerm
        else:
            self.become_follower(term)
            self._reset_election_timeout()
            
            # Check if log contains entry at prevLogIndex with term matching prevLogTerm
            prev_log_index = data['prev_log_index']
            prev_log_term = data['prev_log_term']
            
            if (prev_log_index >= len(self.log) or 
                (prev_log_index >= 0 and self.log[prev_log_index]['term'] != prev_log_term)):
                pass  # Log inconsistency
            else:
                success = True
                
                # Delete any conflicting entries and append new ones
                if data['entries']:
                    self.log = self.log[:prev_log_index + 1] + data['entries']
                
                # Update commit index if leader's commit index is higher
                if data['leader_commit'] > self.commit_index:
                    self.commit_index = min(data['leader_commit'], len(self.log) - 1)
                    self._apply_committed_entries()
        
        response = {
            'type': 'AppendEntriesResponse',
            'term': self.current_term,
            'success': success,
            'match_index': prev_log_index + len(data.get('entries', []))
        }
        self.send_message(leader_id, response)
    
    def _handle_append_entries_response(self, follower_id: str, data: Dict[str, Any]) -> None:

        # Handle an AppendEntriesResponse RPC.
        
        # Args:
        #     follower_id: ID of the follower responding
        #     data: The AppendEntriesResponse message contents
        
        if self.state != RaftState.LEADER:
            return
        
        term = data['term']
        if term > self.current_term:
            self.become_follower(term)
            return
        
        if data['success']:
            # Update nextIndex and matchIndex for follower
            self.next_index[follower_id] = data['match_index'] + 1
            self.match_index[follower_id] = data['match_index']
            self._update_commit_index()
        else:
            # Decrement nextIndex and retry
            self.next_index[follower_id] = max(0, self.next_index[follower_id] - 1)
            self._send_heartbeats()  # Will resend AppendEntries with updated nextIndex
    
    def _handle_heartbeat_timer(self) -> None:
        #Handle the heartbeat timer event (send new heartbeats if leader)
        if self.state == RaftState.LEADER:
            self._send_heartbeats()
            self._schedule_heartbeat()
        else:
            self._check_election_timeout()
    
    def on_event(self, event: Event) -> None:
    
        # Handle an incoming event (message or timer).
        
        # Args:
        #     event: The event to handle
        
        if event.type == EventType.MESSAGE:
            self.handle_message(event)
        elif event.type == EventType.TIMER:
            if event.data['type'] == 'Heartbeat':
                self._handle_heartbeat_timer()
    
    def submit_command(self, command: Any) -> None:
        
        # Submit a new command to be replicated by Raft (leader only).
        
        # Args:
        #     command: The command to append to the log
        
        if self.state == RaftState.LEADER:
            entry = {
                'term': self.current_term,
                'command': command
            }
            self.log.append(entry)
            self._send_heartbeats()  # Replicate immediately