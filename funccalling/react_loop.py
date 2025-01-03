import os
from dotenv import load_dotenv

load_dotenv()

from collections.abc import Callable
import json
import sys
import traceback

from google.protobuf.json_format import MessageToJson
from vertexai import generative_models
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool

model = GenerativeModel(
    "gemini-1.5-pro",
    system_instruction=[
        "You are an assistant that helps me tidy my room."
        "Your goal is to make sure all the books are on the shelf, all clothes are in the hamper, and the trash is empty.",
        "You cannot receive any input from me.",
    ],
    generation_config={"temperature": 0.0},
    safety_settings=[
        generative_models.SafetySetting(
            category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            method=generative_models.SafetySetting.HarmBlockMethod.PROBABILITY,
            threshold=generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
    ],
)


verbose = True

# Conveience function to print multiline text indented


def indent(text, amount, ch=" "):
    padding = amount * ch
    return "".join(padding + line for line in text.splitlines(True))


# Convenience function for logging statements
def logging(msg):
    global verbose
    print(msg) if verbose else None


# Retrieve the text from a model response
def get_text(resp):
    return resp.candidates[0].content.parts[0].text


# Retrieve the function call information from a model response
def get_function_call(resp):
    return resp.candidates[0].function_calls[0]


def get_action_label(json_payload, log, role="MODEL"):
    log(f"{role}: {json_payload}")
    answer = json.loads(json_payload)
    action = answer["next_action"]
    return action


def get_action_from_function_call(func_payload, log, role="MODEL"):
    json_payload = MessageToJson(func_payload._pb)
    log(f"{role}: {json_payload}")
    return func_payload.name


# Initial room state


def reset_room_state(room_state):
    room_state.clear()
    room_state["clothes"] = "floor"
    room_state["books"] = "scattered"
    room_state["wastebin"] = "empty"


# Functions for actions (replace these with Gemini function calls)
def pick_up_clothes(room_state):
    room_state["clothes"] = "carrying by hand"
    return room_state, "The clothes are now being carried."


def put_clothes_in_hamper(room_state):
    room_state["clothes"] = "hamper"
    return room_state, "The clothes are now in the hamper."


def pick_up_books(room_state):
    room_state["books"] = "in hand"
    return room_state, "The books are now in my hand."


def place_books_on_shelf(room_state):
    room_state["books"] = "shelf"
    return room_state, "The books are now on the shelf."


def empty_wastebin(room_state):
    room_state["wastebin"] = "empty"
    return room_state, "The wastebin is emptied."


# Maps a function string to its respective function reference.
def get_func(action_label):
    return None if action_label == "" else getattr(sys.modules[__name__], action_label)


# Function to check if the room is tidy
# Some examples below do not call this function,
# for those examples the model takes on the goal validation role.


def is_room_tidy(room_state):
    return all(
        [
            room_state["clothes"] == "hamper",
            room_state["books"] == "shelf",
            room_state["wastebin"] == "empty",
        ]
    )

functions = """

    put_clothes_in_hamper - place clothes into hamper, instead of carrying them around in your hand.
    pick_up_clothes - pick clothes up from the floor.
    pick_up_books - pick books up from anywhere not on the shelf
    place_books_on_shelf - self explanatory.
    empty_wastebin - self explanatory.
    done - when everything are in the right place.
"""


def get_next_step_full_prompt(state, cycle, log):
    observation = f"The room is currently in this state: {state}."
    prompt = "\n".join(
        [
            observation,
            f"You can pick any of the following action labels: {functions}",
            "Which one should be the next step to achieve the goal? ",
            'Return a single JSON object containing fields "next_action" and "rationale".',
        ]
    )
    (
        log("PROMPT:\n{}".format(indent(prompt, 1, "\t")))
        if cycle == 1
        else log(f"OBSERVATION: {observation}")
    )

    return prompt


 Main ReAct loop


def main_react_loop(loop_continues, log):
    room_state = {}
    reset_room_state(room_state)
    trash_added = False

    cycle = 1
    while loop_continues(cycle, room_state):
        log(f"Cycle #{cycle}")

        # Observe the environment (use Gemini to generate an action thought)
        try:  # REASON #
            response = model.generate_content(
                get_next_step_full_prompt(room_state, cycle, log),
                generation_config={"response_mime_type": "application/json"},
            )  # JSON Mode
            action_label = get_action_label(get_text(response).strip(), log)

        except Exception:
            traceback.print_exc()
            log(response)
            break

        # Execute the action and get the observation
        if action_label == "done":
            break

        try:  # ACTION #
            # Call the function mapped from the label
            room_state, acknowledgement = get_func(action_label)(room_state)
            log(f"ACTION:   {action_label}\nEXECUTED: {acknowledgement}\n")

        except Exception:
            log("No action suggested.")

        # Simulating a change in environment
        if cycle == 4 and not trash_added:
            room_state["wastebin"] = "1 item"
            trash_added = True

        cycle += 1
        # End of while loop

    # Determine the final result
    result = (
        "The room is tidy!" if is_room_tidy(room_state) else "The room is not tidy!"
    )

    return room_state, result


# We are passing in a while loop continuation test function:
# Continue while loop when number of cycles <= 10 AND the room is not yet tidy.
# We are explicitly testing if the room is tidy within code.
#
# To save space, only the first cycle prints the full prompt.
# The same prompt template is used for every model call with a modified room state.
room_state, result = main_react_loop(
    lambda c, r: c <= 10 and not is_room_tidy(r), logging
)
print(room_state, result)