#****************************
#*         IMPORTS          *
#****************************
from Tkinter import *
import tkMessageBox
from socket import*
import threading
import json
from time import sleep
import unicodedata
from pip.cmdoptions import editable
try:
    import tkinter.ttk as ttk
except ImportError:
    import Tkinter as tk
    import ttk
    
import atexit
import sys
'''
    CLASS DECLARATIONS
    --------------------------------------
'''

'''
    TIME ZONE MANAGER
    --------------------------------------
    
'''
from datetime import datetime,tzinfo,timedelta

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name
    pass #end of zone

#EST = Zone(-5,False,'EST')

#print datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S %Z')
'''
GMT = Zone(8,False,'GMT')
print datetime.now(GMT).strftime('%m/%d/%Y %I:%M:%S %p')
'''
#print datetime.now(EST).strftime('%m/%d/%Y %H:%M:%S %Z')

#t = datetime.strptime('2011-01-21 02:37:21','%Y-%m-%d %H:%M:%S')
#t = t.replace(tzinfo=GMT)
#print t
#print t.astimezone(EST)


'''
    MONOCLIENT SERVER CONNECTIVITY
    --------------------------------------
'''


class MonoClient():
    def __init__(self):
        #self.mime_result = {'type':'null','result':'null'}
        self.HOST = '127.0.0.1' #'192.168.15.4'
        self.PORT = 2224
        try:
            self.mono_socket = socket(AF_INET, SOCK_STREAM)
            self.mono_socket.connect((self.HOST,self.PORT))
        except:
            self.showInfoMsg("Server Information","Server is unreachable. Please try again.")
            print "Server is unreachable"
            pass
        
        #self.graph = GUI()
        pass #end of construct
    
    def send_request(self,request):
        try:        
            data_json = json.dumps(request, ensure_ascii=False).encode('utf-8')
            self.mono_socket.send(data_json)
            return self.mono_socket.recv(131072)
        except Exception as e:
            print e
            return "-143" # cannot reach the server
        pass # end request
    

    
    pass # end of class
   
