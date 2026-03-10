"""知识库导入入口"""

import os
import shlex
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import config_data as config
from document_importer import ensure_knowledge_base, import_documents, list_knowledge_bases
from knowledge_base_registry import normalize_knowledge_base_name


EXIT_COMMANDS = {"/exit", "/quit"}
KNOWN_BARE_COMMANDS = {"help", "list", "use", "create", "import", "status", "exit", "quit"}


def print_knowledge_bases():
    print("当前可用知识库：")
    for knowledge_base in list_knowledge_bases():
        print(
            f"- {knowledge_base['name']}: {knowledge_base['label']} "
            f"(collection={knowledge_base['collection_name']}, "
            f"directory={knowledge_base['persist_directory']})"
        )


def print_help():
    print("可用命令：")
    print("- /help: 查看帮助")
    print("- /list: 列出当前知识库")
    print("- /use <知识库名>: 切换当前知识库")
    print("- /create <知识库名> [展示名称]: 创建知识库")
    print("- /import <文件或目录路径>: 导入文件到当前知识库")
    print("- /import <文件或目录路径> --non-recursive: 导入目录但不递归")
    print("- /status: 查看当前知识库")
    print("- /exit: 退出")


def print_status(knowledge_base_name):
    print(f"当前知识库：{knowledge_base_name}")


def is_missing_slash_command(command_text):
    command_name = command_text.split(maxsplit=1)[0].lower()
    return command_name in KNOWN_BARE_COMMANDS


def run_import(input_path, knowledge_base_name, recursive=True, create_if_missing=False, label=None):
    knowledge_base_name, is_created = ensure_knowledge_base(
        knowledge_base_name,
        create_if_missing=create_if_missing,
        label=label,
    )

    if is_created:
        print(f"已创建知识库：{knowledge_base_name}")

    summary = import_documents(
        input_path,
        knowledge_base_name,
        recursive=recursive,
    )

    if summary["success_count"] == 0 and summary["skipped_count"] == 0 and summary["failed_count"] == 0:
        print("未发现可导入文件，请检查路径和文件类型。")
        return 0

    for error in summary["errors"]:
        print(f"导入失败：{error['file_path']}，原因：{error['reason']}")

    print(
        f"导入完成：成功 {summary['success_count']} 个，跳过 {summary['skipped_count']} 个，"
        f"失败 {summary['failed_count']} 个，目标知识库 {summary['knowledge_base_name']}"
    )
    return 0 if summary["failed_count"] == 0 else 1


def run_create_command(command_parts, current_knowledge_base):
    if len(command_parts) < 2:
        print("用法：/create <知识库名> [展示名称]")
        return current_knowledge_base

    knowledge_base_name = command_parts[1]
    knowledge_base_label = " ".join(command_parts[2:]) if len(command_parts) > 2 else None
    normalized_name, is_created = ensure_knowledge_base(
        knowledge_base_name,
        create_if_missing=True,
        label=knowledge_base_label,
    )
    if is_created:
        print(f"已创建知识库：{normalized_name}")
    else:
        print(f"知识库已存在：{normalized_name}")
    return normalized_name


def run_interactive_shell(default_knowledge_base):
    current_knowledge_base = normalize_knowledge_base_name(default_knowledge_base)
    print("已进入知识库导入模式，输入 /help 查看命令。")
    print_status(current_knowledge_base)

    while True:
        try:
            command_text = input(f"\nimport[{current_knowledge_base}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出导入模式。")
            return 0

        if not command_text:
            continue

        if is_missing_slash_command(command_text):
            print("命令必须以 / 开头，例如 /import ./docs。")
            continue

        if not command_text.startswith("/"):
            print("未知输入，导入模式下请使用 /help 查看命令。")
            continue

        try:
            command_parts = shlex.split(command_text)
        except ValueError as exc:
            print(f"命令解析失败：{exc}")
            continue

        command_name = command_parts[0].lower()

        if command_name in EXIT_COMMANDS:
            print("已退出导入模式。")
            return 0

        if command_name == "/help":
            print_help()
            continue

        if command_name == "/list":
            print_knowledge_bases()
            continue

        if command_name == "/status":
            print_status(current_knowledge_base)
            continue

        if command_name == "/use":
            if len(command_parts) < 2:
                print("用法：/use <知识库名>")
                continue
            try:
                current_knowledge_base, _ = ensure_knowledge_base(command_parts[1])
                print_status(current_knowledge_base)
            except ValueError as exc:
                print(exc)
            continue

        if command_name == "/create":
            current_knowledge_base = run_create_command(command_parts, current_knowledge_base)
            continue

        if command_name == "/import":
            if len(command_parts) < 2:
                print("用法：/import <文件或目录路径> [--non-recursive]")
                continue
            input_path = command_parts[1]
            recursive = "--non-recursive" not in command_parts[2:]
            try:
                run_import(input_path, current_knowledge_base, recursive=recursive)
            except Exception as exc:
                print(f"导入失败：{exc}")
            continue

        print(f"未知命令：{command_name}，输入 /help 查看支持的命令。")


def main():
    return run_interactive_shell(config.DEFAULT_KNOWLEDGE_BASE)


if __name__ == "__main__":
    sys.exit(main())