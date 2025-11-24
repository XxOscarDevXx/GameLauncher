import customtkinter as ctk
from chat_client import ChatClient
import threading

class ChatWindow(ctk.CTkToplevel):
    def __init__(self, parent, client, friend_name):
        super().__init__(parent)
        self.client = client
        self.friend_name = friend_name
        self.title(f"Chat - {friend_name}")
        self.geometry("400x500")
        
        self.chat_area = ctk.CTkTextbox(self, state="disabled")
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.msg_entry = ctk.CTkEntry(self.input_frame)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_msg)
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=60, command=self.send_msg)
        self.send_btn.pack(side="right")
        
    def send_msg(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            self.client.send_message(self.friend_name, msg)
            self.add_message("Me", msg)
            self.msg_entry.delete(0, "end")
            
    def add_message(self, sender, content):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"{sender}: {content}\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

class FriendsPanel(ctk.CTkFrame):
    def __init__(self, master, client, **kwargs):
        super().__init__(master, **kwargs)
        self.client = client
        self.friends = [] # [{username, status, game}]
        self.requests = []
        
        # Header
        self.header = ctk.CTkLabel(self, text="Friends", font=("Roboto", 16, "bold"))
        self.header.pack(pady=10)
        
        # Add Friend
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.pack(fill="x", padx=5)
        self.add_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Username", height=25)
        self.add_entry.pack(side="left", fill="x", expand=True)
        self.add_btn = ctk.CTkButton(self.add_frame, text="+", width=25, height=25, command=self.add_friend)
        self.add_btn.pack(side="right", padx=2)
        
        # Requests Button
        self.req_btn = ctk.CTkButton(self, text="Requests (0)", fg_color="transparent", border_width=1, height=25, command=self.show_requests)
        self.req_btn.pack(fill="x", padx=5, pady=5)
        
        # List
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)
        
        self.chat_windows = {} # {friend_name: window}

    def update_data(self, friends, requests):
        self.friends = friends
        self.requests = requests
        self.req_btn.configure(text=f"Requests ({len(requests)})")
        self.refresh_list()

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
            
        for friend in self.friends:
            f_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            f_frame.pack(fill="x", pady=2)
            
            # Status Dot
            color = "green" if friend["status"] == "Online" else "gray"
            dot = ctk.CTkLabel(f_frame, text="●", text_color=color, font=("Arial", 16))
            dot.pack(side="left", padx=2)
            
            # Name & Game
            text = friend["username"]
            if friend["game"]:
                text += f"\nPlaying {friend['game']}"
            
            lbl = ctk.CTkButton(f_frame, text=text, fg_color="transparent", anchor="w", command=lambda f=friend["username"]: self.open_chat(f))
            lbl.pack(side="left", fill="x", expand=True)

    def add_friend(self):
        username = self.add_entry.get()
        if username:
            self.client.send_friend_request(username)
            self.add_entry.delete(0, "end")

    def show_requests(self):
        if not self.requests:
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Friend Requests")
        dialog.geometry("300x400")
        
        for req in self.requests:
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(frame, text=req).pack(side="left", padx=10)
            ctk.CTkButton(frame, text="Accept", width=60, command=lambda r=req, d=dialog: self.accept(r, d)).pack(side="right", padx=5)

    def accept(self, requester, dialog):
        self.client.accept_friend_request(requester)
        
        # Add to my list immediately
        if not any(f["username"] == requester for f in self.friends):
            self.friends.append({"username": requester, "status": "Online", "game": None})
            self.refresh_list()
            
        # Remove from requests
        if requester in self.requests:
            self.requests.remove(requester)
            self.req_btn.configure(text=f"Requests ({len(self.requests)})")
            
        dialog.destroy()

    def open_chat(self, friend_name):
        if friend_name in self.chat_windows and self.chat_windows[friend_name].winfo_exists():
            self.chat_windows[friend_name].focus()
        else:
            self.chat_windows[friend_name] = ChatWindow(self, self.client, friend_name)

    def receive_msg(self, sender, content):
        if sender not in self.chat_windows or not self.chat_windows[sender].winfo_exists():
            self.open_chat(sender)
        self.chat_windows[sender].add_message(sender, content)
