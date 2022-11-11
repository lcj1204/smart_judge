# -*- coding: utf-8 -*-
"""banana_vgg19.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cJtumn4ap9y4IodWcDmiPK5tEY2-Bu-g
"""

## pytorch install
### https://pytorch.kr/get-started/locally/
### conda install pytorch torchvision torchaudio -c pytorch

## PIL install
### pip install pillow

## pandas install
### pip install pandas

from PIL import Image
# from torchvision import transforms
import torch
import torch.nn as nn
import torch.nn.functional as F
# import pandas as pd

import json
from collections import OrderedDict

# model_path = './flask_api/tut4-model.pt'   # set model path (tut4-model.pt가 있는 디렉토리로 설정**)
# img_rotten_name = "rotten_banana_365.jpg"  # set file name
# img_rotten_path = "/content/drive/MyDrive/건국대학교/2022-2/종설/banana/for_test/" + img_rotten_name  # set path
# result_path = "/content/drive/MyDrive/건국대학교/2022-2/종설/banana/banana_four/"  # result csv파일 저장 path 설정


# model_path = './'   # set model path (tut4-model.pt가 있는 디렉토리로 설정**)
# # img_rotten_name = "rotten_banana_365.jpg"  # set file name
# img_rotten_name = "banana1.jpeg"  # set file name
# img_rotten_path = "./" + img_rotten_name  # set path
# result_path = "./result/"  # result csv파일 저장 path 설정


class VGG(nn.Module):
    def __init__(self, features, output_dim):
        super().__init__()

        self.features = features

        self.avgpool = nn.AdaptiveAvgPool2d(7)

        self.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, output_dim),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        h = x.view(x.shape[0], -1)
        x = self.classifier(h)
        return x, h


def get_vgg_layers(config, batch_norm):
    layers = []
    in_channels = 3

    for c in config:
        assert c == 'M' or isinstance(c, int)
        if c == 'M':
            layers += [nn.MaxPool2d(kernel_size=2)]
        else:
            conv2d = nn.Conv2d(in_channels, c, kernel_size=3, padding=1)
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(c), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = c

    return nn.Sequential(*layers)


def predict(img, img_name):
    from torchvision import transforms

    OUTPUT_DIM = 4  # label 종류
    banana_classes = {
        0: 'Green',
        1: 'Midripen',
        2: 'Overripen',
        3: 'Yellowish_Green'
    }

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')   # GPU 사용 가능 여부 체크

    vgg16_config = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512,
                    'M', 512, 512, 512, 'M']
    vgg16_layers = get_vgg_layers(vgg16_config, batch_norm=True)

    model = VGG(vgg16_layers, OUTPUT_DIM)

    model.to(device)
    # model.load_state_dict(torch.load(model_path+'tut4-model.pt', map_location=torch.device('cpu')))
    model.load_state_dict(torch.load('./flask_api/model/tut4-model.pt', map_location=torch.device('cpu')))
    model.eval()

    pretrained_size = (224, 224)
    pretrained_means = [0.485, 0.456, 0.406]
    pretrained_stds = [0.229, 0.224, 0.225]

    transforms = transforms.Compose([transforms.Resize(pretrained_size),
                                     transforms.ToTensor(),
                                     transforms.Normalize(mean=pretrained_means,
                                                          std=pretrained_stds)])

    img_rotten = transforms(Image.open(img)).unsqueeze(0)

    y_pred, _ = model(img_rotten.to(device))
    y_prob = F.softmax(y_pred, dim=-1)

    print(y_prob)
    print(torch.argmax(y_prob, 1))

    dictionary = {i: y_prob.cpu().detach().numpy()[0][i] for i in range(len(y_prob.cpu().detach().numpy()[0]))}
    dictionary_data_convert = {k:float(v) for k, v in dictionary.items()} # float 클래스로 값이 들어가 있는 value들을 float으로 바꿔줌

    result = OrderedDict()
    result["img_name"] = img_name
    result["banana_classes"] = banana_classes
    result["Probability"] = dictionary_data_convert
    result["argmax"] = torch.argmax(y_prob, 1).item() #banana_classes[torch.argmax(y_prob, 1).item()]
    print(result)

    # js = json.dumps(result, ensure_ascii=False, indent="\t")
    # print(js)

    return result

# if __name__ == "__main__":
#     # image = Image.open("./rotten_banana_365.jpg")
#     # image_name = "rotten_banana_365"
#     image = Image.open("./banana1.jpeg")
#     image_name = "banana1"
#     predict(image, image_name)