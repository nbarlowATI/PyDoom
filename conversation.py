import pygame as pg
from speechbubble import SpeechBubble
from events import TEXT_EVENT, TEXT_FINISH_EVENT, NPC_RESPONSE_EVENT

class Conversation:

    def __init__(self, game, participants=[]):
        self.game = game
        self.participants = participants
        self.participant_ids = [p.id for p in participants]
        self.speech_bubble = None
        self.now_talking = None
        self.conversation_so_far = []

    def add_participant(self, character):
        if character.id not in self.participant_ids:
            print(f"adding participant {character.id}")
            self.participants.append(character)
            self.participant_ids.append(character.id)

    def talk(self, talker, text=None):
        print(f"conversation.talk called by {talker.id}")
        # if self.now_talking and self.now_talking.id == talker.id:
        #     return
        self.now_talking = talker
        sb = SpeechBubble(self.game, self.now_talking)
        if text:
            # this will only be set by NPC - player will type input.
            print(f"setting speechbubble text to {text}")
            sb.set_text(text)
            self.conversation_so_far.append(f"{talker.id}: {text}")
        self.speech_bubble = sb

    def set_next_talker(self):
        if len(self.participants) < 2:
            return
        print(f"number of participants {len(self.participants)}")
        for i, p in enumerate(self.participants):
            if p.id == self.now_talking.id:
                self.now_talking.talking = False
                next_talker_idx = (i + 1) % len(self.participants)
                self.now_talking = self.participants[next_talker_idx]
                print(f"NOW TALKING {self.now_talking.id}")
                break

    def update(self):
        pass

    def handle_event(self, event):
        if event.type == TEXT_EVENT:
            self.speech_bubble.handle_event(event)
        elif (event.type == pg.KEYDOWN and self.now_talking.id == "player"):
            if not self.speech_bubble:
                self.talk(self.now_talking)
            if self.speech_bubble:
                self.speech_bubble.handle_event(event)
        elif event.type == TEXT_FINISH_EVENT:
            print("Got a TEXT_FINISH_EVENT")
            self.speech_bubble = None
            pg.time.set_timer(TEXT_FINISH_EVENT, 0)
            self.set_next_talker()
        elif event.type == NPC_RESPONSE_EVENT:
            self.talk(self.now_talking, event.text)
            self.now_talking.thinking = False
