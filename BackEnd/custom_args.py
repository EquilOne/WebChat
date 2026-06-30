import argparse

from rich.console import Console

console = Console(width=100)

parser = argparse.ArgumentParser(
    prog="Chatbot", description="Basic call, response chatbot"
)
parser.add_argument(
    "-o", "--one-shot", action="store_true", help="Single response mode, no history"
)
parser.add_argument("user_prompt", type=str, nargs="?", help="User prompt")
parser.add_argument("-d", "--debug", action="store_true", help="Run with debug output")
parser.add_argument("-n", "--dry-run", action="store_true", help="Run without API call")
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose output"
)
args = parser.parse_args()

if args.debug:
    console.print(args.__dict__)
