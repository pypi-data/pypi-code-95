"""
Микросервис
"""

# pylint: disable= no-else-return
# Отключено, т.к. ловим ошибку при возврате на основную страницу после работы функций relogin,
# rename и т.д.


# pylint: disable= too-many-nested-blocks
# Отлючено, т.к. для работы необходимо большое количество вложенных блоков

# pylint: disable= redefined-outer-name
# Отлючено для удобства чтения функций загрузки страниц web-приложения

# pylint: disable= too-many-return-statements
# Отлючено для удобства обработки исключений при вызове функции flash()

# pylint: disable= no-member

import argparse
import os
from fileinput import FileInput
from flask import Flask, render_template, request, flash
import slush_list


UPLOAD_FOLDER = './group_lists'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config.from_json('microservice_cfg.json')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some_secret'


@app.route('/', methods=['GET', 'POST'])
def index():
    """Основная страница web-приложения"""

    if request.method == 'POST':
        fullname = request.form.get('fullname')

        if fullname == '':

            message = 'fullname не введен'

            flash(message, category='error')

            return render_template("index.html")

        cheak_name = fullname.split('-')

        if len(cheak_name) < 4:

            message = 'Неверно введенный fullname'

            flash(message, category='error')

            return render_template("index.html")

        if not get_stud(fullname):

            message = 'fullname не найден'

            flash(message, category='error')

            return render_template("index.html")

        else:

            info = get_stud(fullname).copy()

            return render_template('getstud.html', info=info)

    else:

        return render_template("index.html")


groups_dir = {}
groups_addr = {}


def allowed_file(check_file):
    """Функция проверки формата загруженного файла

    Args:
        check_file:  Имя файла

    """

    return '.' in check_file and \
           check_file.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/load', methods=['GET', 'POST'])
def load():
    """Страница загрузки списка группы"""

    if request.method == 'POST':
        year = request.form.get('year')
        number = request.form.get('number')
        file = request.files.get('file')

        print(file)

        if year is None:

            message = 'Не указан год поступления'
            flash(message, category='error')

            return render_template("load.html")

        if number == '':

            message = 'Не указан порядковый номер группы'
            flash(message, category='error')

            return render_template("load.html")

        if file and allowed_file(file.filename):

            filename = f"{year}-{number}.txt"

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            load_list = slush_list.Students(year, number)
            key = f"{year}-{number}"
            if key in groups_dir:

                message = "Группа с таким названием уже загружена"

                flash(message, category='error')

                return render_template("load.html")

            if load_list.read_slush(f"{UPLOAD_FOLDER}/{filename}"):

                group_name = load_list.load_slush()
                groups_dir[group_name] = load_list

                message = 'Группа загружена'

                flash(message, category='success')

                return render_template("load.html")
            else:

                os.remove(f"{UPLOAD_FOLDER}/{filename}")

                message = "Введенные данные указаны неверно"

                flash(message, category='error')

                return render_template("load.html")
        else:

            message = "Неверный формат файла"

            flash(message, category='error')

            return render_template("load.html")

    else:
        return render_template("load.html")

    return render_template("index.html")


@app.route('/list')
def grouplist():
    """Cтраница со спискаком загруженных групп"""

    groups_lists = os.listdir(UPLOAD_FOLDER)

    for name in groups_lists:
        if name =='.DS_Store':
            groups_lists.remove(name)

    groups = []

    for filename in groups_lists:
        gr_number = filename.split('.')[0]

        groups.append(gr_number)

    return render_template("list.html", groups=groups)


@app.route('/list/<string:number>')
def slushlist(number):
    """Страница, отображающая список загруженных слушателей
       в определенной группе """

    sl_list = []
    slush = []

    with open(f"{UPLOAD_FOLDER}/{number}.txt", 'r') as fl_link:
        for line in fl_link:

            if line[0] == "#":
                continue

            fio, fullname, login = line.split(';')
            login = login[:-1]
            del fio

            slush.append(fullname)
            slush.append(login)
            sl_list.append((list(slush)))

            slush.clear()

    return render_template("sllist.html", sl_list=sl_list, number=number)


