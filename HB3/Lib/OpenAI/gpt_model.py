from typing import Callable, Generator

from jinja2 import Template

FUNCTION_PARSER = system.import_library("./function_parser.py")
INTERACTION_HISTORY = system.import_library(
    "../../Decisive Behaviour/Knowledge/Interaction_History.py"
)
ENVIRONMENT_KNOWLEDGE = system.import_library(
    "../../Decisive Behaviour/Knowledge/Environment_Knowledge.py"
)

gpt_functions = system.import_library("./gpt_functions.py")


class GPTModel:
    def __init__(
        self,
        model: str,
        system_message: str,
        user_prompt_template: Template,
        functions: list[Callable],
        history_limit: int = 10,
        **kwargs
    ):
        """Initialise a GPTModel class.

        Args:
            model: OpenAI model to use
            system_message: The system message for prompting the LLM
            user_prompt_template: The user prompt template for the LLM
            functions: The functions the model is allowed to call
            history_limit: The number of interactions to include in the prompt
            **kwargs to be passed to the openai call
        """
        self.model = model
        self.user_prompt_template = user_prompt_template
        self.set_system_message(system_message)
        self.history_limit = history_limit
        self.set_functions(functions)
        self.gpt_kwargs = kwargs
        self.interaction_history = INTERACTION_HISTORY.InteractionHistory()

    def set_system_message(self, system_message) -> None:
        """
        Set system message which is used for prompting the LLM.

        Args:
            system_message: message to set.
        """
        self.system_messages = [{"role": "system", "content": system_message}]

    def set_functions(self, functions: list[Callable]):
        """Set the functions for a GPT model.

        Args:
            functions: the functions to set
        """
        (
            self.functions_prompt,
            self.functions_map,
        ) = FUNCTION_PARSER.get_functions_prompt_map(functions)

    def get_message_prompt(self) -> list[dict]:
        """Get the prompt from the interaction history, profiles etc.

        Returns:
            a list of messages to be passed to the openai api
        """
        conversation = self.interaction_history.to_message_list(self.history_limit)

        # Disable profiles until identity is stable
        # profiles = ENVIRONMENT_KNOWLEDGE.get_profiles()
        messages = self.system_messages + conversation

        return messages

    async def __call__(self, messages: list[dict]) -> Generator[dict, None, None]:
        """Call the model on a set of messages.

        Args:
            messages: run the model on the set of messages

        Yields:
            the responses from openai
        """
        return await gpt_functions.run_chat_streamed(
            model=self.model,
            messages=messages,
            eos_separators=[",", ". ", "!", "?", "\n", ":"],
            functions=self.functions_prompt,
            **self.gpt_kwargs
        )
