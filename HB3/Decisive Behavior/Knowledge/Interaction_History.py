"""
Log all the events which occurs in the short term.
"""
from abc import abstractmethod
from time import time as time_unix
from typing import List, ClassVar, Optional
from dataclasses import dataclass

CONFIG = system.import_library("../../../Config/Chat.py").CONFIG

ROBOT_NAME = CONFIG["ROBOT_NAME"]


class InteractionEvent:
    openai_role: ClassVar[Optional[str]] = None

    @abstractmethod
    def to_text(self) -> Optional[str]:
        """Return the event as a string to be printed into the interaction history.

        Returns:
            A description of the event.
        """
        pass

    def to_message(self) -> Optional[dict]:
        """Return the event as a message to be printed into the interaction history.

        Returns:
            A description of the event.
        """
        if self.openai_role:
            return {"role": self.openai_role, "content": self.to_text()}
        else:
            return None

    def try_conflate(self, other):
        return None


@dataclass(slots=True)
class TTSEvent(InteractionEvent):
    tts_text: str
    language_code: str

    openai_role: ClassVar[Optional[str]] = "assistant"

    def to_text(self) -> Optional[str]:
        return f'{ROBOT_NAME} said: "{self.tts_text}"'

    def to_message(self) -> Optional[dict]:
        """Return the event as a message to be printed into the interaction history.

        Returns:
            A description of the event.
        """
        return {"role": self.openai_role, "content": self.tts_text}

    def try_conflate(self, other):
        if not isinstance(other, TTSEvent):
            return None

        # Nothing to stop LLM from changing language part way through.
        language_code = self.language_code
        if other.language_code != language_code:
            language_code = "?"

        return TTSEvent(
            tts_text=self.tts_text + " " + other.tts_text,
            language_code=language_code,
        )


@dataclass(slots=True)
class SpeechRecognisedEvent(InteractionEvent):
    speaker: str
    speech: str

    openai_role: ClassVar[Optional[str]] = "user"

    def to_text(self) -> Optional[str]:
        return f'User said: "{self.speech}"'


DiagnosticEvent = SpeechRecognisedEvent


@dataclass(slots=True)
class NonVerbalInteractionEvent(InteractionEvent):
    actor: str
    description: str

    openai_role: ClassVar[Optional[str]] = "user"

    def to_text(self) -> Optional[str]:
        return f'{self.actor}: "**{self.description}**"'


@dataclass(slots=True)
class PersonEntryEvent(InteractionEvent):
    person: str

    def to_text(self) -> Optional[str]:
        return None

    def __eq__(self, other):
        return (
            type(other).__name__ == self.__class__.__name__
            and other.person == self.person
        )


@dataclass(slots=True)
class PersonExitEvent(InteractionEvent):
    person: str

    def to_text(self) -> Optional[str]:
        return None

    def __eq__(self, other):
        return (
            type(other).__name__ == self.__class__.__name__
            and other.person == self.person
        )


@dataclass(slots=True)
class InteractionItem:
    event_time_s: float
    event: InteractionEvent


# TODO: This doesn't need to be a class, these can be top-level module functions.
class InteractionHistory:
    # Use a single shared history by putting it here
    # Editing this script will throw away the history tho - be careful! :smile:
    history = []

    def __getitem__(self, idx):
        return self.history[idx]

    def __len__(self):
        return len(self.history)

    def to_text(self, max_len: Optional[int] = None) -> List[str]:
        """Get history as line separated events.

        Args:
            max_len: maximum number of events to pull. If None, there is no limit. Defaults to None.

        Returns:
            The interaction history as line-separated events.
        """
        chunks: List[str] = []
        last_event: Optional[InteractionEvent] = None
        for item in reversed(self.history):  # iterate history in reverse order
            # Conflate messages of the same type to avoid artifacts from streaming tts
            # We want 1 message per user.
            if (conflated := item.event.try_conflate(last_event)) is not None:
                chunks[-1] = conflated.to_text()
                last_event = conflated
                continue
            elif (text := item.event.to_text()) is not None:
                # Only check length when we add a new item, (so we can still conflate)
                if max_len and (len(chunks) >= max_len):
                    break
                chunks.append(text)
                last_event = item.event

        return "\n".join(reversed(chunks))

    def to_message_list(self, max_len: Optional[int] = None) -> List[dict]:
        """Get history as list of messages (for ChatCompletion API).

        Args:
            max_len: maximum number of events to pull. If None, there is no limit. Defaults to None.

        Returns:
            The interaction history as message list.
        """
        messages: List[str] = []
        last_event: Optional[InteractionEvent] = None
        for item in reversed(self.history):  # iterate history in reverse order
            # Conflate messages of the same type to avoid artifacts from streaming tts
            # We want 1 message per user.
            if (conflated := item.event.try_conflate(last_event)) is not None:
                messages[-1] = conflated.to_message()
                last_event = conflated
            elif (message := item.event.to_message()) is not None:
                # Only check length when we add a new item, (so we can still conflate)
                if max_len and (len(messages) >= max_len):
                    break
                messages.append(message)
                last_event = item.event

        return messages[-1::-1]

    def get_person_conversation(self, person_name: str) -> Optional[str]:
        """Get conversation history since a particular person entered the scene until they left the scene.

        Args:
            person_name: the name of the person to get information about.

        Returns:
            The interaction history as line-separated events.
        """
        try:
            start_point = next(
                len(self.history) - i
                for i, item in enumerate(reversed(self.history))
                if item.event == PersonEntryEvent(person_name)
            )
        except StopIteration:
            return None

        items = []
        person_has_spoken = False
        for item in self.history[start_point:]:
            if type(item.event).__name__ == "SpeechRecognisedEvent":
                person_has_spoken = True
            if item.event == PersonExitEvent(person_name):
                break
            if (text := item.event.to_text()) is not None:
                items.append(text)
        if not person_has_spoken:
            return None
        return "\n".join(items)

    def add_to_memory(self, interaction_event):
        event_time_s = time_unix()
        self.history.append(InteractionItem(event_time_s, interaction_event))
        # if isinstance(interaction_event, PersonEntryEvent):
        #     print('add person entry event ####@@@@@ ')
        #     import traceback
        #     traceback.print_stack()
        # if isinstance(interaction_event, PersonExitEvent):
        #     print('add person exit event $$$$@@@@@!!!')
        #     import traceback
        #     traceback.print_stack()

    def reset(self):
        self.history[:] = []