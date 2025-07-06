# Event Logger for distributed system simulation
# Features:
# - Tracks message events (sent/received/dropped)
# - Records node state transitions
# - Supports multiple output formats (stdout/file)
# - Configurable verbosity levels
# - Structured logging options

import json
from enum import Enum
from typing import Dict, Optional, Union, TextIO

class LogLevel(Enum):
    QUIET = 0
    BASIC = 1
    VERBOSE = 2
    DEBUG = 3

class EventLogger:
    def __init__(
        self,
        level: LogLevel = LogLevel.BASIC,
        output_file: Optional[str] = None,
        structured: bool = False
    ):
        self.level = level
        self.structured = structured
        self.output_file = output_file
        self._file_handle: Optional[TextIO] = None

    def __enter__(self):
        if self.output_file:
            self._file_handle = open(self.output_file, 'a')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_handle:
            self._file_handle.close()

    def log_event(
        self,
        event_type: str,
        node_id: str,
        message: Optional[str] = None,
        details: Optional[Dict] = None,
        level: LogLevel = LogLevel.BASIC
    ):
        if level.value > self.level.value:
            return

        log_entry = {
            'event': event_type,
            'node': node_id,
            'timestamp': self._get_timestamp(),
            'message': message,
            'details': details or {}
        }

        if self.structured:
            output = json.dumps(log_entry)
        else:
            output = self._format_plaintext(log_entry)

        self._write_output(output)

    def _get_timestamp(self) -> float:
        # TODO: Replace with system's time source
        import time
        return time.time()

    def _format_plaintext(self, entry: Dict) -> str:
        return (
            f"[{entry['timestamp']:.6f}] {entry['node']} - {entry['event']}: "
            f"{entry['message'] or ''}"
        )

    def _write_output(self, text: str):
        if self._file_handle:
            self._file_handle.write(text + '\n')
        else:
            print(text)

# TODO: Add thread-safety if used in multi-threaded context
# TODO: Consider adding log rotation for file output
# TODO: Add support for different serialization formats (e.g. YAML)