@app.route('/delete', methods=['GET', 'POST'])
def delete_group():
    """страница удаления загруженной группы"""

    if request.method == 'POST':
        group = request.form.get('group')

        if group == '':

            message = 'Не указана группа'
            flash(message, category='error')

            return render_template("groupdel.html")

        try:
            del groups_dir[group]

            os.remove(f"./group_lists/{group}.txt")

            message = 'Группа удалена'

            flash(message, category='success')

            return render_template("groupdel.html")

        except KeyError:

            message = "Введенный номер группы отсутствует в списке"

            flash(message, category='error')

            return render_template("groupdel.html")

    return render_template("groupdel.html")


@app.route('/relogin', methods=['GET', 'POST'])
def relogin():
    """страница изменения login слушателя"""

    group = list(groups_dir.keys())

    if request.method == 'POST':
        number_group = request.form.get('group')
        old_login = request.form.get('old_login')
        new_login = request.form.get('new_login')

        if number_group is None:

            message = 'Не указана группа'
            flash(message, category='error')

            return render_template("relogin.html", group=group)

        if old_login == '':

            message = 'Не указан старый login'
            flash(message, category='error')

            return render_template("relogin.html", group=group)

        if new_login == '':

            message = 'Не указан новый login'
            flash(message, category='error')

            return render_template("relogin.html", group=group)

        try:
            groups_dir[number_group].relogin(old_login, new_login)

            for line in FileInput(f"{UPLOAD_FOLDER}/{number_group}.txt", inplace=True):
                login = line.split(';')
                login[2] = login[2][:-1]
                if login[2] == old_login:
                    login[2] = new_login + '\n'
                    line = ';'.join(login)
                print(line, end='')

            message = 'Login изменен'

            flash(message, category='success')

            return render_template("relogin.html", group=group)

        except ValueError:

            message = "Введенный login отсутствует в списке"

            flash(message, category='error')

            return render_template("relogin.html", group=group)

    else:

        return render_template("relogin.html", group=group)


@app.route('/rename', methods=['GET', 'POST'])
def rename():
    """Страница изменения fullname слушателя"""

    group = list(groups_dir.keys())

    if request.method == 'POST':
        number_group = request.form.get('group')
        login = request.form.get('login')
        new_name = request.form.get('new')

        if number_group is None:

            message = 'Не указана группа'
            flash(message, category='error')

            return render_template("rename.html", group=group)

        if login == '':

            message = 'Не указан login'
            flash(message, category='error')

            return render_template("rename.html", group=group)

        if new_name == '':

            message = 'Не указан новый fullname'
            flash(message, category='error')

            return render_template("rename.html", group=group)

        gr_year, gr_num = number_group.split('-')

        new_fullname = new_name.split('-')

        if gr_year != new_fullname[0]:

            message = 'Не верно указан год поступления в новом fullname'
            flash(message, category='error')

            return render_template("rename.html", group=group)

        if gr_num != new_fullname[1]:

            message = 'Не верно указан порядковый номер группы в новом fullname'
            flash(message, category='error')

            return render_template("rename.html", group=group)

        try:
            if groups_dir[number_group].rename(login, new_name):

                for line in FileInput(f"{UPLOAD_FOLDER}/{number_group}.txt", inplace=True):
                    fullname = line.split(';')
                    fullname[2] = fullname[2][:-1]
                    if fullname[2] == login:
                        fullname[1] = new_name
                        line = ';'.join(fullname) + '\n'
                    print(line, end='')

                message = 'Fullname изменен'

                flash(message, category='success')

                return render_template("rename.html", group=group)

            else:

                message = "Новый fullname введен некорректно"

                flash(message, category='error')

                return render_template("rename.html", group=group)

        except ValueError:

            message = "Введенный login отсутствует в списке"

            flash(message, category='error')

            return render_template("relogin.html", group=group)
    else:

        return render_template("rename.html", group=group)


@app.route('/repos', methods=['GET', 'POST'])
def repos():
    """Страница со списками репозиториев"""

    group = list(groups_dir.keys())

    if request.method == 'POST':
        choice = request.form.get('choice')
        number_group = request.form.get('group')
        repo_name = request.form.get('repo_name')

        if choice is None:

            message = 'Не указана операция'
            flash(message, category='error')

            return render_template("getrepos.html", group=group)

        if number_group == '':

            message = 'Не указана группа'
            flash(message, category='error')

            return render_template("getrepos.html", group=group)

        if repo_name == '':

            message = 'Не указано имя репозитория или группы'
            flash(message, category='error')

            return render_template("getrepos.html", group=group)

        sl_list = []

        if choice == 'repo':
            flag = '-r'
            sl_list = get_repos(number_group, repo_name, flag)

            return render_template("showrepos.html", group=number_group, sl_list=sl_list)

        elif choice == 'group':
            flag = '-g'
            sl_list = get_repos(number_group, repo_name, flag)

            return render_template("showgroups.html", group=number_group, sl_list=sl_list)

        return None

    else:

        return render_template("getrepos.html", group=group)


