"""Socket server in python using select function."""
 
import socket
import functools
from select import select


class ChatServer(object):
    """Manage chat registration and messages."""
    
    clients_list = []    # list of socket clients
    outgoing_messages = {} 
    
    @staticmethod
    def _chat_callback(socket):
        """Recieve message from client and send to the others."""
        message = socket.recv()
        
        if not message:
            # Hangup
            ChatServer.clients_list.remove(socket)
            ChatServer.outgoing_messages.pop(socket)
            socket.close()
            return
        
        for client in ChatServer.clients_list:
            if client == socket:
                continue
            
            ChatServer.clients_list.get(client, []).append(message)
       
    @staticmethod     
    def _chat_send_callback(socket):
        """Send a message to a client."""
        if socket not in ChatServer.clients_list:
            # Client was removed.
            return
        
        msg = ChatServer.outgoing_messages[socket].pop()
        
        if not ChatServer.outgoing_messages[socket]:
            ChatServer.outgoing_messages.pop(socket)
        
        socket.send(msg)
            
    class RegisterSocket(socket.socket):
        """Callback socket for registration."""
        
        def _chat_callback(self):
            """Register a new cclient."""
            sockfd, addr = self.accept()            
            ChatServer.clients_list.append(sockfd)
            sockfd._chat_callback = functools.partial(
                ChatServer._chat_callback,
                sockfd)
            sockfd._chat_send_callback = functools.partial(
                ChatServer._chat_send_callback,
                sockfd)
            
    def run(self):
        """Run the chat server."""
        PORT = 5000
             
        server_socket = RegisterSocket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(10)
        
        # Recieve the first client.
        server_socket._chat_callback()
        
        while self.clients_list:
            recv_sockets = self.clients_list + [server_socket]
            send_socket = self.outgoing_messages.keys()
            r_fds, w_fds, _ = select(recv_sockets, send_socket, [])
            
            for fd in r_fds:
                fd._chat_callback()
                
            for fd in w_fds:
                fd._chat_send_callback() 
            
        server_socket.close()