#****************************
#*          MAIN            *
#****************************
''' CLASS GUI
---------------------------------------------------------------

'''
class GUI():
    def __init__(self):
        self.client = MonoClient()
        self.broadcast_reciever = threading.Thread(target=self.fetch_broadcast)
        self.client_lister = threading.Thread(target=self.fetch_clients)
        self.graphics_render = threading.Thread(target=self.showLoginForm)
        self.messenger = threading.Thread(target=self.fetch_messages)
        self.private_records = []
        print "BROADCAST SET"
        self.auth_user = "USER"
        self.GMT = Zone(8,False,'GMT') # +8 GMT ASIA TAIPEI
        print datetime.now(self.GMT).strftime('%m/%d/%Y %I:%M:%S %p')
        
        self.fetch_message_block = 1
        
        # infinite loop all codes below will not be called
        #self.showLoginForm()
        self.graphics_render.start()
        
        
        #self.rcv_brod = 0
        #self.broadcast_reciever.start()
       

        pass # end init
    
    
    def showErrorMsg(self,title,message):
        window = Tk()
        window.wm_withdraw()
        window.geometry("3x2+200+200")
        tkMessageBox.showerror(title=title,message=message,parent=window)

    def showInfoMsg(self,title,msg):
        window = Tk()
        window.wm_withdraw()
        window.geometry("3x2+"+str(window.winfo_screenwidth()/2)+"+"+str(window.winfo_screenheight()/2))
        tkMessageBox.showinfo(title=title, message=msg)

    def authenticate(self):
        request = {}
    
        request['type'] = 'LOGIN'
        
        global text_font
        text_font = ('Calibri', '12')
        request['username'] = self.txt_user.get()
        request['password'] = self.txt_password.get()
        data = self.client.send_request(request)
        response = json.loads(data)
        res = response['result']
        if(res == "0"):
            self.showErrorMsg("Account Error","Account not found.")
            print "Account Not Existing"
        elif(res == "-1"):
            self.showErrorMsg("Account Error","Incorrect password.")
            print "Wrong Password"
        elif(res == "2"):
            self.showInfoMsg("Account Information","Account is already online. Please use another account.")
            print "Account is already online"
        elif(res == "3"):
            self.showErrorMsg("Account Error","Maximum client reached. Try again later.")
            print "MAX CLIENT REACHED"
        elif(res == "1"):
            self.showInfoMsg("Account Information","Successfully Logged in!")
            print "Login Success"
            self.auth_user = self.txt_user.get()
            self.frm_login.destroy()
            self.rcv_brod = 1
            self.showMainForm()
            
        else:
            self.showErrorMsg("Unknown Error","An error occured. Try again.")
            print "An Error Occured"

        pass






   
    def register(self):
        
        request = {}
        request['type'] = 'REGISTER'
        request['username'] = self.reg_username.get()
        request['password'] = self.reg_password.get()
        data = self.client.send_request(request)
        response = json.loads(data)
        res = response['result']
        if(res == "-1"):
            self.showInfoMsg("Account Information","Account already exists.")
            print "Account Already Exists"
        elif(res == "1"):
            self.showInfoMsg("Account Information","Account created.")
            print "Account Created"
            self.frm_register.destroy()
            self.showLoginForm()
        else:
            self.showErrorMsg("Unknown Error","An error occured. Try again.")
            print "An Error Occured"
            self.frm_register.destroy()

        pass

    def verifyPass(self):
        username = self.reg_username.get()
        passwrd = self.reg_password.get()
        reenter = self.reg_confirm.get()
        if(username==""):
            self.showInfoMsg("Account Information","Please enter your username.")
        elif(passwrd==""):
            self.showInfoMsg("Account Information","Please enter your password.")
        elif(reenter==""):
            self.showInfoMsg("Account Information","Please re-enter your password.")
        elif(passwrd==reenter):
            self.fromRegToLogin()
        else:
            self.showErrorMsg("Account Error","Password not matched.")
        pass


    def broadcast(self,event):
        msg =  self.msgBox.get("1.0",END)
        print "msg here: ", msg
        bad_words = ['fuck', 'bitch', 'shit', 'damn', 'piss', 'asshole', 'slut', 'tangina', 'puta', 'gago', 'hudas', 'lintik', 'ulol', 'tarantado', 'buwisit',
                     'burat', 'kupal', 'leche', 'ungas', 'punyeta', 'hinayupak', 'pucha', 'pesteng yawa', 'pakshet', 'tanga']
        index=0
        ctr=0
        
        while 1:
            if(index==len(bad_words)):
                break
            if(bad_words[index] in msg.lower()):
                ctr=1
                break
            index+=1
                
        if ctr==1:
            self.showErrorMsg("Content Error","Please avoid bad or foul words.")
        else:
            msg_nrm = unicodedata.normalize('NFKD', msg).encode('ascii','ignore').strip() 
            request = {}
            request['type'] = 'BROADCAST'
            request['sender'] = self.auth_user
            request['content'] = msg_nrm
            request['send_date'] = datetime.now(self.GMT).strftime('%m/%d/%Y %I:%M:%S %p')
            while(1==1):
                try:
                    data = self.client.send_request(request)
                    response = json.loads(data)
                except:
                    self.showInfoMsg("Message Information","Retrying to send message.")
                    print "Retrying to send"
                    sleep(0.5)
                    continue
                    pass
                break
        
            try:
                if(response['type'] == "BROADCAST"):
                    print response
                    self.msgBox.delete("0.0",END)
            except Exception as e:
                print e
            
                #self.fetch_broadcast()
            pass # end of broadcast
    
    
    def fetch_messages(self):
        request = {}
        request['type'] = 'FETCH_PRIVATE'
        
        while self.fetch_message_block==1:
            # ok
            while 1==1:
                # ok
                try:
                    data = self.client.send_request(request)
                    response = json.loads(data)
                except Exception as e:
                    print "Retrieving Messages: ",e
                    sleep(0.5)
                    continue
                    pass
                break
                pass # end loop
            if(response['type'] == "FETCH_PRIVATE"):
                #print
                
                try:
                    self.private_records = []
                    msg_counter = 0               
                    while(msg_counter<(len(response)-1)):
                        line = response[str(msg_counter)]
                        arrange_me = json.loads(line)
                        msg_counter+=1
                        self.private_records.append(arrange_me)
                    pass
                    #print 'CHATBOX REFRESHED'
                except:
                    self.showErrorMsg("Message Error","Cannot retrieve private messages.")
                    print "CANNOT RETRIEVED PRIVATE MESSAGES"
                    break
                    pass
                pass # end of if
            sleep(2)
            pass # end of infinite loop
        pass # end fetch
    
    # this function refreshes the message box
    def fetch_broadcast(self):
        request = {}
        request['type'] = 'FETCH_BROADCAST'
        while 1==1:
            # ok
            sleep(1)
            while 1==1:
                # ok
                try:
                    data = self.client.send_request(request)
                    response = json.loads(data)
                except Exception as e:
                    print "Retrieving Messages: ",e
                    sleep(0.5)
                    continue
                    pass
                break
                pass # end loop
            if(response['type'] == "FETCH_BROADCAST"):
                #print
                msg_counter = 0
                public_message_string = ""
                #message loop
                while(msg_counter<(len(response)-1)):
                    line = response[str(msg_counter)]
                    arrange_me = json.loads(line)
                    msg_counter+=1
                    public_message_string += (arrange_me['send_date'] +" >>> [ "+arrange_me['sender'] + " ] : " +arrange_me['content'] + "\n")
                    pass # end of message loop
                try:               
                    self.publicList.configure(state='normal')
                    self.publicList.delete('1.0', END)
                    self.publicList.insert(END, public_message_string)
                    self.publicList.see(END)
                    self.publicList.configure(state='disabled')
                    #print 'CHATBOX REFRESHED'
                except:
                    self.showErrorMsg("Message Error","Cannot retrieve messages.")
                    print "CANNOT RETRIEVED MESSAGES"
                    break
                    pass
                pass # end of if
            pass # end of infinite loop
        pass # end fetch
    
    def listClick(self,evt):
        try:
            selected_index = self.clientList.curselection()
            select_string = self.clientList.get(selected_index)
            st,name = select_string.split("-")
            self.showPrivateMsgForm(name.strip())
        except:
            print "BAD INDEX at 255"
            pass
        
        pass

    def fetch_clients(self):
        request = {}
        request['type'] = 'FETCH_CLIENTS'
        while 1==1:
            # ok
            sleep(2)
            while 1==1:
                # ok
                try:
                    data = self.client.send_request(request)
                    response = json.loads(data)
                except Exception as e:
                    print "Retrieving CLIENTS: ",e
                    sleep(0.5)
                    continue
                    pass
                break
                pass # end loop
            if(response['type'] == "FETCH_CLIENTS"):
                #print
                try:
                    self.publicList.configure(state='disabled')   
                    #-0---------------Populate online client
                    user_count  = (len(response) - 1)
                    self.clientList.delete(0,END)
                    x = 0
                    while(x < user_count):
                        user_item =  response[str(x)]
                        user_state = "[ " + user_item['state'] + " ] - " + user_item['username']
                        self.clientList.insert(END,user_state)
                        x+=1
                        pass
                    
                    
                    #---------------------------------------
                    pass
                    #print 'CHATBOX REFRESHED'
                except:
                    self.showErrorMsg("Account Error","Cannot retrieve client list.")
                    print "CANNOT RETRIEVED CLIENT LIST"
                    break
                    pass
                pass # end of if
            pass # end of infinite loop
        pass # end fetch
    

    def change_pass(self,old_pass,new_pass):
        request = {}
        if(old_pass.get()==""):
            self.showInfoMsg("Acount Information", "Please enter your old password.")
            return 0
        elif(new_pass.get() == ""):
            self.showInfoMsg("Account Information", "Please enter a valid new password.")
            return 0
        elif(new_pass.get() != self.change_confirm_pass.get()):
            self.showErrorMsg("Account Error", "New password not matched.")
            return 0
        request['type'] = 'CHANGE_PASS'
        request['user'] = self.auth_user
        request['old_pass'] = old_pass.get()
        request['new_pass'] = new_pass.get()
        data = self.client.send_request(request)
        response = json.loads(data)
        res = response['result']
       
        if(res=="-1"):
            self.showErrorMsg("Acount Error","Old password not matched.")
        elif(res=="1"):
            self.showInfoMsg("Account Information", "Password sucessfully changed.")
            
        print res
        pass

    def logout(self):
        self.frm_public.destroy()
        exit()
        pass

    def change_profile(self):
        self.showInfoMsg("Application Information","No available process.")

    def change_font(self, event):
        global combo_box
        print combo_box.get()
        font = combo_box.get()
        if(font=="Arial Black"):
            self.publicList.configure(height=22)
            text_font = (font,'9')
        elif(font=="Cambria"):
            self.publicList.configure(width=70)
            self.publicList.configure(height=25)
            text_font = (font,'10')
        elif(font=="Arial"):
            self.publicList.configure(width=70)
            self.publicList.configure(height=25)
            text_font = (font,'9')
        else:
            self.publicList.configure(height=20)
            text_font = (font,'12')
        print text_font
        self.publicList.configure(font=text_font)
        self.clientList.configure(font=text_font)
        self.msgBox.configure(font=text_font)

        
        
    def btn_pm(self):
        self.showInfoMsg("Application Information","Double click the user you want to send private message.")

    #****************************************************
    #                   THEMES
    #****************************************************
    def theme1(self):
        self.frm_public.configure(background='dodgerblue2')
        print "theme1"
        pass

    def theme2(self):
        self.frm_public.configure(background='springgreen2')
        print "theme2"
        pass

    def theme3(self):
        self.frm_public.configure(background='midnight blue')
        print "theme3"
        pass

    def theme4(self):
        self.frm_public.configure(background='dark slate gray')
        print "theme4"
        pass
    
    def theme5(self):
        self.frm_public.configure(background='Coral')
        print "theme5"
        pass
    
    def default(self):
        self.frm_public.configure(background='white smoke')
        print "default"
        pass
    
    '''
    ------------------------------------------------------------------------------------------------------
        UI MODULE
    ------------------------------------------------------------------------------------------------------
    '''

    def showLoginForm(self):
        #createWindow("Login", "350x400+100+200")
        self.frm_login = Tk()
        
        self.frm_login.geometry("430x430+"+str((430/2)+(430/2))+"+"+str(430/2-70))
        self.frm_login.title("Login")
        self.frm_login.resizable(width="false", height="false")
        #self.frm_login.geometry("430x430+100+200")
        lbl1 = Label(self.frm_login, text="Login", width=10, height=3, fg="#1A4AA0", font="Calibri 19")
        lbl1.pack(side=TOP)

        usernameFrame = Frame(self.frm_login)
        usernameFrame.pack()
        lbl2 = Label(usernameFrame, text="Username:", width=10, fg="#1A4AA0", font="Calibri 14")
        lbl2.pack(side=LEFT)
        self.txt_user = Entry(usernameFrame, fg="#1A4AA0", font="Calibri 14")
        self.txt_user.pack(side=LEFT)

        passFrame = Frame(self.frm_login)
        passFrame.pack()
        lbl3 = Label(passFrame, text="Password:", width=10, height=3, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        self.txt_password = Entry(passFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.txt_password.pack(side=LEFT)

        buttonFrame = Frame(self.frm_login)
        buttonFrame.pack(side=RIGHT, padx=25)
        btnLogin = Button(buttonFrame, text="Login", height=1, width=12,
                          command=self.authenticate, fg="#F0F0F0", bg="#2A3540", font="Calibri 14")
        btnLogin.pack(pady=5)
        btnRegister = Button(buttonFrame, text="Register",
                             height=1, width=12, command=self.showRegisterForm,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 14")
        btnRegister.pack(pady=5)
        
        btnSettings = Button(buttonFrame, text="Connection Settings",
                             height=2, width=17, command=self.showConnectionForm,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 10")
        #btnSettings.pack(pady=5)
        self.frm_login.mainloop()        

    def showConnectionForm(self):
        con_set = Tk()
        con_set.title("Connection Settings")
        con_set.resizable(width="false", height="false")


        con_set.geometry("430x430+"+str((430/2)+(430/2))+"+"+str(380/2))
        
        #con_set.geometry("430x430+100+200")
        
        frm1 = Frame(con_set)
        frm1.pack(pady=15, padx=10)
        lbl2 = Label(frm1, text="Server IP:", width=8, fg="#1A4AA0", font="Calibri 14")
        lbl2.pack(side=LEFT)
        entry1 = Entry(frm1, fg="#1A4AA0", font="Calibri 14")
        entry1.pack(side=LEFT)

        frm2 = Frame(con_set)
        frm2.pack()
        lbl3 = Label(frm2, text="Port:", width=8, height=3, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        entry2 = Entry(frm2, fg="#1A4AA0", font="Calibri 14")
        entry2.pack(side=LEFT)

        buttonFrame = Frame(con_set)
        buttonFrame.pack(fill=BOTH)
        btnSubmit = Button(buttonFrame, text="Submit", height=1, width=12,
                          command=self.authenticate, fg="#F0F0F0", bg="#2A3540", font="Calibri 14")
        btnSubmit.pack(pady=5)
        
        frm3 = Frame(con_set)
        frm3.pack(fill=BOTH)
        lbl3 = Label(frm3, text="Result:", width=8, height=1, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT, padx=48)
        
        frm4 = Frame(con_set)
        frm4.pack(fill=BOTH)
        con_list = Listbox(frm4, relief=SUNKEN, width=37, height=10, font="Calibri 12")
        con_list.pack(pady=2, padx=5)

    '''
    REGISTRATION
    '''
    
    def showRegisterForm(self):
        self.frm_login.destroy() #destroy the login
        
        self.frm_register = Tk()
        self.frm_register.title("Register")
        self.frm_register.resizable(width="false", height="false")
        
        self.frm_register.geometry("430x430+"+str((430/2)+(430/2))+"+"+str(380/2))
        
        #self.frm_register.geometry("430x380+100+200")
        frmLbl = Frame(self.frm_register)
        frmLbl.pack(fill=BOTH, pady=5)
        lbl1 = Label(frmLbl, text="Registration", width=10, height=3, fg="#1A4AA0", font="Calibri 19")
        lbl1.pack(side=RIGHT, padx=25)

        usernameFrame = Frame(self.frm_register)
        usernameFrame.pack()
        lbl2 = Label(usernameFrame, text="Username:", width=15, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl2.pack(side=LEFT)
        self.reg_username = Entry(usernameFrame, fg="#1A4AA0", font="Calibri 14")
        self.reg_username.pack(side=LEFT)

        passFrame = Frame(self.frm_register)
        passFrame.pack()
        lbl3 = Label(passFrame, text="Password:", width=15, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        self.reg_password = Entry(passFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.reg_password.pack(side=LEFT)

        reTypePassFrame = Frame(self.frm_register)
        reTypePassFrame.pack()
        lbl3 = Label(reTypePassFrame, text="Retype-Password:", width=15, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        self.reg_confirm = Entry(reTypePassFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.reg_confirm.pack(side=LEFT)

        buttonFrame = Frame(self.frm_register)
        buttonFrame.pack(side=RIGHT, padx=30)
        btnRegister = Button(buttonFrame, text="Register", width=12, command=self.verifyPass,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 14")
        btnRegister.pack(pady=2)
        btnBack = Button(buttonFrame, text="Back", width=12, command=self.btnBack,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 14")
        btnBack.pack(pady=2)
        pass
    
    def btnBack(self):
        self.frm_register.destroy()
        self.showLoginForm()
        pass
    
    def fromRegToLogin(self):
        self.register()
        #self.frm_register.destroy()
        #self.showLoginForm()
        pass
        '''
    END REGISTRATION
    '''

    global text_font
    def showMainForm(self):
        
        #createWindow("Main", "1000x565+100+200")
        self.frm_public = Tk()  
        self.frm_public.title("Main")
        self.frm_public.resizable(width="false", height="false")

        self.frm_public.geometry("900x565+"+str((900/2)-200)+"+"+str(565/2-200))
        
        #self.frm_public.geometry("900x565+100+200")
        #MENU
        menu = Menu(self.frm_public)
        self.frm_public.config(menu=menu)
        subMenuFile = Menu(menu)
        menu.add_cascade(label="File", menu=subMenuFile)
        subMenuFile.add_command(label="Logout",
                                command=self.logout)
        
        subMenuEdit = Menu(menu)
        menu.add_cascade(label="Edit", menu=subMenuEdit)
        subMenuEdit.add_command(label="Change profile",
                                command=self.showChangePassForm)

        subMenuView = Menu(menu)
        menu.add_cascade(label="View", menu=subMenuView)

        subMenuView.add_command(label="Default | White Smoke",
                                command=self.default)
        
        subMenuView.add_command(label="Theme 1 | Dodger Blue",
                                command=self.theme1)

        subMenuView.add_command(label="Theme 2 | Spring Green",
                                command=self.theme2)
        
        subMenuView.add_command(label="Theme 3 | Midnight Blue",
                                command=self.theme3)
        
        subMenuView.add_command(label="Theme 4 | Dark Slate Gray",
                                command=self.theme4)
        
        subMenuView.add_command(label="Theme 5 | Coral",
                                command=self.theme5)
        
        #Public Chat Frame
            

        publicChatLogs = Frame(self.frm_public)
        publicChatLogs.pack(side=LEFT, padx=10, pady=5)
        frm1 = Frame(publicChatLogs)
        frm1.pack(fill=BOTH)
        lbl1 = Label(frm1, text="Public Chat", fg="#1A4AA0", font="Calibri 12")
        lbl1.pack(side=LEFT)

        #publicList = Listbox(publicChatLogs, relief=SUNKEN, width=50, height=18, font=text_font)
        self.publicList = Text (publicChatLogs, fg="#232C35", font=text_font, relief=GROOVE, height=20, width=50)
        #
        # create a Scrollbar and associate it with txt
        #
        
        self.publicList.pack(fill=BOTH, pady=5)
        
        
        
        frm2 = Frame(publicChatLogs)
        frm2.pack(fill=BOTH)
        global combo_box
        combo_box = ttk.Combobox(frm2, font=text_font)    # apply font to combobox
        combo_box.bind("<<ComboboxSelected>>", self.change_font)
        combo_box.pack(side=LEFT)
        combo_box['values'] = ('Arial', "Arial Black", 'Calibri', 'Cambria')

        self.msgBox = Text (publicChatLogs, fg="#232C35", font=text_font, relief=GROOVE, height=3)
        self.msgBox.pack(expand=1, fill=BOTH, pady=5)

        btnSend = Button(publicChatLogs, text="Send", height=2, width=12,
                          command=lambda: self.broadcast('<Return>'), fg="#F0F0F0", bg="#2A3540")
        btnSend.pack(side=RIGHT, pady=5)
        ############################################
        self.frm_public.bind_all('<Return>', self.broadcast)
        ############################################

        #Private Message Frame
        privateMsgFrame = Frame(self.frm_public)
        privateMsgFrame.pack(side=TOP, pady=8, padx=10)
        frm2 = Frame(privateMsgFrame)
        frm2.pack(fill=BOTH)
        lbl2 = Label(frm2, text="Connected Clients:", fg="#1A4AA0", font="Calibri 12")
        lbl2.pack(side=LEFT)
        
        #----------------------------------------------------------------------------
        self.clientList = Listbox(privateMsgFrame, relief=SUNKEN, width=45,
                             height=22, font=text_font)
        self.clientList.pack(pady=5)
        self.clientList.bind('<Double-Button-1>',self.listClick)
        
        
        btnPrivateMsg = Button(privateMsgFrame, text="Private Message",
                               height=2, width=50,# remove command
                               fg="#F0F0F0", bg="#2A3540", command=self.btn_pm)


        btnPrivateMsg.pack(pady=5)

        

        #RUN DAEMON
        self.broadcast_reciever.start()
        self.client_lister.start()
        
        
    def showPrivateMsgForm(self,reciever):
        pm = Tk()
        pm.title(reciever)
        pm.resizable(width="false", height="false")
        
        #self.pm.geometry("600x450+"+str((600/2)+(600/2+200))+"+"+str(450/2+20))
        
        pm.geometry("600x450+400+150")
        text_font = ('Calibri', '12')
        

        frm1 = Frame(pm)
        frm1.pack(fill=BOTH)
        lbl1 = Label(frm1, text="Private Chat", fg="#1A4AA0", font="Calibri 12")
        lbl1.pack(side=LEFT, padx=10, pady=5)
        
        privateList = Text (pm, fg="#232C35", font=text_font, relief=GROOVE, height=11)
        privateList.pack(fill=BOTH, padx=10, pady=5)
        
        
        frm = Frame(pm)
        frm.pack(fill=BOTH)
        combo_box = ttk.Combobox(frm, font=text_font)    # apply font to combobox
        combo_box.pack(side=LEFT, padx=10)
        combo_box['values'] = ('Arial', "Arial Black", 'Calibri', 'Cambria')
        
        msgBox = Text(pm, fg="#232C35", font=text_font, relief=GROOVE, height=3)
        
        msgBox.pack(fill=BOTH, pady=5, padx=10)
        
        # --------------------------------------------------- ERROR
        
        
        def load_messages(rec):
            x= 1
            while(x==1):
                sleep(1)
                try:
                    
                    privateList.delete("1.0", END)
                    #print "INSIDE LE:", len(self.private_records)
                    #print "THREAD STATE:", self.messenger.is_alive()
                    if(len(self.private_records) > 0):
                        temp = self.private_records
                        print "recieve"
                        for mymsg in temp:
                            
                            if((mymsg['to'] == rec and mymsg['from'] == self.auth_user) or (mymsg['to'] == self.auth_user and mymsg['from'] == rec)):
                                privateList.insert(END,mymsg['send_date'] + " >> " + mymsg['from'] + ":  " + mymsg['message'] + "\n")
                                
                            #privateList.insert(END,"Hiiii")
                    else:
                        continue
                        pass
                    #privateList.see(0)
                    #sleep(1)    
                except Exception as e:
                    
                    if(str(e) == "invalid command name \".66008448\""):
                        print "super error"
                        pass
                    elif(str(e) == "out of stack space (infinite loop?)"):
                        print "stupid error"
                        pass
                    elif(str(e) == "invalid command name \".70163552\""):
                        print "stupid error"
                        pass
                    elif(str(e) == "invalid command name \".70238896\""):
                        print "stupid error"
                        pass
                    else:
                        print "PRIVATE CLOSE" + str(e)
                        x=0
                        break
                        pass
                    
                    
                
                '''
                for each_record in self.private_records:
                    print "FROM: " + each_record['from'] + " TO: " + each_record['to'] + " MESSAGE " + each_record['message']
                    pass    
                '''
                pass
            
            
        
        message_displayer = threading.Thread(target = load_messages,args=(reciever,))
        message_displayer.start()
        
        #---------------------------------- ERROR

        
        def send_message(evt,reciever):
            
            #get message

            
            msg =  msgBox.get("1.0",END)

            print "msg here: ", msg
            bad_words = ['fuck', 'bitch', 'shit', 'damn', 'piss', 'asshole', 'slut', 'tangina', 'puta', 'gago', 'hudas', 'lintik', 'ulol', 'tarantado', 'buwisit',
                     'burat', 'kupal', 'leche', 'ungas', 'punyeta', 'hinayupak', 'pucha', 'pesteng yawa', 'pakshet', 'tanga']
            index=0
            ctr=0
        
            while 1:
                if(index==len(bad_words)):
                    break
                if(bad_words[index] in msg.lower()):
                    ctr=1
                    break
                index+=1
                
            if ctr==1:
                self.showErrorMsg("Content Error","Please avoid bad or foul words.")
            else:

                msg_nrm = unicodedata.normalize('NFKD', msg).encode('ascii','ignore').strip() 
            
            
                request = {}
                request['type'] = "PRIVATE"
                request['from'] = self.auth_user
                request['to'] = reciever
                request['message'] = msg_nrm
                request['send_date'] = datetime.now(self.GMT).strftime('%m/%d/%Y %I:%M:%S %p')
                print request
                #retru if no response was recieve
                x=1
            
                while(x==1):
                    try:
                        data = self.client.send_request(request)
                        response = json.loads(data)
                    except:
                        self.showInfoMsg("Message Information","Retrying to send message.")
                        print "Retrying to send"
                        sleep(0.5)
                        continue
                        pass
                    x=0
                    break
                if(response['type'] == "PRIVATE"):
                    print response
                    pass
                msgBox.delete("1.0", END)
                pass
        
        btnSend = Button(pm, text="Send", height=2, width=12,
                          command=lambda: send_message('<Return>',reciever), fg="#F0F0F0", bg="#2A3540")
        btnSend.pack(side=RIGHT, pady=5, padx=10)
        
        

        #use lambda event to bind function with parameters
        ############################################
        pm.bind_all('<Return>',lambda event: send_message('<Return>',reciever))
        
        ############################################

        if(self.messenger.is_alive()):
            print "ALREADY LIVE"
            pass
        else:
            self.fetch_message_block = 1
            self.messenger.start()
            print "THREAD STARTED"
            
            pass
        pass

    

    def showChangePassForm(self):
        cp = Tk()
        cp.title("Change Profile")
        cp.geometry("500x320+400+150")
        text_font = ('Calibri', '12')
        frme1 = Frame(cp)
        frme1.pack(fill=BOTH)
        
        lbel1 = Label(frme1, text="Change Password", font="Calibri 22", fg="#1A4AA0")
        lbel1.pack(side=LEFT, padx=10, pady=5)

        usernameFrame = Frame(cp)
        usernameFrame.pack()
        lbl2 = Label(usernameFrame, text="Old Password:", width=15, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl2.pack(side=LEFT)
        self.change_old_pass = Entry(usernameFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.change_old_pass.pack(side=LEFT)

        passFrame = Frame(cp)
        passFrame.pack()
        lbl3 = Label(passFrame, text="New Password:", width=15, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        self.change_new_pass = Entry(passFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.change_new_pass.pack(side=LEFT)

        reTypePassFrame = Frame(cp)
        reTypePassFrame.pack()
        lbl3 = Label(reTypePassFrame, text="Retype-New Password:", width=20, height=2, fg="#1A4AA0", font="Calibri 14")
        lbl3.pack(side=LEFT)
        self.change_confirm_pass = Entry(reTypePassFrame, show="*", fg="#1A4AA0", font="Calibri 14")
        self.change_confirm_pass.pack(side=LEFT)

        buttonFrame = Frame(cp)
        buttonFrame.pack(side=RIGHT, padx=30)
        btnSave = Button(buttonFrame, text="Save changes", width=12,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 14",command=lambda: self.change_pass(self.change_old_pass, self.change_new_pass))
        btnSave.pack(pady=2)
        btnBack = Button(buttonFrame, text="Back", width=12,
                             fg="#F0F0F0", bg="#2A3540", font="Calibri 14",)
        #btnBack.pack(pady=2)
        
    


    pass # end of class GUI
GUI()
