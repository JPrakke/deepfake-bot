import boto3
import unittest
import json


class LambdaTest(unittest.TestCase):
    def test_invoke(self):

        client = boto3.client('lambda')

        test_data = {
            "data_uid": "420b0112ac3748b5b51a511ecd3b8738",
            "filters": "",
            "state_size": 3,
            "new_line": False,
            "number_responses": 100
        }

        payload = json.dumps(test_data)

        response = client.invoke(
            FunctionName='deepfake-bot-markovify',
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=payload,
        )

        res_str = response['Payload'].read().decode('utf-8')
        res_json = json.loads(res_str)

        if res_json['statusCode'] == 200:
            sample_responses = res_json['body']
            for i in sample_responses:
                print(i)


if __name__ == '__main__':
    unittest.main()
