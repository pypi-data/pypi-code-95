# (c) Roxy Corp. 2021-
# Roxy AI Inspect-Server
import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from subprocess import call, run
import shutil
import colorama
from termcolor import cprint


# ==================================================================
# 各種定数定義
# ==================================================================
SCRIPT_NAME = Path(sys.argv[0])
SERVER_FOLDER = Path(__file__).parent.resolve()
venv_path = os.environ.get('VIRTUAL_ENV')
if venv_path:
    import roxyai_inspect
    module_path = Path(roxyai_inspect.__file__).absolute()
    SCRIPTS_FOLDER = Path(os.environ['VIRTUAL_ENV']) / 'Scripts'
    if Path(venv_path) in module_path.parents:
        # 通常インストールのPython仮想環境からの起動
        CHECKER_PATH = 'roxy_lic_checker.exe'
    else:
        # 開発用インストール（-eオプション）のPython仮想環境からの起動
        CHECKER_PATH = module_path.parent / 'roxy_lic_checker.exe'
else:
    # Python仮想環境外からの起動
    SCRIPTS_FOLDER = SERVER_FOLDER.parent.parent.parent / 'Scripts'
    CHECKER_PATH = SCRIPTS_FOLDER / 'roxy_lic_checker.exe'
VENV_ACTIVATE = SCRIPTS_FOLDER / 'activate.bat'
INSPECT_SERVER = SERVER_FOLDER / 'inspect_server.py'
SERVER_LICENSE = SERVER_FOLDER / 'pytransform/license.lic'
DEFAULT_CONFIG = SERVER_FOLDER / 'config/system_config.json'
parser = None

# デフォルトのフォルダ定義
SAMPLE_CONFIG = SERVER_FOLDER / 'config/sample/'
SETUP_FOLDER = {
    # フォルダの説明: デフォルトのフォルダ位置
    'プロジェクトトップ': '',
    'AIモデル格納      ': 'product',
    '検査結果格納      ': 'result',
    'ログ出力          ': 'log',
    'ログバックアップ  ': 'log/oldLog',
    '各種設定          ': 'config',
}
SETUP_FILES = {
    # コピー先ファイル名: コピー元Pathクラス
    'サーバー設定      ': ('config/system_config.json', SAMPLE_CONFIG / 'system_config.json'),
    '検査サーバログ設定': ('config/inspect_server_log.conf', SAMPLE_CONFIG / 'inspect_server_log.conf'),
    '分析サーバログ設定': ('config/analyze_server_log.conf', SAMPLE_CONFIG / 'analyze_server_log.conf'),
}
CONFIG_PATH = Path('config/system_config.json')


def setup_project():
    curdir = Path(os.getcwd())
    print()
    print('現在のフォルダ')
    cprint(f'  {curdir.as_posix()}', color='cyan')
    print('に、Roxy AI の検査プロジェクトを構築します。')
    cprint('    続けるには [Y] を入力してください >>> ', 'yellow', end='')
    answer = input('')
    if answer not in ('y', 'Y', 'yes', 'Yes', 'YES'):
        err_exit('プロジェクトの構築を中止します。', 0)
    print()
    print('フォルダを構築')
    for k, v in SETUP_FOLDER.items():
        path = curdir / v
        print(f' {k}: {path.as_posix()} ', end='')
        if path.exists():
            print('(既存利用)')
        else:
            # フォルダが存在しない場合
            try:
                path.mkdir(parents=True)
            except Exception as e:
                print(e)
                err_exit('フォルダが作成できません。', 10, path.as_posix())
            cprint('(新規作成)', color='yellow')
    print()
    print('ファイルを作成')
    for k, (dst, src) in SETUP_FILES.items():
        path = curdir / dst
        print(f' {k}: {path.as_posix()} ', end='')
        if path.exists():
            print('(既存利用)')
        if not path.exists():
            # フォルダが存在しない場合
            try:
                shutil.copy2(src, path)
            except Exception as e:
                print(e)
                err_exit(
                    'フォルダがコピーできません。', 11,
                    f'{src.as_posix()} -> {path.as_posix()}'
                )
            cprint('(新規作成)', color='yellow')
    print()
    print('デフォルト設定によるサンプルプロジェクトを構築しました。')
    print(f'設定を変更する場合には {CONFIG_PATH.as_posix()} を修正してください。')
    print()
    print('現在のフォルダ')
    cprint(f'  {curdir.as_posix()}')
    print('から')
    cprint(f'  {SCRIPT_NAME.name} {CONFIG_PATH.as_posix()}', color='cyan')
    print('で検査サーバを実行します。')
    print()
    sys.exit(0)


