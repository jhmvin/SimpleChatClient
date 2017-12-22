from socket import *
import sys
import threading
from time import sleep
import atexit
import json
from _codecs import register

class MonoServer():

    def __init__(self):
        self.MAX_USERS = 4
        #-------------------- init --------------
        self.HOST = '' # all host are accepted if empty
        self.PORT = 2224 # connection socket
        self.mono_socket = socket(AF_INET, SOCK_STREAM) #protocol implementation
        self.mono_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # socket recycler
        self.mono_socket.bind((self.HOST, self.PORT)) # apply all settings
        self.mono_socket.listen(100) # connection limit
        
        #------------------ sys ----------------
        self.client_counter = 0
        self.client_list = []
        atexit.register(self.exit_handler)
        pass
    
    def exit_handler(self):
        try:
            self.mono_socket.close()
            print "Sockets Closed"
        except Exception as e:
            print e
            print "Sockets are already Closed"
            pass
        pass # handler end
    
    def connection_daemon(self):
        
        x = 1
        #definition: it waits for incomming connection
        while x==1:
            
            try:
                print "Waiting for Connection . . ."
                (conn, addr) = self.mono_socket.accept() # checks if there is a incomming connection
                print "Client: ", addr ,"connected."
                con_info = {'con':conn, 'ip':addr} # saves it to a dictionary
            except Exception as  e:
                print "CONNECTION DAEMON:" +  str(e)
                x = 0;
                print "connection is already closed"
                pass
            threading._start_new_thread(self.client_daemon,(conn,addr))
            pass #end of while
        pass
    
    ''' CLIENT DAEMON '''
    
   
    def client_daemon(self,conn,addr):
        # main processes are found here
        x = 1
        while x==1:
            try:
                
                #no error block
                data = conn.recv(131072)
                format_json = json.loads(data)
                
                if format_json['type'] == 'LOGIN':
                    response_json = self.login(format_json['username'], format_json['password'],addr)
                    conn.sendto(response_json,addr)
                    print self.client_counter
                    pass
                elif format_json['type'] == 'REGISTER':
                    response_json =  self.register(format_json['username'],format_json['password'])
                    conn.sendto(response_json,addr)
                    pass
                elif format_json['type'] == 'BROADCAST':
                    response_json = self.send_broadcast(format_json['sender'],format_json['content'],format_json['send_date'])
                    conn.sendto(response_json,addr)
                    pass
                elif format_json['type'] == 'FETCH_BROADCAST':
                    response_json = self.fetch_broadcast()
                    conn.sendto(response_json,addr)
                    pass
                elif format_json['type'] == 'FETCH_CLIENTS':
                    response_json = self.fetch_client_list()
                    conn.sendto(response_json,addr)
                    pass
                elif format_json['type'] == 'PRIVATE':
                    response_json = self.private(format_json['from'],format_json['to'],format_json['message'],format_json['send_date'])
                    conn.sendto(response_json,addr)
                elif format_json['type'] == 'FETCH_PRIVATE':
                    response_json = self.fetch_private()
                    conn.sendto(response_json,addr)
                    pass
                elif format_json['type'] == 'CHANGE_PASS':
                    response_json = self.change_password(format_json['user'],format_json['old_pass'],format_json['new_pass'])
                    conn.sendto(response_json,addr)
                    pass
                
                
            except Exception as e:
                print "ERROR IN DAEMON: " + str(e)
                error_code = str(e)
                if(error_code == "[Errno 10054] An existing connection was forcibly closed by the remote host"):
                    print addr, "Client is closed"
                    
                    ############# REMOVE FROM CLIENT LIST
                    x = 0
                    for client in self.client_list:
                        if(client['address'] == addr):
                            client_info = {}
                            client_info['address'] = ""
                            client_info['username'] = "username"
                            self.client_list[x] = client_info
                            pass
                        
                        x+=1
                        pass
                    #############
                    self.client_counter-=1
                    
                    x = 0
                    return
                    pass
                else:
                    print e
                pass #end except
            #print str(addr) + ": " + str(format_json['content'])
            if data == "":
                x = 0
                conn.close()
                print addr, " disconnected"
                pass
            sleep(0.143)
        pass # end of client daemon
    ''' END OF CLIENT DAEMON '''
   
   
    ''' CLIENT OPERATIONS BLOCKING'''
   
    def change_password(self,user_l,old,new):
        # get the values from client
        account = {}
        account['username'] = user_l
        account['password'] = old
        
        # get values from database
        accounts = open('accounts.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        
        # now check existence
        response = {}
        counter = 0
        for user in records:
            user_json = json.loads(user.strip()) # converts string to json format
            if(user_json['username'] == account['username']):
                # initialize headers
                response = {}
                response['type'] = "LOGIN"
                if(user_json['password'] == account['password']):
                    response['result'] = "1" # for success 
                    #----------------------------------------------
                    accounts = open('accounts.txt','w')
                    records.pop(counter)
                    #--------------- Change Here
                    new_account = {}
                    new_account['username'] = user_l
                    new_account['password'] = new
                    json_new = json.dumps(new_account, ensure_ascii=False).encode('utf-8') + "\n"
                    records.append(json_new)
                    #----------------
                    accounts.writelines(records)
                    accounts.close()
                    break
                    #----------------------------------------------            
                    pass
                else:
                    response['result'] = "-1" # for failed
                    pass
                response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
                return response_json #if exists return -1
                pass
            counter+=1
            pass # end of for loop
        
        response['type'] = "CHANGE_PASS"
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        return response_json
        pass
   
    def fetch_private(self):
        accounts = open('private.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        json_lib = {}
        json_lib['type'] = 'FETCH_PRIVATE'
        x=0
        for lisdne in records:
            json_lib[x] = lisdne.strip()
            x+=1    
        response_json = json.dumps(json_lib, ensure_ascii=False).encode('utf-8')
        #print response_json
        
        return response_json
        pass # end fetch
   
    def private(self,_from,to,_message,send_date):
        message = {}
        message['from'] = _from
        message['to'] = to
        message['message'] = _message
        message['send_date'] = send_date
        print message
        message_json = json.dumps(message, ensure_ascii=False).encode('utf-8') + '\n'
        messages = open('private.txt','a')
        messages.write(message_json)
        messages.close()
        
        response = {}
        response['type'] = "PRIVATE"
        response['result'] = "1"
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        return response_json
        pass
   
    def isOnline(self,user):
        client_count = len(self.client_list)
        x = 0
        state = "offline"
        while(x < client_count):
            iteratable = self.client_list[x]
            if(iteratable['username'] == user):
                state = "online"
                break
                pass
            x+=1
        return state
        pass
   
    def fetch_client_list(self):
        # get values from database
        accounts = open('accounts.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        
        user_list = {}
        user_list['type'] = "FETCH_CLIENTS"
        
        x = 0
        # now check existence
        for user in records:
            user_info = {}
            user_json = json.loads(user.strip()) # converts string to json format 
            user_info['username'] = user_json['username']
            user_info['state'] = self.isOnline(user_json['username'])
            
            user_list[x] = user_info
            
            x+=1
        #print user_list
        response_json = json.dumps(user_list, ensure_ascii=False).encode('utf-8')
        #print response_json
        
        return response_json
            
        pass # end func
   
    def send_broadcast(self,sender,content,send_date):
        message = {}
        message['sender'] = sender
        message['content'] = content
        message['send_date'] = send_date
        message_json = json.dumps(message, ensure_ascii=False).encode('utf-8') + '\n'
        messages = open('messages.txt','a')
        messages.write(message_json)
        messages.close()
        
        response = {}
        response['type'] = "BROADCAST"
        response['result'] = "1"
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        return response_json
        pass # end of send
    
    def fetch_broadcast(self):
        accounts = open('messages.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        json_lib = {}
        json_lib['type'] = 'FETCH_BROADCAST'
        x=0
        for lisdne in records:
            json_lib[x] = lisdne.strip()
            x+=1    
        response_json = json.dumps(json_lib, ensure_ascii=False).encode('utf-8')
        #print response_json
        
        return response_json
        pass # end fetch
    
    def register(self,username,password):
        ''' FLAGS 1 for success and -1 for existing '''
        # get the values from client
        account = {}
        account['username'] = username
        account['password'] = password
        
        # get values from database
        accounts = open('accounts.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        # now check existence
        for user in records:
            user_json = json.loads(user.strip()) # converts string to json format
            if(user_json['username'] == account['username']):
                response = {}
                response['type'] = "REGISTER"
                response['result'] = "-1"
                response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
                return response_json #if exists return -1
                pass
            pass
        
        # if not exist append the registration to existing users
        account_json = json.dumps(account, ensure_ascii=False).encode('utf-8') + '\n'
        records.append(account_json)
        
        # open file database and write it
        accounts = open('accounts.txt','w')
        accounts.writelines(records)
        accounts.close()
        
        # return the response to the client
        response = {}
        response['type'] = "REGISTER"
        response['result'] = "1"
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        return response_json
        pass #end of registration
    ''' END OF REGISTRATION'''
   
    def login(self,username,password,addr):
        # get the values from client
        account = {}
        account['username'] = username
        account['password'] = password
        
        # get values from database
        accounts = open('accounts.txt','r')
        records = accounts.readlines()
        accounts.close()
        records = filter(None,records) #this will remove whitespaces
        
        # now check existence
        for user in records:
            user_json = json.loads(user.strip()) # converts string to json format
            if(user_json['username'] == account['username']):
                # initialize headers
                response = {}
                response['type'] = "LOGIN"
                if(user_json['password'] == account['password']):
                    response['result'] = "1" # for success
                    if(self.isOnline(user_json['username']) == "online"):
                        response['result'] = "2" # for already login
                        pass
                    elif(self.client_counter >= self.MAX_USERS):
                        response['result'] = "3" # MAX CLIENTS REACHED
                        pass
                    else:
                    
                        #---------------------
                        client_info = {}
                        client_info['address'] = addr
                        client_info['username'] = username
                        self.client_list.append(client_info)
                        self.client_counter+=1
                        print self.client_list
                        #---------------------
                    
                    pass
                else:
                    response['result'] = "-1" # for failed
                    pass
                response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
                return response_json #if exists return -1
                pass
            pass # end of for loop
        
        response = {}
        response['type'] = "LOGIN"
        response['result'] = "0" # for account not existing
        
        
        # send the reply to the client        
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        return response_json
        pass # end of login
    
    pass #end of MonoServer

server = MonoServer()
server.connection_daemon()


