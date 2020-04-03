import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import torchvision.transforms as transforms
import torchvision.models as models

class WSL(nn.Module):
    def __init__(self, layer=None):
        """Take WSL pretrained model up to layer n"""
        super(WSL, self).__init__()
        pretrained_model = torch.hub.load(
            "facebookresearch/WSL-Images", "resnext101_32x16d_wsl")
        for param in pretrained_model.parameters():
            param.requires_grad = False
        if layer is None:
            self.model = pretrained_model
        else:
            layers = list(pretrained_model.children())
            layers = layers[:layer] if layer is not None else layers
            self.model = nn.Sequential(*layers)
        
    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, start_dim=1)
        return x

class VGG16(nn.Module):
    def __init__(self, layer=None):
        """Take VGG16 pretrained model up to layer n"""
        super(VGG16, self).__init__()
        pretrained_model = models.vgg16(pretrained=True)
        for param in pretrained_model.parameters():
            param.requires_grad = False
        if layer is None:
            self.model = pretrained_model
        else:
            layers = list(pretrained_model.children())
            layers = layers[:layer] if layer is not None else layers
            self.model = nn.Sequential(*layers)
        
    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, start_dim=1)
        return x

class VGG16MultiLayer(nn.Module):
    def __init__(self):
        super(VGG16MultiLayer, self).__init__()
        self.model = models.vgg16(pretrained=True)
        for param in self.model.parameters():
            param.requires_grad = False
        
    def forward(self, x):
        N, C, H, W = x.shape
        
        e1 = torch.zeros(N, 64, 128, 128)
        e2 = torch.zeros(N, 128, 64, 64)
        e3 = torch.zeros(N, 256, 32, 32)
        e4 = torch.zeros(N, 512, 16, 16)
        e5 = torch.zeros(N, 512, 8, 8)

        l1 = list(self.model.children())[0][0] 
        l2 = list(self.model.children())[0][5] 
        l3 = list(self.model.children())[0][10]
        l4 = list(self.model.children())[0][17]
        l5 = list(self.model.children())[0][24]

        h1 = l1.register_forward_hook(lambda m, i, o: e1.copy_(o.data))
        h2 = l2.register_forward_hook(lambda m, i, o: e2.copy_(o.data))
        h3 = l3.register_forward_hook(lambda m, i, o: e3.copy_(o.data))
        h4 = l4.register_forward_hook(lambda m, i, o: e4.copy_(o.data))
        h5 = l5.register_forward_hook(lambda m, i, o: e5.copy_(o.data))

        self.model(x)

        e1 = nn.MaxPool2d(16)(e1)
        e2 = nn.MaxPool2d(8)(e2)
        e3 = nn.MaxPool2d(4)(e3)
        e4 = nn.MaxPool2d(2)(e4)
        #e5 = nn.MaxPool2d()(e5)

        fe1 = torch.flatten(e1, start_dim=1)
        fe2 = torch.flatten(e2, start_dim=1)
        fe3 = torch.flatten(e3, start_dim=1)
        fe4 = torch.flatten(e4, start_dim=1)
        fe5 = torch.flatten(e5, start_dim=1)
        output = torch.cat((fe1, fe2, fe3, fe4, fe5), 1)
        return output

    def compute_distance(self, X, Y):
        """If 'OMP: Error #15: Initializing libiomp5.dylib, [...]' => conda install nomkl"""
        # s1 = np.prod((64, 128, 128)).item()
        # s2 = np.prod((128, 64, 64)).item()
        # s3 = np.prod((256, 32, 32)).item()
        # s4 = np.prod((512, 16, 16)).item()
        # s5 = np.prod((512, 8, 8)).item()
        s1 = np.prod((64, 8, 8)).item()
        s2 = np.prod((128, 8, 8)).item()
        s3 = np.prod((256, 8, 8)).item()
        s4 = np.prod((512, 8, 8)).item()
        s5 = np.prod((512, 8, 8)).item()
        assert len(X.shape) == 2
        assert len(Y.shape) == 2
        assert X.shape[0] == Y.shape[0]
        assert X.shape[1] == Y.shape[1]
        assert X.shape[1] == s1+s2+s3+s4+s5

        p1 = np.linalg.norm(X[:,:s1] - Y[:,:s1], axis=1) / 5.3 * 2.5
        p2 = np.linalg.norm(X[:,s1:s2] - Y[:,s1:s2], axis=1) / 2.7 / 1.2
        p3 = np.linalg.norm(X[:,s2:s3] - Y[:,s2:s3], axis=1) / 1.35 / 2.3
        p4 = np.linalg.norm(X[:,s3:s4] - Y[:,s3:s4], axis=1) / 0.67 / 8.2
        p5 = np.linalg.norm(X[:,s4:] - Y[:,s4:], axis=1) / 0.16

        distance = (p1 + p2 + p3 + p4 + p5) / 5.0 / 8.0 #128.0
        return distance


class VGG19(nn.Module):
    def __init__(self, layer=None):
        """Take VGG19 pretrained model up to layer n"""
        super(VGG19, self).__init__()
        pretrained_model = models.vgg19(pretrained=True)
        for param in pretrained_model.parameters():
            param.requires_grad = False
        if layer is None:
            self.model = pretrained_model
        else:
            layers = list(pretrained_model.children())
            layers = layers[:layer] if layer is not None else layers
            self.model = nn.Sequential(*layers)
        
    def forward(self, x):
        x = self.model(x)
        x = torch.flatten(x, start_dim=1)
        return x

def forward(model, imgs, size=(224, 224)):
    """Input a list of PIL images in imgs and run a batch forward on them"""
    composed = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])
    embeddings = model(torch.stack([composed(img) for img in imgs], dim=0))
    return embeddings.numpy()

if __name__ == "__main__":
    # VGG16MultiLayer
    x_image = torch.randn(2, 3, 128, 128)
    model = VGG16MultiLayer()
    model.eval()
    with torch.no_grad():
        output = model(x_image)
        X, Y = output[0, ...].unsqueeze(0), output[1, ...].unsqueeze(0)
        d = model.compute_distance(X.numpy(), Y.numpy())
        print(d)

    # WSL
    x_image = torch.randn(1, 3, 128, 128)
    print("Initialize model...", end=" ")
    model = WSL(-10)
    model.eval()
    print("Start forward.", end=" ")
    with torch.no_grad():
        output = model(x_image)
    print(f"done: {output.shape}")
