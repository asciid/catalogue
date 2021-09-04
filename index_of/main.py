
"""
TODO
[-] Создание пакета
[-] Интеграция с catalogue
"""

import os
import time


def super_round(number):
    precision = 0
    while round(number, precision) == 0:
        precision += 1

    return round(number, precision)


def generate_css(root):
    css_path = os.path.join(root, "style.css")

    with open(css_path, "w") as css:
        css.write("body { color: white; background: black; }")


def generate_page(path, is_root=False, is_bottom=False):
    index_path = os.path.join(path, "index.html")
    css_path = os.path.join(os.getcwd(), "style.css")

    if is_root:
        title = "/"
    else:
        title = path.split("/")[-1]

    with open(index_path, "w") as index:
        index.write("<html>")
        index.write("<head>")
        index.write("<link rel='stylesheet' href='{}'>".format(css_path))
        index.write("<title>{}</title>".format(title))
        index.write("</head>")
        index.write("<body>")

        if is_root:
            index.write("<h1>index of /</h1>")
        else:
            index.write("<h1>index of {}</h1>".format(os.path.join("/", path)))
            index.write("<p><a href='../index.html'>../<a></p>")

        if is_bottom:
            index.write("".join(
                ["<p><a href='{0}'>{0}</a></p>".format(entity)
                 for entity in os.listdir(path)
                 if not entity.endswith(".meta") and entity != "index.html"]
                )
            )
        else:
            index.write("".join(
                ["<p><a href='{0}/index.html'>{0}</a></p>".format(entity)
                 for entity in os.listdir(path)
                 if entity != "index.html"]
                )
            )

        index.write("</body>")
        index.write("</html>")


class IndexOf:

    running_time = 0
    termination_time = 0
    files_created = 0

    def __init__(self, source_root, target_root):
        start_time = time.time()
        files_created = 1

        old_directory = os.getcwd()

        if not os.path.exists(target_root):
            os.mkdir(target_root)
        os.chdir(target_root)

        cwd = os.getcwd()

        first = True
        root_dirs = []

        # Прогон для сканирования
        for a, b, c in os.walk(source_root):
            if first:
                first = False
                root_dirs = b
                continue

            if not c:
                for entity in b:
                    full_path = os.path.join(*os.path.join(a, entity).split("/")[-2:])

                    if not os.path.exists(full_path):
                        os.makedirs(full_path)

            if c and not b:
                lib_path = a
                index_path = os.path.join(*a.split("/")[-2:])

                for entity in os.listdir(lib_path):
                    if not entity.endswith(".meta") and entity != "index.html":
                        file_name = entity.split("/")[-1]

                        src_path = os.path.join(lib_path, entity)
                        end_path = os.path.join(index_path, file_name)

                        if not os.path.exists(end_path):
                            os.symlink(src_path, end_path)
                            files_created += 1

                generate_page(index_path, is_bottom=True)
                files_created += 1

        # Мы в каталоге root/
        generate_page(cwd, is_root=True)

        # Прогон для заполнения
        for directory in root_dirs:
            generate_page(directory)
            files_created += 1

        os.chdir(old_directory)

        self.termination_time = time.strftime("%D %H:%m:%S", time.localtime())
        self.running_time = super_round(time.time() - start_time)
        self.files_created = files_created


if __name__ == "__main__":
    root = "/home/ash/build/lib/root/"
    index = IndexOf(root, "root")

    print("Сканирование {} от {}:\nФайлов создано: {}\nВремя: {} с.".format(root, index.termination_time,
                                                                            index.files_created, index.running_time))
