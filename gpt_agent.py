import openai

openai.api_key = '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'


# def get_completion(prompt, model="gpt-3.5-turbo"):
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0,  # Control randomness
#     )
#     return response.choices[0].message["content"]

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # Control randomness
    )
    return response.choices[0].message["content"]

def card_to_string(cards):
    cards_str = ["Scarlett", "Mustard", "White", "Green", "Peacock", "Plum","Dagger", "Candlestick", "Revolver", "Rope", "Lead Pipe", "Wrench",
             "Kitchen", "Ballroom", "Conservatory", "Dining Room", "Billiard Room", "Library", "Lounge", "Hall","Study"]
    card_string = []
    for card in cards:
        card_string.append(cards_str[card])
    return card_string

def string_to_number(cards_string):
    cards_str = ["Scarlett", "Mustard", "White", "Green", "Peacock", "Plum", "Dagger", "Candlestick", "Revolver",
                 "Rope", "Lead Pipe", "Wrench",
                 "Kitchen", "Ballroom", "Conservatory", "Dining Room", "Billiard Room", "Library", "Lounge", "Hall",
                 "Study"]
    # print(cards_string)
    return set(index for index, element in enumerate(cards_str) if element in cards_string)



def gpt_agent(state):
    n_players = state.n_players
    players = state.players
    cards_dice =  state.cards_dice
    cards = state.cards
    information_state = state.information_state
    # step = state.step
    suspect_cards= card_to_string(cards&{0,1,2,3,4,5})
    weapon_cards=card_to_string(cards&{6,7,8,9,10,11})
    room_cards=card_to_string(cards&{12,13,14,15,16,17,18,19,20})
    card_in_hand = card_to_string(cards_dice[3])
    player_information =[]
    for key in information_state[3].keys():
        if sum(information_state[3][key]) !=0:
            if information_state[3][key].index(1)==0:
                player_information.append(str(card_to_string([key])) + 'in envelope')
            else:
                player_information.append(str(card_to_string([key]))+'in player'+str(information_state[3][key].index(1))+"'hand")


    prompt = f"""
    In Cluedo Card Game, {n_players} players who are {players} aim to solve a mystery. \
    Set up by separating and shuffling character, weapon, and room cards. \
    Randomly choose one of each to create the mystery, kept secret in an envelope. \
    Distribute remaining cards to players. Players take turns suggesting a character, weapon, and room combination, \
    attempting to match the mystery. Others disprove suggestions by privately revealing a contradicting card. \
    If you have collected enough information, you can take an accusation to guess the mystery; if correct, you win. \
    you are player 3,\
    now the state information include all the suspect cards{suspect_cards}, the weapon cards{weapon_cards}, \
    the room cards{room_cards}, the cards in your hand{card_in_hand},\
    and you already know that {player_information},\
    please generate a optimal suggestion action which is a set\
    with the format like {'Peacock','Candlestick','Ballroom'} \
    please only tell me the suggestion action without any other information
    ''
    """
    response = get_completion(prompt)
    print(response)
    action = string_to_number(response)
    return action


