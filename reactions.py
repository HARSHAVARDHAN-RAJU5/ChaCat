current_state = "neutral"
state_timer = 0
state_duration = 0

def set_state(state, duration=0):
    global current_state, state_timer, state_duration
    current_state = state
    state_timer = 0
    state_duration = duration

def get_state():
    return current_state

def update_state():
    global current_state, state_timer, state_duration
    if state_duration > 0:
        state_timer += 1
        if state_timer >= state_duration:
            state_timer = 0
            state_duration = 0
            current_state = "neutral"

reminder_reactions = {
    "food": {
        "question": "time to eat <3",
        "yes": {"state": "excited", "bubble": "yay! enjoy your food <3","duration": 1800},
        "no":  {"state": "angry",      "bubble": "You have 5minutes to eat or I'm getting angry!","duration": 1800},
    },
    "bath": {
        "question": "time to take a bath <3",
        "yes": {"state": "love",    "bubble": "good girl!! squeaky clean <3","duration": 1800},
        "no":  {"state": "judging", "bubble": "...really? go bathe.","duration": 1800},
    },
    "grocery": {
        "question": "time to buy grocery and fruits <3",
        "yes": {"state": "excited", "bubble": "yay!! get some yummy fruits <3","duration": 1800},
        "no":  {"state": "sad",     "bubble": "but we need food... :(","duration": 1800},
    },
}