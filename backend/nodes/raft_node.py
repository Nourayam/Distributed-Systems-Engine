from enum import Enum, auto
import logging
import random
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.simulation_events import Event
    from simulation.simulation import Simulation

from nodes.base_node import Node

logger = logging.getLogger(__name__)


class RaftState(Enum):
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()


class RaftNode(Node):
    #using the Raft consensus algorithm

    #constants in seconds
    ELECTION_TIMEOUT_MIN = 1.0
    ELECTION_TIMEOUT_MAX = 2.0
    HEARTBEAT_INTERVAL = 0.5

    def __init__(self, node_id: str, simulation: 'Simulation'):
        super().__init__(node_id, simulation)

        #persistent state
        self.current_term: int = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []

        #volatile state
        self.commit_index: int = 0
        self.last_applied: int = 0
        self.state: RaftState = RaftState.FOLLOWER

        #leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        #vote tracking
        self.votes_received: Set[str] = set()
        self.votes_needed: int = 0

        #timeout tracking
        self.election_timeout: float = self._random_election_timeout()
        self.last_heartbeat_time: float = simulation.current_time

        self.schedule_timeout(self.election_timeout, "election")
        
        self.logger.info(f"Raft node initialised in {self.state.name} state")

    def _random_election_timeout(self) -> float:
        return random.uniform(self.ELECTION_TIMEOUT_MIN, self.ELECTION_TIMEOUT_MAX)

    def _get_other_nodes(self) -> List[str]:
        return [node_id for node_id in self.simulation.nodes.keys() if node_id != self.node_id]

    def become_follower(self, term: int) -> None:
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            
        self.state = RaftState.FOLLOWER
        self.votes_received.clear()
        self._reset_election_timeout()
        
        self.logger.info(f"Became FOLLOWER for term {self.current_term}")

    def become_candidate(self) -> None:
        self.current_term += 1
        self.state = RaftState.CANDIDATE
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}  # Vote for self
        
        #calculate votes needed for majority
        total_nodes = len(self.simulation.nodes)
        self.votes_needed = (total_nodes // 2) + 1
        
        self.logger.info(f"Became CANDIDATE for term {self.current_term}, need {self.votes_needed} votes")
        
        #request votes from all peers
        self._request_votes()
        self._reset_election_timeout()

    def _request_votes(self) -> None:
        #sends the votes
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1]['term'] if self.log else 0
        
        for peer_id in self._get_other_nodes():
            payload = {
                'term': self.current_term,
                'candidate_id': self.node_id,
                'last_log_index': last_log_index,
                'last_log_term': last_log_term
            }
            self.send_message(peer_id, "RequestVote", payload)

    def become_leader(self) -> None:
        #transition to leader state
        self.state = RaftState.LEADER
        
        next_idx = len(self.log)
        self.next_index = {node_id: next_idx for node_id in self._get_other_nodes()}
        self.match_index = {node_id: 0 for node_id in self._get_other_nodes()}
        
        self.logger.info(f"Became LEADER for term {self.current_term}")
        
        self._send_heartbeats()
        self._schedule_heartbeat()

    def _reset_election_timeout(self) -> None:
        #reset with new random value"""
        self.election_timeout = self._random_election_timeout()
        self.last_heartbeat_time = self.simulation.current_time

    def _send_heartbeats(self) -> None:
        #send AppendEntries messages to all followers
        for peer_id in self._get_other_nodes():
            self._send_append_entries(peer_id)

    def _send_append_entries(self, peer_id: str) -> None:
        #send AppendEntries message to a specific peer
        next_idx = self.next_index.get(peer_id, 0)
        prev_log_index = next_idx - 1
        prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 and prev_log_index < len(self.log) else 0
        entries = self.log[next_idx:] if next_idx < len(self.log) else []
        
        payload = {
            'term': self.current_term,
            'leader_id': self.node_id,
            'prev_log_index': prev_log_index,
            'prev_log_term': prev_log_term,
            'entries': entries,
            'leader_commit': self.commit_index
        }
        
        self.send_message(peer_id, "AppendEntries", payload)

    def _schedule_heartbeat(self) -> None:
        self.schedule_timeout(self.HEARTBEAT_INTERVAL, "heartbeat")

    def receive_message(self, event: 'Event') -> None:
        if not self.is_alive():
            return
            
        data = event.data
        message_type = data['type']
        sender_id = data['src']
        payload = data['payload']
        
        try:
            if message_type == 'RequestVote':
                self._handle_request_vote(sender_id, payload)
            elif message_type == 'RequestVoteResponse':
                self._handle_request_vote_response(sender_id, payload)
            elif message_type == 'AppendEntries':
                self._handle_append_entries(sender_id, payload)
            elif message_type == 'AppendEntriesResponse':
                self._handle_append_entries_response(sender_id, payload)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
        except Exception as e:
            self.logger.error(f"Error handling {message_type}: {e}", exc_info=True)

    def tick(self, current_time: float) -> None:
        #time-based operations
        if not self.is_alive():
            return
            
        # Check for election timeout (followers and candidates)
        if self.state in [RaftState.FOLLOWER, RaftState.CANDIDATE]:
            if (current_time - self.last_heartbeat_time) >= self.election_timeout:
                self.logger.debug("Election timeout triggered")
                self.become_candidate()

    def handle_election_timeout(self) -> None:
        if self.state != RaftState.LEADER:
            self.logger.debug("Election timeout - starting new election")
            self.become_candidate()

    def handle_heartbeat_timeout(self) -> None:
        if self.state == RaftState.LEADER:
            self._send_heartbeats()
            self._schedule_heartbeat()

    def _handle_request_vote(self, candidate_id: str, data: Dict[str, Any]) -> None:
        term = data['term']
        last_log_index = data['last_log_index']
        last_log_term = data['last_log_term']
        
        vote_granted = False
        
        #update the term if candidate's term is higher
        if term > self.current_term:
            self.become_follower(term)
        
        #grants vote if conditions are met
        if (term == self.current_term and 
            (self.voted_for is None or self.voted_for == candidate_id) and
            self._is_log_up_to_date(last_log_index, last_log_term)):
            
            vote_granted = True
            self.voted_for = candidate_id
            self.last_heartbeat_time = self.simulation.current_time
            self.logger.debug(f"Granted vote to {candidate_id} for term {term}")
        else:
            self.logger.debug(f"Denied vote to {candidate_id} for term {term}")
        
        response = {
            'term': self.current_term,
            'vote_granted': vote_granted
        }
        self.send_message(candidate_id, "RequestVoteResponse", response)

    def _handle_request_vote_response(self, voter_id: str, data: Dict[str, Any]) -> None:
        if self.state != RaftState.CANDIDATE:
            return
        
        term = data['term']
        vote_granted = data['vote_granted']
        
        # Update term if response has higher term
        if term > self.current_term:
            self.become_follower(term)
            return
        
        # Count vote if granted
        if vote_granted and term == self.current_term:
            self.votes_received.add(voter_id)
            self.logger.debug(f"Received vote from {voter_id} ({len(self.votes_received)}/{self.votes_needed})")
            
            # Check if we have majority
            if len(self.votes_received) >= self.votes_needed:
                self.become_leader()

    def _handle_append_entries(self, leader_id: str, data: Dict[str, Any]) -> None:
        term = data['term']
        prev_log_index = data['prev_log_index']
        prev_log_term = data['prev_log_term']
        entries = data['entries']
        leader_commit = data['leader_commit']
        
        success = False
        
        #updates term if leader's term is higher
        if term > self.current_term:
            self.become_follower(term)
        
        if term == self.current_term:
            if self.state == RaftState.CANDIDATE:
                self.become_follower(term)
            
            self.last_heartbeat_time = self.simulation.current_time
            
            #log consistency check
            if self._log_consistency_check(prev_log_index, prev_log_term):
                success = True
                
                if entries:
                    #remove conflicting entries and append new ones
                    self.log = self.log[:prev_log_index + 1] + entries
                    self.logger.debug(f"Appended {len(entries)} entries")
                
                if leader_commit > self.commit_index:
                    self.commit_index = min(leader_commit, len(self.log) - 1)
                    self._apply_committed_entries()
        
        # Send response
        response = {
            'term': self.current_term,
            'success': success,
            'match_index': prev_log_index + len(entries) if success else 0
        }
        self.send_message(leader_id, "AppendEntriesResponse", response)

    def _handle_append_entries_response(self, follower_id: str, data: Dict[str, Any]) -> None:
        if self.state != RaftState.LEADER:
            return
        
        term = data['term']
        success = data['success']
        match_index = data.get('match_index', 0)
        
        #updates term if response has higher term
        if term > self.current_term:
            self.become_follower(term)
            return
        
        if term == self.current_term:
            if success:
                self.next_index[follower_id] = match_index + 1
                self.match_index[follower_id] = match_index
                self._update_commit_index()
                self.logger.debug(f"Updated indices for {follower_id}: next={self.next_index[follower_id]}, match={match_index}")
            else:
                #decrement next_index and retry
                self.next_index[follower_id] = max(0, self.next_index[follower_id] - 1)
                self.logger.debug(f"Log inconsistency with {follower_id}, decremented next_index to {self.next_index[follower_id]}")
                #will retry on next heartbeat

    def _is_log_up_to_date(self, last_log_index: int, last_log_term: int) -> bool:
        if not self.log:
            return True
        
        our_last_term = self.log[-1]['term']
        our_last_index = len(self.log) - 1
        
        return (last_log_term > our_last_term or 
                (last_log_term == our_last_term and last_log_index >= our_last_index))

    def _log_consistency_check(self, prev_log_index: int, prev_log_term: int) -> bool:
#checks the logs matchup
        if prev_log_index == -1:
            return True
        
        if prev_log_index >= len(self.log):
            return False
        
        return self.log[prev_log_index]['term'] == prev_log_term

    def _update_commit_index(self) -> None:
        if self.state != RaftState.LEADER:
            return
        
        #find highest index replicated on majority
        for index in range(len(self.log) - 1, self.commit_index, -1):
            if self.log[index]['term'] == self.current_term:
                replicated_count = 1  # Leader has it
                for match_idx in self.match_index.values():
                    if match_idx >= index:
                        replicated_count += 1
                
                if replicated_count > len(self.simulation.nodes) // 2:
                    self.commit_index = index
                    self._apply_committed_entries()
                    self.logger.debug(f"Advanced commit index to {index}")
                    break

    def _apply_committed_entries(self) -> None:
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            self.logger.debug(f"Applied entry {self.last_applied}: {entry}")

    def submit_command(self, command: Any) -> bool:
        #leader only
        if self.state != RaftState.LEADER:
            return False
        
        entry = {
            'term': self.current_term,
            'command': command,
            'index': len(self.log)
        }
        self.log.append(entry)
        self.logger.info(f"Added command to log at index {len(self.log) - 1}")
        
        # Replicate immediately
        self._send_heartbeats()
        return True

    def get_state_info(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'state': self.state.name,
            'current_term': self.current_term,
            'voted_for': self.voted_for,
            'log_length': len(self.log),
            'commit_index': self.commit_index,
            'last_applied': self.last_applied,
            'alive': self.is_alive(),
            'votes_received': len(self.votes_received) if self.state == RaftState.CANDIDATE else 0,
            'votes_needed': self.votes_needed if self.state == RaftState.CANDIDATE else 0
        }