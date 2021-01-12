import csv
import os
import random
import cv2

def create_dataset_splits(train_split = 70, dev_split = 10, test_split = 20):

    if (train_split + dev_split + test_split) != 100:
        raise Exception('Splits must sum 100')

    train_split = train_split/10
    dev_split = dev_split/10 + train_split
    test_split = test_split/10 + dev_split

    img_dir = os.getcwd() + '/../images/'

    #Create three arrays of suffled samples for each split.
    train_samples = []
    dev_samples = []
    test_samples = []

    for label in os.listdir(img_dir):
        
        img_list = os.listdir(os.path.join(img_dir, label))
        random.shuffle(img_list)

        i=0
        for img in img_list:
            img_path = os.path.join(img_dir, label, img)
            if train_split <= i < dev_split:
                dev_samples.append((img_path, label))
            elif dev_split <= i:
                test_samples.append((img_path, label))
            else:
                train_samples.append((img_path, label))

            i+=1
            if i==10:
                i=0

    #Generate three csv files, each one for each split

    train_path = os.getcwd() + "/../annotations/train.csv"
    dev_path = os.getcwd() + "/../annotations/dev.csv"
    test_path = os.getcwd() + "/../annotations/test.csv"


    with open(train_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for sample in train_samples:
            writer.writerow(sample)
    with open(dev_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for sample in dev_samples:
            writer.writerow(sample)
    with open(test_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for sample in test_samples:
            writer.writerow(sample)


def video2frames(video_path, class_directory, class_name):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not cap.isOpened():
        print('Unable to capture video!')
    else:

        num_frame = len(os.listdir(class_directory))
        i = 10
        interval = 10
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
              break
            if i % interval == 0:
              cv2.imwrite(class_directory + "/{}_{}.jpg".format(class_name, num_frame), frame)
              num_frame += 1
            i+=1
        cap.release()
        cv2.destroyAllWindows()
    os.remove(video_path)

if __name__ == '__main__':
    create_dataset_splits()