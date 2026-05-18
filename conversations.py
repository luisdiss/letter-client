from pathlib import Path
from datetime import datetime
import json
import requests as rq
import sys
from bidict import bidict

def select_func(func):
    def wrapper(self, *args, **kwargs):
        if self.state.selected_username: 
            func(self, *args, **kwargs)
        else:
            print("no user selected")
    return wrapper

class Message:
    def __init__(self, conversation_id: int, author: str, sent_at: int, content: str, expiration: int):
        self.conversation_id: int = conversation_id
        self.author: str = author
        self.sent_at: int = sent_at
        self.content: str = content
        self.expiration: int = expiration
    
    def __repr__(self,):
        return f"{self.author} {datetime.fromtimestamp(self.sent_at)}\n{self.content}"
    
    @classmethod
    def deserialise(self, d):
        return Message(**d)

class Conversation:
    def __init__(self, name: str, id: int, messages: list[Message] = []):
        self.name = name
        self.id = id
        self.messages = messages
    
    @classmethod
    def deserialise(self, d):
        if 'name' in d and 'id' in d and 'messages' in d:
            messages = [Message.deserialise(m) for m in d["messages"]]
            d["messages"] = messages
            return Conversation(**d)
        return d

class Conversations:
    def __init__(self, state):
        self.state = state
        self.messages_path: Path = Path("messages.txt")
        self.name_path = Path("names.txt")
        self.name_to_conversation_id: bidict[str, int] = self._load_name_to_conversation_id()
        self.conversation_id_to_conversation:  dict[int, Conversation] = self._load_conversation_id_to_conversation()

    def _load_name_to_conversation_id(self) -> bidict[str, int]:
        names = {}
        try:
            with open(self.name_path, "r") as file:
                names = json.load(file)
        except FileNotFoundError:
            with open(self.name_path, "w") as file:
                file.write("{}")
        except PermissionError:
            print(f"permission error: could not load names at location: {self.name_path}")
            sys.exit()
        except Exception as e:
            print(f"an error occurred while reading the file: {e}")
            sys.exit()
        
        return bidict(names)
    
    def _save_name_to_conversation_id(self):
        try:
            with open(self.name_path, "w") as file:
                json.dump(dict(self.name_to_conversation_id), file)
        except FileNotFoundError:
            print("file not found error: could not save conversation_ids at location: {self.name_path}")
        except PermissionError:
            print(f"permission error: could not save conversation_ids at location: {self.name_path}")
        except Exception as e:
            print(f"an error occurred while reading the file: {e}")

    
    def _load_conversation_id_to_conversation(self) -> dict[int, Conversation]:
        conversations: dict[int, Conversation] = {}

        try:
            with open(self.messages_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg_data = json.loads(line)
                        conversation_id = msg_data['conversation_id']
                        message = Message(**msg_data)
                        
                        if conversation_id in conversations:
                            conversations[conversation_id].messages.append(message)
                        else:
                            name = self.name_to_conversation_id.inverse[conversation_id]
                            conversations[conversation_id] = Conversation(name = name, id = conversation_id, messages=[message])
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"parsing error: could not parse line: {line}. error: {e}")
                        continue
                        
        except FileNotFoundError:
            with open(self.messages_path, 'w') as file:
                pass
        except PermissionError:
            print(f"permission error: could not load messages at location: {self.messages_path}")
            sys.exit()
        except Exception as e:
            print(f"an error occurred while reading the file: {e}")
            sys.exit()

        return conversations
        
    def sync_messages(self) -> None:
        messages_contents = self._get_messages(self.state.settings["server_url"])
        messages = [Message(**message_content) for message_content in messages_contents]
        messages.sort(key=lambda message: message.sent_at)
        self._append_and_save_messages(messages)

    def _get_messages(self, server_url: str) -> list:
        headers  = {
            "Authorization": f"Token {self.state.auth_token}",
        }
        resp = rq.get(server_url + "/messages", headers=headers)
        
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            print("not authorised. please login")
        else:
            print(f"could not contact the server. status code {resp.status_code}") 
        return []
    
    def _append_and_save_messages(self, messages: list[Message]) -> bool:
        for message in messages:
            conversation_id = message.conversation_id

            if conversation_id not in self.name_to_conversation_id.inverse:
                #it must be a message. group chat ids would be saved because they require manual joining
                self._add_conversation_id(message.author, conversation_id)

            conversation = self.conversation_id_to_conversation.get(conversation_id)
            if not conversation:
                self._add_conversation(self.name_to_conversation_id.inverse[conversation_id], conversation_id)
                conversation = self.conversation_id_to_conversation[conversation_id]
            
            conversation.messages.append(message)
        try:
            with open(self.messages_path, "a") as file:
                for message in messages: 
                    file.write(json.dumps(message, default=lambda o: o.__dict__) + "\n")
            return True
        except FileNotFoundError:
            print(f"file not found error: could not save messages at location: {self.messages_path}")
            return False
        except PermissionError:
            print(f"permission error: could not save messages at location: {self.messages_path}")
            return False
    
    @select_func
    def send_message(self, msg_text:list[str]) -> None:
        username = self.state.selected_username
        conversation_id = self.name_to_conversation_id.get(username)
        sent_at = int(datetime.now().timestamp())
        expiration = self.state.settings["expiration"]
        content = ' '.join(msg_text)

        data = {
            "conversation_id":conversation_id,
            "recipient_username":username,
            "content":content,
            "sent_at":sent_at,
            "expiration":expiration
        }
        headers  = {"Authorization": f"Token {self.state.auth_token}"}
        resp = rq.post(self.state.settings["server_url"] + "/messages", json=data, headers=headers)

        if resp.status_code == 200:
            if conversation_id == None:
                conversation_id = resp.json()["conversation_id"]
                self._add_conversation_id(username, conversation_id)
            else: 
                conversation_id = self.name_to_conversation_id[username]


            message = Message(
                conversation_id = conversation_id,              
                author = username,
                content = content,
                sent_at = sent_at,
                expiration = expiration
            )  
            self._append_and_save_messages([message])
        elif resp.status_code == 401:
            print(f"not authorised: please login")
        elif resp.status_code == 404:
            print(f"user does not exist")
        else:
            print("message not sent: could not contact the server")
    
    def _add_conversation_id(self, name: str, conversation_id: int) -> None:
        self.name_to_conversation_id[name] = conversation_id
    
    def _add_conversation(self, name: str, id: int) -> None:
        conversation = Conversation(name=name, id=id)
        self.conversation_id_to_conversation[id] = conversation

    #add lazy loading when gui
    @select_func
    def messages(self, count: int) -> None:
        username = self.state.selected_username
        if (conv_id := self.name_to_conversation_id.get(username)) != None:
            if (conversation := self.conversation_id_to_conversation.get(conv_id)) != None:
                messages = conversation.messages
                count = min(count, len(messages))
                for message in messages[-count:]: print(message)
                return

        print(f"no messages with {username}")