def show_title(title):
    """ スクリプトのタイトル表示（ログ記録無し）
    """
    cprint('--------------------------------------------------')
    cprint('Roxy ', 'blue', attrs=['bold'], end='')
    cprint('AI', 'white', attrs=['bold', 'dark'], end='')
    cprint(f' : {title}')
    cprint('                             (c) Roxy Corp. 2020- ')
    cprint('--------------------------------------------------')


def err_exit(message: str, errcode: int, description: str = ''):
    """ エラー終了
    """
    print()
    cprint(message, color='red')
    print(description)
    parser.print_usage()
    sys.exit(errcode)


def call_python(script, args=''):
    """ 仮想環境上でPythonのスクリプトを実行
    """
    command = (
        f'cmd /v:on /C "call {VENV_ACTIVATE} && '
        f'python {str(script)} {args}'
        f'"'
    )
    ret = call(command, shell=True)
    if ret != 0:
        raise RuntimeError(f'エラーコード {ret} が返りました。\nコマンド： "{command}"')
    return


def launch_server(config):
    """ Roxy AI Train-Server起動
    """
    try:
        call_python(INSPECT_SERVER, str(config))
    except Exception as e:
        err_exit('Roxy AI Inspect-Server の実行に失敗しました。', 1, str(e))


def check_license(regfile: Path):
    """ roxy_lic_checker.exe でライセンスファイルをチェック
    """
    start_server = True
    if regfile:
        if not regfile.exists():
            err_exit('ライセンスファイルが見つかりません。', 3, str(regfile.resolve()))

        # ライセンスファイルの上書き
        print('ライセンスファイル ', end='')
        cprint(str(regfile.resolve()), color='cyan', end='')
        print(' を登録します。')
        if SERVER_LICENSE.exists():
            print('古いライセンスファイルに上書きで登録します。')
            cprint('    続けるには [Y] を入力してください >>> ', 'yellow', end='')
            answer = input('')
            if answer in ('y', 'Y', 'yes', 'Yes', 'YES'):
                try:
                    SERVER_LICENSE.unlink()
                except Exception as e:
                    err_exit('古いライセンスファイルが削除できません。', 4, f'{SERVER_LICENSE}\n{e}')
            else:
                err_exit('ライセンスファイルの登録を中止します。', 0)
        try:
            shutil.copy2(str(regfile), str(SERVER_LICENSE))
        except Exception as e:
            err_exit('ライセンスファイルのコピーに失敗しました。', 5, f'{regfile} -> {SERVER_LICENSE}\n{e}')
        print('ライセンスファイルを登録しました。')
        start_server = False

    command = f'{CHECKER_PATH} -i {SERVER_LICENSE}'
    result = run(command)
    if result.returncode != 0:
        err_exit('有効なライセンスファイルが登録されていません。', -1)
    if not start_server:
        # ライセンス登録後はコマンド処理終了
        sys.exit(0)


def main():
    """ インストールされたモジュールのスクリプトエントリーポイント
    """
    global parser
    # タイトル表示
    colorama.init()
    show_title('Inspect-Server')

    # コマンド引数のパース
    parser = ArgumentParser(
        description="Roxy AI Inspect-Server",
        formatter_class=RawTextHelpFormatter,
        epilog=(
            "TensorFlowバージョンを切り替える場合は pip で以下の様に更新してください\n"
            "  pip install --upgrade roxyai-inspect[tf21]    ← TensorFlow 2.1.0 への切り替え\n"
            "  pip install --upgrade roxyai-inspect[tf24]    ← TensorFlow 2.4.0 への切り替え\n"
        ),
    )
    parser.add_argument('-l', '--license', type=Path, help='ライセンスファイル登録')
    parser.add_argument('-s', '--setup', action='store_true', help='プロジェクトフォルダのサンプル生成')
    parser.add_argument('config_file', nargs='?', default=DEFAULT_CONFIG.as_posix(), help='設定ファイル')
    args = parser.parse_args()

    # ライセンスチェック
    check_license(args.license)

    # プロジェクトフォルダ生成
    if args.setup:
        setup_project()

    # サーバ起動
    launch_server(Path(args.config_file))


if __name__ == "__main__":
    main()
