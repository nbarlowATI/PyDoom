import ollama

from settings import OLLAMA_MODEL

SYSTEM_MSG_GENERAL = {
    "role": "system",
    "content": "You are an NPC in the video game DOOM.  I will give you a user prompt containing a conversation up to this point.  Please respond to the most recent message with a JSON structure with keys 'text' and 'action', where 'action' can only be 'GOTO <location>' or 'None'.  The GOTO option should only be used if there is a specific conversational reason for it."
}


class Talk:
    def __init__(self):
        pass

    def get_response(self, backstory, previous_conversation):
        user_msg_backstory = {"role": "user", "content": backstory}
        user_msg = {"role": "user", "content": f"{previous_conversation}"}
        response = ollama.chat(model=OLLAMA_MODEL, messages = [
            SYSTEM_MSG_GENERAL, user_msg_backstory, user_msg
        ])
        return response


