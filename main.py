import argparse
import asyncio
from aiopath import AsyncPath
from aioshutil import move


output_folder = AsyncPath()


async def del_empty_folders(folder: AsyncPath) -> bool:
    async for el in folder.iterdir():
        if await el.is_dir():
            if await del_empty_folders(el):
                await el.rmdir()
        else:
            return False
    return True


async def get_arguments() -> tuple[AsyncPath, AsyncPath]:
    """
    --source [-s] folder
    --output [-o]
    """
    # global base_folder, output_folder

    parser = argparse.ArgumentParser(description='Sorting folder')
    parser.add_argument('--source', '-s', help='Source folder', required=True)
    parser.add_argument('--output', '-o', help='Output folder (default="sorted_trash")', default='sorted_trash')
    args = vars(parser.parse_args())

    base_folder_ = AsyncPath(args.get('source'))
    if not (await base_folder_.exists()):
        print(f"Don't exist folder {base_folder_}")
        quit()

    output_folder_ = AsyncPath(args.get('output'))
    if not (await make_folder(output_folder_)):
        quit()

    return base_folder_, output_folder_


async def read_folder(path: AsyncPath) -> None:
    async for el in path.iterdir():
        if await el.is_dir():
            await read_folder(el)
        else:
            await move_file(el)


async def make_folder(folder: AsyncPath) -> bool:
    try:
        await folder.mkdir(exist_ok=True, parents=True)
    except OSError as err:
        print(err)
        return False
    return True


async def move_file(file: AsyncPath) -> None:
    # print(f'moving_files: {file}')
    global output_folder
    ext = file.suffix
    new_path = output_folder / ext
    if await make_folder(new_path):
        await move(file, new_path / file.name)


async def main():
    global output_folder
    base_folder, output_folder = await get_arguments()
    await read_folder(base_folder)
    await del_empty_folders(base_folder)
    print(f'Folder "{base_folder}" cleaned and files sorted in ".\\{output_folder}"')


if __name__ == '__main__':
    asyncio.run(main())
