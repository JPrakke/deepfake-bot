import sys
from training import basic_job


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python train.py <data_id> <model_path> <"filter1,filter2,...">')
    else:
        data_id = sys.argv[1]
        model_path = sys.argv[2]
        filters = sys.argv[3]
        basic_job.train(data_id, model_path, filters)
