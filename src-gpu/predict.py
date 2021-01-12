import torch
import torch.nn as nn
import torch.nn.functional as F
import os
from tqdm import tqdm
import torch.nn as nn
import torch.optim as optim
import torchvision.utils
import numpy as np
import matplotlib.pyplot as plt
import argparse
from DataLoader import ODT_Dataset
from torch.utils.data import DataLoader
from models import custom_resnet
import math
import time
from PIL import Image
from torchvision.transforms import transforms



def predict(input, weights_path):
    model = custom_resnet()
    model.load_state_dict(torch.load(weights_path))
    model.eval()
    #predictions = F.softmax(model(input), dim=0).detach()
    predictions = model(input).detach()
    predictions = torch.exp(predictions)

    index_list = torch.argmax(predictions, dim=1).numpy()

    classes_list = os.listdir(os.getcwd()+ '/../images/')
    classes_list.sort()

    dict_classes = {i : classe for i,classe in enumerate(classes_list)}
    
    output = [(dict_classes[i], prediction[i]) for i, prediction in zip(index_list, predictions.numpy())]

    return output

def predict_telegram(image):

    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(device)
    img = Image.open(image)
    transformations = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    img_tensor = transformations(img)
    img_tensor = img_tensor.unsqueeze(0).to(device)
    model = custom_resnet()
    model.load_state_dict(torch.load(os.getcwd() + "/trained_models/last_trained_model"))
    model.to(device)
    model.eval()
    prediction = model(img_tensor)
    prediction = torch.exp(prediction)

    index = torch.argmax(prediction).item()

    classes_list = os.listdir(os.getcwd()+ '/../images/')
    classes_list.sort()
    dict_classes = {i : classe for i,classe in enumerate(classes_list)}

    return dict_classes[index], prediction[0][index]

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
    parser = argparse.ArgumentParser(description='Pipeline execution')
    parser.add_argument('-mn', '--model_name', default="last_trained_model", help='Location of saved tf.summary')
    args = parser.parse_args()

    train_dataset = ODT_Dataset(split = 'test')
    
    train_loader = DataLoader(train_dataset, batch_size = 5, shuffle = True)

    
    # Get a batch of training data
    inputs, classes = next(iter(train_loader))
    predictions = predict(inputs, os.getcwd() + "/trained_models/" + args.model_name)
    

    # Make a grid from batch
    out = torchvision.utils.make_grid(inputs)

    print(predictions)
    print(classes)
    #imshow(out, title=[x[0] for x in predictions])
