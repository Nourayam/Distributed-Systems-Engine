from __future__ import annotations
from enum import Enum, auto
import logging
import random
from typing import Any, Dict, List, Optional

from ..base_node import Node
from ..simulation.simulation_events import Event, EventType


class RaftState(Enum):
    """Possible states for a Raft node."""
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()


class RaftNode(Node):
    """Implementation of a node using the Raft consensus algorithm."""

    # Constants in seconds
    ELECTION_TIMEOUT_MIN = 0.15
    ELECTION_TIMEOUT_MAX = 0.30
    HEARTBEAT_INTERVAL = 0.05

    def __init__(self, node_id: str, simulation):
        """Initialize a Raft node."""
        super().__init__(node_id, simulation)

        # Persistent state
        self.current_term: int = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []

        # Volatile state
        self.commit_index: int = 0
        self.last_applied: int = 0
        self.state: RaftState = RaftState.FOLLOWER

        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Timeout tracking
        self.election_timeout: float = self._random_election_timeout()
        self.last_heartbeat_time: float = simulation.clock

        # Schedule initial timeout
        self.schedule_timeout(self.election_timeout, "election")

    def _random_election_timeout(self) -> float:
        """Generate random election timeout within configured bounds."""
        return random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX)

    def become_follower(self, term: int) -> None:
        """Transition to follower state."""
        assert term >= self.current_term, "Term cannot decrease"
        self.current_term = term
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self._reset_election_timeout()


    def become_candidate(self) -> None:
        #Transition to candidate state and start election
        self.current_term += 1
        self.state = RaftState.CANDIDATE
        self.voted_for = self.node_id
        
        # Request votes from all peers
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1]['term'] if self.log else 0
        
        for peer in self.simulation.nodes.values():
            if peer.node_id == self.node_id:
                continue
                
            self.send_message(
                peer.node_id,
                "RequestVote",
                {
                    'term': self.current_term,
                    'candidate_id': self.node_id,
                    'last_log_index': last_log_index,
                    'last_log_term': last_log_term
                }
            )
        
        self._reset_election_timeout()
    
    def become_leader(self) -> None:
        #Transition to leader state
        self.state = RaftState.LEADER
        
        # Initialise leader state
        next_idx = len(self.log)
        self.next_index = {
            str(node_id): next_idx 
            for node_id in self.simulation.nodes
        }
        self.match_index = {str(node_id): 0 for node_id in self.simulation.nodes}
        
        # Send initial heartbeats
        self._send_heartbeats()
    
    def _reset_election_timeout(self) -> None:
        #Reset election timeout with new random value
        self.election_timeout = self._random_election_timeout()
        self.last_heartbeat_time = self.simulation.clock
        self.schedule_timeout(self.election_timeout, "election")
    
    def _send_heartbeats(self) -> None:
        #Send AppendEntries messages to all followers
        for node in self.simulation.nodes.values():
            if node.node_id == self.node_id:
                continue
                
            # Prepare AppendEntries message
            next_idx = self.next_index.get(node.node_id, 0)
            prev_log_index = next_idx - 1
            prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 else 0
            entries = self.log[next_idx:] if next_idx < len(self.log) else []
            
            self.send_message(
                node.node_id,
                "AppendEntries",
                {
                    'term': self.current_term,
                    'leader_id': self.node_id,
                    'prev_log_index': prev_log_index,
                    'prev_log_term': prev_log_term,
                    'entries': entries,
                    'leader_commit': self.commit_index
                }
            )
    
    def receive_message(self, event: Event) -> None:
        #Handle incoming messages
        data = event.data
        
        if data['type'] == 'RequestVote':
            self._handle_request_vote(data['src'], data)
        elif data['type'] == 'RequestVoteResponse':
            self._handle_request_vote_response(data['src'], data)
        elif data['type'] == 'AppendEntries':
            self._handle_append_entries(data['src'], data)
        elif data['type'] == 'AppendEntriesResponse':
            self._handle_append_entries_response(data['src'], data)
    
    def tick(self, current_time: float) -> None:
        """Handle time-based operations."""
        # Check for election timeout
        if (current_time - self.last_heartbeat_time) > self.election_timeout:
            if self.state != RaftState.LEADER:
                self.become_candidate()
        
        # Send heartbeats if leader
        if self.state == RaftState.LEADER:
            if current_time - self.last_heartbeat_time >= self.HEARTBEAT_INTERVAL:
                self._send_heartbeats()
                self.last_heartbeat_time = current_time

    
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


#please clean up any import issues