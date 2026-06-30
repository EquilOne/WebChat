from openai.types.responses.response_input_param import ResponseInputParam
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Footer, Header, LoadingIndicator, RichLog, TextArea

from response import get_response


class ChatInput(TextArea):
    class Submitted(Message):
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    BINDINGS = [
        Binding("enter", "submit", "Submit", show=False),
    ]

    def action_submit(self) -> None:
        text = self.text.strip()
        if text:
            self.post_message(self.Submitted(text))
            self.clear()

    async def _on_key(self, event) -> None:
        if event.key == "shift+enter":
            event.stop()
            self.insert("\n")
        elif event.key == "enter":
            event.prevent_default()
            self.action_submit()


class ChatInputApp(App):
    CSS = """
    ChatInput {
        height: 5;           /* input box height */
        dock: bottom;        /* pin to bottom */
        border: tall $primary;
    }
    RichLog {
        height: 1fr;         /* takes remaining space */
        border: tall $surface;
    }
    LoadingIndicator {
        height: 1;
        dock: bottom;
        layer: top;
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator()
        yield RichLog(id="log", markup=True, wrap=True)
        yield ChatInput(id="chat", placeholder="Type your message here...")
        yield Footer()

    def on_mount(self) -> None:
        self.history: ResponseInputParam = []
        self.query_one(ChatInput).focus()

    def create_response_input_param(self, user_input: str) -> ResponseInputParam:
        self.history.append({"role": "user", "content": user_input})
        return self.history

    async def on_chat_input_submitted(self, message: ChatInput.Submitted) -> None:
        loader = self.query_one(LoadingIndicator)
        loader.display = True
        log = self.query_one("#log", RichLog)
        chat = self.query_one("#chat", ChatInput)

        chat.disabled = True
        log.write(f"[bold rose]You:[/bold rose] {message.text}")
        # log.write(f"[italic]{status}[/italic]")

        try:
            resp = await get_response(self.create_response_input_param(message.text))
            log.write(f"[bold rose]Assistant:[/bold rose] {resp.output_text}")
            self.history.append({"role": "assistant", "content": resp.output_text})
        except Exception as e:
            log.write(f"[bold red]Error:[/bold red] {e}")
        finally:
            loader.display = False
            chat.disabled = False
            chat.focus()
