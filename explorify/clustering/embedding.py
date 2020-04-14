import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import torchvision.transforms as transforms
import torchvision.models as models


class WSL(nn.Module):
    def __init__(self, layer=None, gpu=False):
        """Take WSL pretrained model up to layer n"""
        super(WSL, self).__init__()
        pretrained_model = torch.hub.load("facebookresearch/WSL-Images", "resnext101_32x16d_wsl")
        if layer is None:
            self.model = pretrained_model
        else:
            layers = list(pretrained_model.children())
            layers = layers[:layer]
            self.model = nn.Sequential(*layers)
        self.model.eval()
        if gpu:
            self.model.float().cuda()
        
    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, start_dim=1)
        return x


class VGG16(nn.Module):
    def __init__(self, layer=None, gpu=False):
        """Take VGG16 pretrained model up to layer n"""
        super(VGG16, self).__init__()
        pretrained_model = models.vgg16(pretrained=True)
        if layer is None:
            self.model = pretrained_model
        else:
            layers = list(pretrained_model.children())
            layers = layers[:layer]
            self.model = nn.Sequential(*layers)
        self.model.eval()
        if gpu:
            self.model.float().cuda()
        
    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, start_dim=1)
        return x


def forward(model, imgs, size=(224, 224), gpu=False):
    """Input a list of PIL images in imgs and run a batch forward on them"""
    composed = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])
    images_ready = torch.stack([composed(img) for img in imgs], dim=0)
    if gpu:
        torch.cuda.empty_cache()
        model.float().cuda()
        images_ready = images_ready.float().cuda()
    embeddings = model(images_ready)
    return embeddings.cpu().numpy()


if __name__ == "__main__":
    # WSL
    x_image = torch.randn(1, 3, 128, 128)
    print("Initialize model...", end=" ")
    model = WSL(layer=-10)
    model.eval()
    print("Start forward.", end=" ")
    with torch.no_grad():
        output = model(x_image)
    print(f"done: {output.shape}")
