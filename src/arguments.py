import argparse
import opts

def createParser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=f"{opts.WEBUI_TITLE}"
    )

    # Main argument for files mode
    parser.add_argument(
        "--files-mode",
        choices=["same_server", "mirror", "direct_links"],
        default="same_server",
        help="Specify how the UI handles file paths. "
             "'same_server': gradio will show files from Comfy output/input directory, "
                                "use if this UI is on the same server with Comfy; "
             "'mirror': files are downloaded to a local storage directory, use if this UI "
                        "is on a different server from Comfy and you want automatically download "
                        "files or clients don't access Comfy server; "
             "'direct_links': the UI provides direct links to files on the Comfy server, use if you "
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
        metavar="BASE_DIRECTORY",
        help="Set the base directory for ComfyUI's models, custom_nodes, and file directories. "
             "This is the base for --comfy-output-directory and --comfy-input-directory if they are not specified. "
             "This argument is required when '--files-mode same_server' is selected."
    )
    same_server_group.add_argument(
        "--comfy-output-directory",
        metavar="OUTPUT_DIRECTORY",
        help="Set the specific output directory for ComfyUI. Overrides --comfy-base-directory."
    )
    same_server_group.add_argument(
        "--comfy-input-directory",
        metavar="INPUT_DIRECTORY",
        help="Set the specific input directory for ComfyUI. Overrides --comfy-base-directory."
    )

    # Arguments for mirror mode
    mirror_group = parser.add_argument_group(
        "mirror mode arguments",
        "Arguments for the mirror mode, where files are stored locally."
    )
    mirror_group.add_argument(
        "--mirror-storage-directory",
        default="storage/",
        help="The local directory where mirrored files will be stored. Defaults to 'storage/'."
    )

    return parser

