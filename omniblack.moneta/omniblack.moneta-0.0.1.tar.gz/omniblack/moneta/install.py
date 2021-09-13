from omniblack.repo import find_root
from anyio import Path, run


hook_exec_name = 'write_change'
run_module = 'exec python -m poetry run python -m'


async def install():
    root: Path = await find_root()
    print(root)

    hook_dir = root/'devtools'/'git_hooks'/'pre-commit'
    await hook_dir.mkdir(exist_ok=True, parents=True)
    hook_file = hook_dir/hook_exec_name
    async with await hook_file.open('x') as file:
        await file.write('#! /usr/bin/sh\n')
        await file.write(
            f'{run_module} {__package__}.{hook_exec_name}'
        )

    # user read/execute
    # group/other readonly
    await hook_file.chmod(0o544)


def main():
    run(install)


if __name__ == '__main__':
    main()
