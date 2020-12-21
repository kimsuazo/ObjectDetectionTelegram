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


def vid2frames(video):
    if video not in os.listdir(img_folder):
        video_path = input_folder + video
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count < 100:
            print("The video is too short!")
            os.remove(video_path)
            return None
        #print(f'Processing video at: {video_path}')
        interval = frame_count // 100
        #print(frame_count)

    if not cap.isOpened():
        print('Unable to capture video!')
    else:
        class_dir = img_folder + '/' + video
        os.mkdir(class_dir)
        print(f'New class folder created: {class_dir}')
        os.chdir(class_dir)
        i = 1
        saves = 0
        while(cap.isOpened() and saves<100):
            ret, frame = cap.read()
            if ret == False:
              break
            if i % interval == 0:
              cv2.imwrite(str(video) + '_' + str(saves) + '.jpg', frame)
              saves += 1
            i+=1
        cap.release()
        cv2.destroyAllWindows()
        os.chdir(root)
        print('-Images succesfully saved!-')
    os.remove(video_path)

if __name__ == '__main__':
    create_dataset_splits()