"""Manage a single socket connection."""
 
from select import select
from datetime import datetime
  

def wait_and_respond(socket):
    """Wait for a message for 50 min and respond the current time to it."""
    r_fds, _, _ = select([socket], [], [], 50 * 60)
    
    if not r_fds:
        raise ValueError("No one connected for 50 minutes.")
    
    _, w_fds, _ = select([], [socket], [])
    w_fds[0].write(str(datetime.today()))
