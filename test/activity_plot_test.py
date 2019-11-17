import unittest
import gzip
import random
from lambdas.activity.lambda_activity import *


class ActivityTest(unittest.TestCase):
    def test_date_ranges(self):
        """Tests activity plot function for different numbers of days"""
        for i in range(1, 100):
            with gzip.open(f'./tmp/{i}-test-channels.csv.gz', 'wb') as f:
                f.write('timestamp,channel\n'.encode())
                for t in range(i):
                    ts = dt.datetime.timestamp(dt.datetime.now() + dt.timedelta(t))
                    for n in range(int(random.random() * 10) + 1):
                        line = f'{int(ts) + n},general\n'
                        f.write(line.encode())

            data_id = f'{i}-test'
            image_uid = f'{i}-test'
            user_name = 'test user'
            time_series_chart(data_id, image_uid, user_name)


if __name__ == '__main__':
    unittest.main()
