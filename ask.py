"""问答服务"""

import shlex
import sys

from cli_terminal import terminal
import config_data as config
from knowledge_base_registry import get_knowledge_base_label, get_knowledge_base_names, normalize_knowledge_base_name
from rag import RAGService


EXIT_COMMANDS = {"/exit", "/quit", ":q"}
HELP_COMMANDS = {"/help", "/h"}
LIST_COMMANDS = {"/list"}
KNOWN_BARE_COMMANDS = {"help", "h", "list", "use", "status", "exit", "quit"}


def print_knowledge_bases():
    print("当前可用知识库：")
    for knowledge_base_name in get_knowledge_base_names():
        print(f"- {knowledge_base_name}: {get_knowledge_base_label(knowledge_base_name)}")


def print_help():
    print("可用命令：")
    print("- /help: 查看帮助")
    print("- /list: 列出当前可用知识库")
    print("- /use <name>: 切换到指定知识库")
    print("- /status: 查看当前知识库")
    print("- /exit 或 /quit: 退出对话")


def create_rag_service(knowledge_base_name, session_id):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    return normalized_name, RAGService(normalized_name, session_id=session_id)


def switch_knowledge_base(command_text, session_id):
    command_parts = shlex.split(command_text)
    if len(command_parts) == 1:
        print_knowledge_bases()
        return None, None

    target_knowledge_base = normalize_knowledge_base_name(command_parts[1])
    return create_rag_service(target_knowledge_base, session_id)


def is_missing_slash_command(prompt):
    command_name = prompt.split(maxsplit=1)[0].lower()
    return command_name in KNOWN_BARE_COMMANDS


def stream_answer(rag_service, prompt):
    answer_chunks = []
    for chunk in rag_service.chain.stream({"input": prompt}, rag_service.session_config):
        chunk_text = chunk if isinstance(chunk, str) else getattr(chunk, "content", str(chunk))
        if not chunk_text:
            continue
        print(chunk_text, end="", flush=True)
        answer_chunks.append(chunk_text)
    print()
    return "".join(answer_chunks)


def run_chat_loop(initial_knowledge_base, session_id):
    knowledge_base_name, rag_service = create_rag_service(initial_knowledge_base, session_id)
    print(f"当前知识库：{knowledge_base_name} ({get_knowledge_base_label(knowledge_base_name)})")
    print("输入 /help 查看命令。")

    while True:
        try:
            prompt = terminal.prompt(f"\n你[{knowledge_base_name}]: ")
        except (EOFError, KeyboardInterrupt):
            print("\n已退出对话。")
            return 0

        if not prompt:
            continue

        if prompt.startswith("/"):
            try:
                command_parts = shlex.split(prompt)
            except ValueError as exc:
                print(f"命令解析失败：{exc}")
                continue

            command_name = command_parts[0].lower()

            if command_name in EXIT_COMMANDS:
                print("已退出对话。")
                return 0

            if command_name in HELP_COMMANDS:
                print_help()
                continue

            if command_name in LIST_COMMANDS and len(command_parts) == 1:
                print_knowledge_bases()
                continue

            if command_name == "/status":
                print(f"当前知识库：{knowledge_base_name} ({get_knowledge_base_label(knowledge_base_name)})")
                continue

            if command_name == "/use":
                try:
                    switched_name, switched_service = switch_knowledge_base(prompt, session_id)
                except ValueError as exc:
                    print(f"知识库切换失败：{exc}")
                    continue

                if switched_name is not None:
                    knowledge_base_name = switched_name
                    rag_service = switched_service
                    print(f"已切换到知识库：{knowledge_base_name} ({get_knowledge_base_label(knowledge_base_name)})")
                continue

            print(f"未知命令：{command_name}，输入 /help 查看支持的命令。")
            continue

        if is_missing_slash_command(prompt):
            print("命令必须以 / 开头，例如 /use big-data。")
            continue

        print(f"\n助手[{knowledge_base_name}]: ", end="", flush=True)
        try:
            stream_answer(rag_service, prompt)
        except KeyboardInterrupt:
            print("\n已中断本次回答。")
        except Exception as exc:
            print(f"\n对话失败：{exc}")


def main():
    return run_chat_loop(config.DEFAULT_KNOWLEDGE_BASE, config.default_session_id)


if __name__ == "__main__":
    sys.exit(main())
