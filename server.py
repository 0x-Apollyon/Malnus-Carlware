
import json
import os
import requests
import time
import random
import threading

with open("config.json" , "r") as f:
    configs = f.read()
    configs = json.loads(configs)

server_api_token = configs["server_api_key"]
server_username = configs["server_username"]
client_username = configs["client_username"]

auth_header = {
    "Authorization":f"Bearer {server_api_token}"
}

server_initialize_moves = ["h7h5" , "g7g5" , "f7f5" , "e7e5" , "d7d5" , "c7c5" , "b7b5" , "a7a5" , "d5c4" , "d8d5" , "g5f4" , "c8f5" , "a8a7" , "h8h6" , "h6a6"]
initialize_threshold = len(server_initialize_moves)*2

global queen_current_position
global rook_one_current_position
global rook_two_current_position
global bishop_current_position

queen_current_position = "d8"
rook_one_current_position = "a8"
rook_two_current_position = "h8"
bishop_current_position = "c8"

global client_queen_current_position
global client_rook_one_current_position
global client_rook_two_current_position
global client_bishop_current_position

client_queen_current_position = "d4"
client_rook_one_current_position = "a2"
client_rook_two_current_position = "a3"
client_bishop_current_position = "f4"

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


global transmit_message
transmit_message = ""

def send_transmissions():
    global transmit_message
    while not transmit_message:
        message = input("[*] Send command to client: ")
        transmit_message = string_to_base14(message)

def make_move(uci_notation , game_id):
    global queen_current_position
    global rook_one_current_position
    global rook_two_current_position
    global bishop_current_position

    r = requests.post(f"https://lichess.org/api/bot/game/{game_id}/move/{uci_notation}" , headers=auth_header)
    start_pos = uci_notation[:2:]
    end_pos = uci_notation[2::]
    if start_pos == queen_current_position:
        queen_current_position = end_pos
    if start_pos == rook_one_current_position:
        rook_one_current_position = end_pos
    if start_pos == rook_two_current_position:
        rook_two_current_position = end_pos
    if start_pos == bishop_current_position:
        bishop_current_position = end_pos

global msg_recieved
msg_recieved = ""

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

def transmission_row_trickery(char):

    global rook_one_current_position
    global rook_two_current_position

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
        rook_number = "7"
        current_pos = rook_one_current_position
    else:
        prenumb = 0
        rook_number = "6"
        current_pos = rook_two_current_position

    
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

def command_parser(msg):
    #do whatever you want with the info you recieve from the agent
    #this is just a poc so we just decode and print ez
    msg = base14_to_string(msg)
    print(f"[*] Recieved information from agent {msg}")

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
    if start_pos == client_queen_current_position:
        client_queen_current_position = end_pos
        
    if "d" in client_queen_current_position:
        if start_pos == client_rook_one_current_position:
            numerical = row_trickery(start_pos , end_pos , 0)
            msg_recieved = msg_recieved + str(numerical)
            client_rook_one_current_position = end_pos
        elif start_pos == client_rook_two_current_position:
            numerical = row_trickery(start_pos , end_pos , 7)
            msg_recieved = msg_recieved + str(numerical)
            client_rook_two_current_position = end_pos
        elif start_pos == client_bishop_current_position:
            msg_recieved = msg_recieved + msg_recieved[-1]
            client_bishop_current_position = end_pos
    else:
        if start_pos == client_rook_one_current_position:
            client_rook_one_current_position = end_pos
        elif start_pos == client_rook_two_current_position:
            client_rook_two_current_position = end_pos
        elif start_pos == client_bishop_current_position:
            client_bishop_current_position = end_pos
        if msg_recieved:
            command_parser(msg_recieved)
            msg_recieved = ""


    if not transmit_message:
        #put it into silence mode
        if "d" in queen_current_position:
            make_move("d5c5" , game_id)
        else:
            random_rook = random.randint(6 , 7)
            if random_rook == 7:
                choices = ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]
                choices.remove(rook_one_current_position[0])
                random_place = random.choice(choices)
                make_move(f"{rook_one_current_position}{random_place}{random_rook}" , game_id)
            else:
                choices = ["a" , "b" , "c" , "d" , "e" , "f" , "g" , "h"]
                choices.remove(rook_two_current_position[0])
                random_place = random.choice(choices)
                make_move(f"{rook_two_current_position}{random_place}{random_rook}" , game_id)
    else:
        if "c" in queen_current_position:
            make_move("c5d5" , game_id)
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
        my_move = False
    else:
        my_move = True
        if state == "initialize":
            make_move(server_initialize_moves[moves_played//2] , game_id)
        if state == "transmission":
            if not transmission_started_yet:
                transmission_started_yet = True
                threading.Thread(target=send_transmissions , args=()).start()
            move_decipher(move_chain , game_id)


    return state
    

#listen for connectins
client_connected = False
while not client_connected:
    with requests.get(f"https://lichess.org/api/stream/event" , headers=auth_header , stream=True) as r:
        if r.status_code != 200:
            print("[*] Failed to connect to lichess")
        
        for line in r.iter_lines():
            if line:
                try:
                    event = json.loads(line)
                    if event["type"] == "challenge":
                        if event["challenge"]["challenger"]["name"] == client_username:
                            client_connected = True
                            challenge_id = event["challenge"]["id"]
                            r = requests.post(f"https://lichess.org/api/challenge/{challenge_id}/accept" , headers=auth_header)
                            print("[*] Challenge accepted")
                            server_connected = True
                            break
                except:
                    pass

#make initial moves
state = "initialize"
game_running = True
while game_running:
    with requests.get(f"https://lichess.org/api/bot/game/stream/{challenge_id}" , headers=auth_header , stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if "state" in data:
                    moves = data["state"]["moves"]
                else:
                    moves = data["moves"]
                state = board_preprocessing(moves , state , challenge_id)
        