import os
from pathlib import Path
from struct import pack, unpack
from argparse import ArgumentParser

from utils import (
    AssetHeader,
    AssetUnpackType,
    AssetPackType,
    print_asset_info,
    print_asset_info_header,
    get_assets_from_path,
)

from constants import SIZEOF_MAGIC_DATA, SIZEOF_NUM_ASSETS


def unpack_assets_header(from_file: str) -> AssetHeader:
    num_assets: int = 0
    assets: list[AssetUnpackType] = []
    size = os.path.getsize(from_file)

    with open(from_file, "rb") as pak:
        num_assets = unpack("<I", pak.read(4))[0]
        for _ in range(num_assets):
            path = pak.read(64).decode("ascii").rstrip("\x00").replace("\\", os.sep)
            offset = unpack("<I", pak.read(4))[0]
            assets.append(AssetUnpackType(path, offset, 0))

        for index, curr_asset in enumerate(assets):
            next_index = index + 1
            assets[index] = curr_asset._replace(
                size=(assets[next_index][1] if next_index < len(assets) else size)
            )
    return AssetHeader(num_assets, assets)


def unpack_assets(from_file: str, to_path: str) -> None:
    to_path = Path(to_path)

    if not to_path.exists():
        to_path.mkdir()

    header = unpack_assets_header(from_file)

    with open(from_file, "rb") as pak:
        print_asset_info_header()
        for asset in header.assets:
            pak.seek(asset.offset, 0)
            data = pak.read(asset.size - asset.offset)
            output_filename = to_path / asset.path

            if output_filename.exists():
                msg = f"File {output_filename} already exists, skipping"
                print(f"| {msg:<64} | {asset.offset:>10} | {asset.size:>10} |")
                continue
            else:
                print_asset_info(asset)

            os.makedirs(os.path.dirname(output_filename), exist_ok=True)

            with open(output_filename, "wb") as f:
                f.write(data)


def pack_assets(from_path: str, to_file: str) -> None:
    assets: list[AssetPackType] = get_assets_from_path(from_path)
    assets_count = len(assets)

    size_of_header = SIZEOF_NUM_ASSETS + ((assets_count + 1) * SIZEOF_MAGIC_DATA)

    # fmt: off
    magic_data = bytes([
        0x00, 0x00, 0x00, 0x00, 0xBC, 0x42, 0x59, 0x81, 0x00, 0x00, 0x00, 0x00, 0x8C, 0x83, 0x59, 0x81, 
        0x8C, 0x83, 0x59, 0x81, 0x88, 0x83, 0x59, 0x81, 0x3B, 0xAE, 0xF7, 0xBF, 0x00, 0x20, 0x56, 0x81, 
        0x00, 0x00, 0x00, 0x00, 0x8C, 0x83, 0x59, 0x81, 0xDB, 0xAE, 0xF7, 0xBF, 0x8C, 0x83, 0x59, 0x81, 
        0xDE, 0xDA, 0xF7, 0xBF, 0x8C, 0x83, 0x59, 0x81, 0x8C, 0x83, 0x59, 0x81, 0xE2, 0x13, 0xF7, 0xBF, 
        0x59, 0xB7, 0x5E, 0x01, 
    ])
    # fmt: on

    print(f"Size of header: {size_of_header} bytes")

    with open(to_file, "wb") as pak:
        pak.write(pack("<I", assets_count))

        offset = 0
        for _, asset in enumerate(assets):
            pak.write(pack("<64s", asset.path.encode("ascii")))
            pak.write(pack("<I", size_of_header + offset))
            offset += asset.size
        pak.write(magic_data)

    for asset in assets:
        with open(asset.path_posix, "rb") as f:
            with open(to_file, "ab") as pak:
                pak.write(f.read())


def main():
    parser = ArgumentParser()
    parser.add_argument("mode", choices=["pack", "unpack"])
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the input file or directory",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path to the input file or directory",
    )
    args = parser.parse_args()

    if args.mode == "unpack":
        if not os.path.exists(args.input):
            print(f"{args.input} does not exist")
            return
        unpack_assets(args.input, args.output)
        return

    elif args.mode == "pack":
        if not os.path.exists(args.input):
            print(f"{args.input} does not exist")
            return

        output = args.output.upper()
        if not output.endswith(".PAK"):
            output = f"{output}.PAK"
        pack_assets(args.input, output)
        return


if __name__ == "__main__":
    main()
