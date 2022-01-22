from subprocess import call
import keep_alive
from multiprocessing import Process


def bot():
    call(["python", "Gold.py"])


def main():
    keep_alive.keep_alive()

    to_start = Process(target=bot)
    to_start.start()

    call(["python", "activity.py"])


if __name__ == "__main__":
    main()
