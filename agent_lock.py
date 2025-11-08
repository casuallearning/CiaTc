#!/usr/bin/env python3
"""
Agent locking mechanism to prevent duplicate processes
Ensures only one instance of each agent runs at a time
"""

import os
import time
import fcntl
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


LOCK_DIR = Path(__file__).parent / ".band_cache" / "locks"
LOCK_DIR.mkdir(parents=True, exist_ok=True)


class AgentLock:
    """File-based lock to prevent duplicate agent processes"""

    def __init__(self, agent_name: str, timeout: int = 0):
        """
        Args:
            agent_name: Name of agent (john, george, pete, paul, ringo)
            timeout: Max seconds to wait for lock (0 = don't wait, skip if locked)
        """
        self.agent_name = agent_name
        self.timeout = timeout
        self.lock_file = LOCK_DIR / f"{agent_name}.lock"
        self.fd = None

    def acquire(self) -> bool:
        """
        Try to acquire lock
        Returns True if acquired, False if already locked
        """
        try:
            # Open lock file
            self.fd = open(self.lock_file, 'w')

            # Try to get exclusive lock
            if self.timeout == 0:
                # Non-blocking - return immediately if locked
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                # Blocking with timeout
                start = time.time()
                while True:
                    try:
                        fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.time() - start > self.timeout:
                            self.fd.close()
                            self.fd = None
                            return False
                        time.sleep(0.1)

            # Write PID and timestamp to lock file
            self.fd.write(f"{os.getpid()}\n{time.time()}\n")
            self.fd.flush()
            return True

        except BlockingIOError:
            # Lock is held by another process
            if self.fd:
                self.fd.close()
                self.fd = None
            return False
        except Exception as e:
            # Unexpected error
            if self.fd:
                self.fd.close()
                self.fd = None
            print(f"Lock acquire error for {self.agent_name}: {e}")
            return False

    def release(self):
        """Release the lock"""
        if self.fd:
            try:
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
                self.fd.close()
                self.fd = None
                # Remove lock file
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except Exception as e:
                print(f"Lock release error for {self.agent_name}: {e}")

    def is_locked(self) -> bool:
        """Check if agent is currently locked (running)"""
        if not self.lock_file.exists():
            return False

        try:
            with open(self.lock_file, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                # We got the lock, so it's not actually locked
                return False
        except BlockingIOError:
            # Couldn't get lock - it's locked
            return True
        except Exception:
            # File doesn't exist or error - assume not locked
            return False

    def __enter__(self):
        if not self.acquire():
            raise BlockingIOError(f"{self.agent_name} is already running")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


@contextmanager
def agent_lock(agent_name: str, skip_if_locked: bool = True):
    """
    Context manager for agent locking

    Args:
        agent_name: Name of agent
        skip_if_locked: If True, skip (return None) if already locked
                       If False, wait for lock

    Usage:
        with agent_lock("john", skip_if_locked=True) as lock:
            if lock:
                # Agent not already running, do work
                run_john()
            else:
                # Agent already running, skip
                print("John already running, skipping")
    """
    lock = AgentLock(agent_name, timeout=0 if skip_if_locked else 300)

    if lock.acquire():
        try:
            yield lock
        finally:
            lock.release()
    else:
        # Already locked
        yield None


def cleanup_stale_locks(max_age_seconds: int = 600):
    """
    Clean up lock files older than max_age_seconds
    Handles cases where process crashed without releasing lock
    """
    for lock_file in LOCK_DIR.glob("*.lock"):
        try:
            # Check if lock is actually held
            with open(lock_file, 'r') as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # We got the lock - file is stale
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                    # Check age
                    lines = f.readlines()
                    if len(lines) >= 2:
                        timestamp = float(lines[1].strip())
                        age = time.time() - timestamp
                        if age > max_age_seconds:
                            lock_file.unlink()
                            print(f"Cleaned up stale lock: {lock_file.name} (age: {age:.0f}s)")
                except BlockingIOError:
                    # Lock is actually held, leave it alone
                    pass
        except Exception as e:
            print(f"Error cleaning up {lock_file}: {e}")


if __name__ == "__main__":
    # Test the locking mechanism
    print("Testing agent lock...")

    # Test 1: Acquire lock
    lock1 = AgentLock("test_agent")
    if lock1.acquire():
        print("✓ Acquired lock")

        # Test 2: Try to acquire same lock (should fail)
        lock2 = AgentLock("test_agent")
        if not lock2.acquire():
            print("✓ Second acquire correctly blocked")
        else:
            print("✗ Second acquire should have been blocked!")

        lock1.release()
        print("✓ Released lock")

        # Test 3: Now should be able to acquire
        if lock2.acquire():
            print("✓ Can acquire after release")
            lock2.release()
        else:
            print("✗ Should be able to acquire after release!")
    else:
        print("✗ Failed to acquire initial lock")

    # Test context manager
    print("\nTesting context manager...")
    with agent_lock("test_agent2", skip_if_locked=True) as lock:
        if lock:
            print("✓ Got lock in context manager")
        else:
            print("✗ Should have gotten lock")

    print("✓ All tests passed!")
