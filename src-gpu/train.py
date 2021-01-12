import torch
import torch.nn as nn
import os
from tqdm import tqdm
import torch.nn as nn
import torch.optim as optim
import argparse
from DataLoader import ODT_Dataset
from torch.utils.data import DataLoader
from models import custom_resnet
import math
import time
import utils

device = torch.device("cpu")



def train_epoch(model, optimizer, criterion, train_loader, epoch, epochs, device):

    # train
    model.train()
    train_loop = tqdm(train_loader, unit=" batches")  # For printing the progress bar
    for data, target in train_loop:
        train_loop.set_description('[TRAIN] Epoch {}/{}'.format(epoch + 1, epochs))
        data, target = data.float().to(device), target.to(device)
        #target = target.unsqueeze(-1)
        optimizer.zero_grad()
        output = model(data)
        #print(output.shape, target.shape)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

def test_epoch(model,test_loader, epoch, epochs, device):

    # test
    acc = 0
    model.eval()
    test_loop = tqdm(test_loader, unit="batches")  # For printing the progress bar
    with torch.no_grad():
        for data, target in test_loop:
            test_loop.set_description('[TEST] Epoch {}/{}'.format(epoch + 1, epochs))
            data, target = data.float().to(device), target.to(device)
            output = model(data)
            acc += correct_predictions(output, target)
    acc = 100. * acc / len(test_loader.dataset)
    print(f'Test accuracy of {math.trunc(acc)}')
    return math.trunc(acc)

def correct_predictions(predicted_batch, label_batch):
    pred = predicted_batch.argmax(dim=1, keepdim=True) # get the index of the max log-probability
    acum = pred.eq(label_batch.view_as(pred)).sum().item()
    return acum

def train_telegram(num_epochs = 15, batch_size = 32, num_workers = 2):
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(device)
    #Create CSV files
    utils.create_dataset_splits(70,30,0)

    #Instantiate datasets
    train_dataset = ODT_Dataset('train', device)
    test_dataset = ODT_Dataset('dev', device)

    train_loader = DataLoader(train_dataset, batch_size, shuffle = True, num_workers = num_workers)
    test_loader = DataLoader(test_dataset, batch_size, num_workers = num_workers)

    #Loss
    loss = nn.NLLLoss()

    #Model
    model = custom_resnet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    #Training parameters
    best_acc = 0

    #Train by epochs
    for epoch in range(num_epochs):
        train_epoch(model, optimizer, loss, train_loader, epoch, num_epochs, device)
        acc = test_epoch(model, test_loader, epoch, num_epochs, device)
        if acc >= best_acc:
            best_acc = acc
            torch.save(model.state_dict(), os.getcwd() + "/trained_models/last_trained_model")
    return(best_acc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pipeline execution')
    parser.add_argument('-e', '--num_epochs', type=int, default=1, help='Number of epochs')
    parser.add_argument('-b', '--batch_size', type=int, default=5, help='Batch size')
    parser.add_argument('-t', '--test', default=True, help='Test the model during training')
    parser.add_argument('-mp', '--model_name', default="last_trained_model", help='Location of saved tf.summary')
    args = parser.parse_args()

    utils.create_dataset_splits(70,0,30)

    train_dataset = ODT_Dataset(split = 'train')
    train_loader = DataLoader(train_dataset, batch_size = 5, shuffle = True)
    if args.test:
        test_dataset = ODT_Dataset(split = 'test')
        test_loader = DataLoader(test_dataset, batch_size=1)

    #describe_dataset(train_dataset)

    #loss = nn.CrossEntropyLoss()
    loss = nn.NLLLoss()
    model = custom_resnet()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    loss = nn.CrossEntropyLoss()
    acc = 0
    best_acc = 0
    for epoch in range(args.num_epochs):
        train_epoch(model, optimizer, loss, train_loader, args.num_epochs)
        if args.test:
            test_epoch(model, test_loader, args.num_epochs, acc)
        if acc>best_acc:
            best_acc = acc
    torch.save(model.state_dict(), os.getcwd() + "/trained_models/" + args.model_name)
