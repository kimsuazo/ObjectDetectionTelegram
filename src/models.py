import torch
from torchvision.models import resnet50
import torch.nn as nn
import os




class custom_resnet(nn.Module):
    def __init__(self):
          super(custom_resnet, self).__init__()
          self.num_classes =len(os.listdir(os.getcwd() + '/../images/'))
          self.base_model = resnet50(pretrained=True)
          for param in self.base_model.parameters():
              param.requires_grad = False

          in_features = self.base_model.fc.in_features
          #self.base_model.fc = nn.Linear(in_features, self.num_classes)
          
          self.base_model.fc = nn.Sequential(
                  nn.Dropout(),
                  nn.Linear(in_features, 128),
                  nn.ReLU(),
                  nn.Dropout(),
                  nn.Linear(128, self.num_classes),
                  nn.LogSoftmax(dim = 1)
                  )
          

    def forward(self, x):
        y = self.base_model(x)
        return y


if __name__ == '__main__':
    model = custom_resnet()
    dir(model)

