import os


def main():
    current_path = os.path.abspath(os.curdir)

    os.chdir(current_path)


if __name__ == '__main__':
    main()
