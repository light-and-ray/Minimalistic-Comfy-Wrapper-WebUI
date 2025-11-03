from mcww import opts
import sys, shlex, os, argparse


def _createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="standalone-start.py",
        description=f"{opts.WEBUI_TITLE}"
    )

    # Main arguments
    parser.add_argument(
        "--storage-directory",
        default=None,
        help="The local directory where files will be stored. Defaults to 'storage/'."
    )

    parser.add_argument(
        "--files-mode",
        choices=["same_server", "mirror", "direct_links"],
        default="mirror",
        help="Specify how the UI handles file paths. "
             "'same_server': gradio will show files from Comfy output/input directory, "
                        "use it if this UI is on the same server with Comfy; "
             "'mirror': files are downloaded to a local storage directory, use it if this UI "
                        "is on a different server from Comfy and you want automatically download "
                        "files or clients don't access Comfy server; "
             "'direct_links': the UI provides direct links to files on the Comfy server, use it if you "
                        "don't want to download any files on the UI server, and the UI clients "
                        "have access to Comfy server."
    )

    # Arguments for same_server mode
    same_server_group = parser.add_argument_group(
        "same_server mode arguments",
        "Arguments to specify ComfyUI's file paths when running in same_server mode."
    )
    same_server_group.add_argument(
        "--comfy-base-directory",
        help="Set the base directory for ComfyUI's models, custom_nodes, and file directories. "
             "This is the base for --comfy-output-directory and --comfy-input-directory if they are not specified. "
             "This argument is required when '--files-mode same_server' is selected."
    )
    same_server_group.add_argument(
        "--comfy-output-directory",
        help="Set the specific output directory for ComfyUI. Overrides --comfy-base-directory."
    )
    same_server_group.add_argument(
        "--comfy-input-directory",
        help="Set the specific input directory for ComfyUI. Overrides --comfy-base-directory."
    )

    return parser


def parseArgs():
    parser = _createParser()
    rawArgs = sys.argv[1:]
    command_line_flags = os.getenv("COMMAND_LINE_FLAGS")
    if command_line_flags:
        args_from_env = shlex.split(command_line_flags)
        rawArgs[1:1] = args_from_env
        print("Added flags from COMMAND_LINE_FLAGS env. variable")
    print(f"Flags: {rawArgs}")
    parsed_args = parser.parse_args(rawArgs)
    return parsed_args
