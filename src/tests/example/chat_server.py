# Socket server in python using select function
 
import socket
import functools
from select import select


class ChatServer(object):
    """Manage chat registration and messages."""
    
    clients_list = []    # list of socket clients
    outgoing_messages = {} 
    
    @staticmethod
    def _chat_callback(socket):
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
        if socket not in ChatServer.clients_list:
            # Client was removed.
            return
        
        msg = ChatServer.outgoing_messages[socket].pop()
        
        if not ChatServer.outgoing_messages[socket]:
            ChatServer.outgoing_messages.pop(socket)
        
        socket.send(msg)
            
    
    class RegisterSocket(socket.socket):
        """Callback socket for registration"""
        
        def callback(self):
            sockfd, addr = self.accept()            
            ChatServer.clients_list.append(sockfd)
            sockfd._chat_callback = functools.partial(
                ChatServer._chat_callback,
                sockfd)
            sockfd._chat_send_callback = functools.partial(
                ChatServer._chat_send_callback,
                sockfd)
            
            
    def main_loop(self, server_socket):
        recv_sockets = self.clients_list + [server_socket]
        send_socket = self.outgoing_messages.keys()
        r_fds, w_fds, _ = select(recv_sockets, send_socket, [])
        
        for fd in r_fds:
            fd._chat_callback()
            
        for fd in w_fds:
            fd._chat_send_callback() 
            
    def run(self):
        PORT = 5000
             
        server_socket = RegisterSocket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(10)
        
        while True:
            main_loop(server_socket)
            
        server_socket.close()
        
