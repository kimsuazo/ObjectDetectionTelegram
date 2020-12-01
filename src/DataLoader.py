import os
from torch.utils.data import Dataset, DataLoader
import csv
from torchvision.transforms import transforms
#import utils
import torch.nn.functional as F
import torch
from PIL import Image
import time
from multiprocessing import Pool


class ODT_Dataset(Dataset):
    def __init__(self, split, dev = 'cpu'):
"""
Create a train, dev and test splits and forward the images through __getitem__ method. 
The splits will be 70/10/20 respectively for train/dev/test. 
As the dataset will be dynamic it will be necessary to rebuild the splits each time a training is launched
"""
        splits = ['train','test','dev']
        img_dir = os.listdir(os.getcwd()+'/../images'

        self.split = split
        if self.split not in splits:
            raise Exception('Split must be one of:', splits)

        self.device = dev
        #Paths
        self.img_dir = frames_path + self.split
        self.csv_path = csv_path
        self.csv_file = csv_path + self.split + ".csv"

        

        self.transform = transforms.Compose([transforms.Resize((112,112)),
                                transforms.ToTensor(),
                                transforms.Normalize(mean=[0.537,0.527,0.520],
                                                     std=[0.284,0.293,0.324])])



    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_fold = os.path.join(self.img_dir, self.samples[idx][0],"")
        #print(img_fold, type(img_fold))

        label = self.process_sentence(self.samples[idx][2], self.dictionary)

        if self.gloss:
            gloss_sent = self.process_sentence(self.samples[idx][1], self.gloss_dictionary)
            return (img_fold, gloss_sent, label)
        else:
            clips = self.make_clips(img_fold, self.long_clips, self.window_clips)
            return (clips, label)


    

if __name__ == '__main__':

    dataset = SNLT_Dataset(split = 'train')
    #train_loader = DataLoader(dataset, batch_size = 4, shuffle = False)

    #print(len(dataset))
    '''
    for i in range(10):
        clip, label = dataset[i]
        print(clip.size())
    '''
    start = time.time()
    sequence = dataset.make_clips('data/frames/images', long = 6, window = 2, max_len = 2)
    print(type(sequence),sequence.size())
    print('time loading images',time.time()-start)

    start = time.time()
    sequence = torch.load('data/tensors/images')
    print(type(sequence), sequence.size())
    print('time loading tensor',time.time()-start)
