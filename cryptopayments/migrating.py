import os


def migrate():
    os.system('aerich init-db')
    os.system('aerich migrate')
    os.system('aerich upgrade')


if __name__ == '__main__':
    migrate()