def create_args():
    """Функция создания аргуметов аргументов командной строки"""

    par = argparse.ArgumentParser(description='read slush_list')

    par.add_argument('-t', '--token', help="token")
    par.add_argument('-l', '--load', help="loading group")
    par.add_argument('-y', '--year', help="year of admission")
    par.add_argument('-n', '--number', help="group number")
    par.add_argument('-gs', '--getstud', help="search student")
    par.add_argument('-rl', '--relog', nargs="+", help="login change")
    par.add_argument('-rn', '--rename', nargs="+", help="fullname change")
    par.add_argument('-r', '--repo', nargs="+", help="name repo")
    par.add_argument('-g', '--group', nargs="+", help="name group with stud")
    par.add_argument('-sh', '--show', help="show group")

    return par


def get_stud(fullname):
    """
    Функция поиска слушателя по шаблону

    Args:
          fullname:   fullname слушателя, которого нужно найти

    Returns:
          True for success, False otherwise.
    """

    summ = 0

    mass = []

    for key in groups_dir:
        for line in groups_dir[key].show_list():
            if fullname in line.show_fullname():
                print(f"fullname ->{line.show_fullname()}\n"
                      f"login -> {line.show_login()}")
                print("Рабочий репозиторий -> ", end='')
                # https://gitwork.com для примера
                print(f"https://gitwork.ru/{line.show_login()}")

                mass.append(line.show_fullname())
                mass.append(line.show_login())
                mass.append(f"https://gitwork.ru/{line.show_login()}")

                return mass
            summ += 1
        summ = 0

    return False


def get_repos(num_group, repo_name, flags):
    """
    Функция получения списка репозиториев

    Args:
        num_group:  Номер группы
        repo_name:  имя репозитория
        flags:      флаг, необходимый для выбора режима работы

    Returns:
             True for success

    Raises:
             KeyError:  Неверно указан номер группы
    """

    mass = []
    temp_mass = []

    try:
        if flags == "-r":
            for line in groups_dir[num_group].show_list():
                # https://gitwork.com для примера
                login = line.show_login()
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}")
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}/-/issues")
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}/-/milestones")

                mass.append(list(temp_mass))
                temp_mass.clear()

        elif flags == "-g":
            for line in groups_dir[num_group].show_list():
                # https://gitwork.com для примера
                fullname = line.show_fullname()
                mass.append(f"https://gitwork.ru/{repo_name}/{fullname}")

        return mass

    except KeyError as repo_ex:
        print(repo_ex)
        raise


if __name__ == '__main__':

    parser = create_args()
    args = parser.parse_args()

    if args.year or args.number or args.load:

        parser_list = slush_list.Students(args.year, args.number)
        parser_list.read_slush(args.load)

        groups_dir[parser_list.load_slush()] = parser_list

        if args.relog or args.rename or args.getstud or args.repo or args.group:

            if args.relog:
                parser_list.relogin(args.relog[0], args.relog[1])

            if args.rename:
                parser_list.rename(args.rename[0], args.rename[1])

            if args.getstud:
                get_stud(args.getstud)

            if args.repo:
                FLAG = '-r'
                rep = get_repos(args.repo[0], args.repo[1], FLAG)

                for elem in rep:
                    print(f"{elem[0]}\t{elem[1]}\t{elem[2]}\n")

            if args.group:
                FLAG = '-g'
                gr = get_repos(args.group[0], args.group[1], FLAG)
                print('\n'.join(gr))

    else:

        groups_lists = os.listdir(UPLOAD_FOLDER)

        for name in groups_lists:
            if name == '.DS_Store':
                groups_lists.remove(name)

        for file in groups_lists:
            filename = file.split('.')[0]

            gr_number = filename.split('-')

            year = gr_number[0]
            number = gr_number[1]

            start_slush = slush_list.Students(year, number)

            if start_slush.read_slush(f"{UPLOAD_FOLDER}/{file}"):

                group_name = start_slush.load_slush()
                groups_dir[group_name] = start_slush

        app.run(debug=True, host='0.0.0.0')
