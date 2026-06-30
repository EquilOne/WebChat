import asyncio

from openai.types.responses import EasyInputMessage, Response
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.status import Status
from rich.table import Table
from rich.text import Text

from custom_args import args

# from input import ChatInputApp
from response import get_response

console = Console(width=100)
status = Status("Crunching the tokens...", spinner="pipe", spinner_style="bold white")


# def construct_panel(content, **args):
#     return Panel(content, **args)


async def main():
    # if not args.one_shot:
    #     await ChatInputApp().run_async()
    #     return
    if not args.user_prompt:
        raise RuntimeError("One-shot (CLI mode) requires a prompt argument")

    resp: Response | None = None
    history: list = []
    input_text = args.user_prompt
    ai_response = ""

    # history.append({"role": "user", "content": input})
    history.append(EasyInputMessage(role="user", content=input_text))

    if args.dry_run:
        return

    with Live(Panel(Group(status), expand=False), console=console, transient=True):
        resp = await get_response(history)
        if resp.status == "failed" or resp.error:
            raise RuntimeError(f"API call failed: {resp.error}")
        ai_response = resp.output_text
        history.append(EasyInputMessage(role="assistant", content=ai_response))

        # print("resp:", resp.__dict__)
        if resp is None:
            raise RuntimeError("No response returned")
        assistant_response = Text()
        response_info = Text()
        response_info.append("User prompt: \n", style="bold")
        response_info.append(f"{input_text}")
        console.print(Panel(response_info, expand=False))
        if args.verbose:
            if not resp.usage:
                raise RuntimeError("No usage data found")
            usage = resp.usage
            # For testing purposes
            # print("User prompt: ", input)
            # print("Prompt tokens: ", usage.input_tokens)
            # print("Response tokens: ", usage.output_tokens)
            prompt_tokens = usage.input_tokens
            resp_tokens = usage.output_tokens
            reasoning_tokens = usage.output_tokens_details.reasoning_tokens

            tokens_table = Table(title="Tokens", title_justify="left")
            tokens_table.add_column("Token Type", justify="left", no_wrap=True)
            tokens_table.add_column("Count", justify="center", no_wrap=True)
            tokens_table.add_row("Prompt", str(prompt_tokens))
            tokens_table.add_row("Response", str(resp_tokens))
            tokens_table.add_row("Reasoning", str(reasoning_tokens))
            console.print(Panel(tokens_table, expand=False))

            model_info = Text()
            model_info.append("Model: ", style="bold")
            model_info.append(f"{resp.model}")
            console.print(Panel(model_info, expand=False))
        assistant_response.append("Assistant:\n\n", style="bold")
        assistant_response.append(ai_response)
        console.print(Panel(assistant_response))


if __name__ == "__main__":
    asyncio.run(main())
