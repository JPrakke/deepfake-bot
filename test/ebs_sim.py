import unittest
import sys
import threading
import time
import bot


def spawn_robot(test_id):
    print("Starting robot for test...")
    bot.application()
    print(f"Robot started. Test ID: {test_id}")


class SimulateEBS(unittest.TestCase):
    def test_one_bot(self):
        with self.assertRaises(SystemExit):
            thread_1 = threading.Thread(target=spawn_robot, args=(0,))
            thread_1.start()
            time.sleep(5)
            sys.exit()

        self.tearDown()

    def test_start_twice(self):
        """"Simulates an issue with EBS where WSGI was trying to start the bot twice"""
        with self.assertRaises(SystemExit):
            thread_1 = threading.Thread(target=spawn_robot, args=(1,))
            thread_2 = threading.Thread(target=spawn_robot, args=(2,))
            thread_1.start()
            thread_2.start()
            sys.exit()

        self.tearDown()


if __name__ == '__main__':
    unittest.main()

