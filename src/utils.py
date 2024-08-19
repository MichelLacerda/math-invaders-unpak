import os
from pathlib import Path, PureWindowsPath
from collections import namedtuple


AssetHeader = namedtuple("AssetHeader", ["num_assets", "assets"])
AssetUnpackType = namedtuple("Asset", ["path", "offset", "size"])
AssetPackType = namedtuple("Asset", ["path_posix", "path", "size"])


def print_asset_info_header():
    header = f"| {'Path':<64} | {'Offset':>10} | {'Size':>10} |"
    print("-" * len(header))
    print(header)
    print("-" * len(header))


def print_asset_info(asset: AssetUnpackType):
    print(f"| {asset.path:<64} | {asset.offset:>10} | {asset.size:>10} |")


def list_assets(assets: list[AssetUnpackType]):
    print_asset_info_header()
    for asset in assets:
        print_asset_info(asset)


def get_assets_from_path(from_path: str) -> list[AssetUnpackType]:
    paths = []
    for dirpath, _, filenames in os.walk(from_path):
        for f in filenames:
            filepath = os.path.join(dirpath, f)
            path_posix = Path(filepath)
            path_windows_fixed = filepath.replace(from_path, "").lstrip("\\")
            path_windows = str(PureWindowsPath(path_windows_fixed)).ljust(64, "\x00")
            size = os.path.getsize(filepath)
            paths.append(AssetPackType(path_posix, path_windows, size))
    return paths
