import os
from torch.utils.data import Dataset, DataLoader
import torchvision.utils
import csv
from torchvision.transforms import transforms
import utils
import torch
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


class ODT_Dataset(Dataset):
    def __init__(self, split, dev = 'cpu'):
        """
        Create a train, dev and test splits and forward the images through __getitem__ method. 
        The splits will be 70/10/20 respectively for train/dev/test. 
        As the dataset will be dynamic it will be necessary to rebuild the splits each time a training is launched
        """
        self.samples = []

        splits = ['train','test','dev']

        self.split = split
        if self.split not in splits:
            raise Exception('Split must be one of:', splits)

        self.csv_file = os.getcwd() + "/../annotations/" + self.split + ".csv"
        self.device = dev        

        #TODO: Define the needed transformations for the selected model.
        #TODO: find the correct mean and std
        self.transform = transforms.Compose([transforms.Resize(256),
                                            transforms.CenterCrop(224),
                                            transforms.ToTensor()])

        #Open the csv file and extract img_path and label
        with open(self.csv_file) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                self.samples.append((row[0], row[1]))


    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        
        img = Image.open(self.samples[idx][0])
        img_tensor = self.transform(img)
        label = self.samples[idx][1]

        return (img_tensor, label)

def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(10)  # pause a bit so that plots are updated
    

if __name__ == '__main__':
    plt.ion()   # interactive mode

    utils.create_dataset_splits()
    train_dataset = ODT_Dataset(split = 'train')
    
    
    print("Number of training samples: {}".format(len(train_dataset)))
    for i in range(2):
        img, label = train_dataset[i]
        print(img)
        print(img.size())
        print(label)
    
    
    train_loader = DataLoader(train_dataset, batch_size = 5, shuffle = False)

    
    # Get a batch of training data
    inputs, classes = next(iter(train_loader))

    # Make a grid from batch
    out = torchvision.utils.make_grid(inputs)

    imshow(out, title=[x for x in classes])
