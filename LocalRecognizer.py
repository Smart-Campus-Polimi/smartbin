import os
import random
import torch
import torch.nn as nn
import numbers
import torchvision.transforms.functional as TF
from PIL import Image
from torchvision import models, transforms

import ResumableTimer as rt

MODEL_PATH = 'trained_model/tr_model.pth'
FOLDER_PATH = 'AllFotos/'

class MyCrop(object):
    def __init__(self, size):
        if isinstance(size, numbers.Number):
            self.size = (int(size), int(size))
        else:
            self.size = size

    def __call__(self, img):
        """
        Args:
            img (PIL Image): Image to be cropped.
            
            Returns:
                PIL Image: Cropped image.
                """
        return TF.crop(img, 0, 48, self.size[0], self.size[1])
    
    def __repr__(self):
        return self.__class__.__name__ + '(size={0})'.format(self.size)

data_transforms = {
    'test': transforms.Compose([
        transforms.Resize(256),
        MyCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.3, 0.36, 0.58], [0.23, 0.24, 0.29])
    ])
}
    
def pick_random_image():
    _randFolder = random.choice(os.listdir(FOLDER_PATH)) + "/"
    _randImg = _randFolder + random.choice(os.listdir(FOLDER_PATH + _randFolder))
    print('Choosing a {}'.format(FOLDER_PATH + _randImg))
    return FOLDER_PATH + _randImg

def LocalRecognizer():
    def __init__(self):
        elapsed_time = rt.ResumableTimer()

#        class_names = ['aluminium_can', 'aluminium_foil', 'aluminium_tray', 'glass_bottle', 'glass_jar', 'indifferent_empty', 'indifferent_lighter', 'indifferent_pen', 'paper_bag', 'paper_box', 'paper_card', 'paper_magazine', 'paper_newspaper', 'paper_piece', 'plastic_bag', 'plastic_bottle', 'plastic_bottle_cap', 'plastic_cup', 'plastic_cutlery', 'plastic_plate']
        material_class_names = ['PLASTIC', 'PLASTIC', 'PLASTIC', 'GLASS', 'GLASS', 'UNSORTED', 'UNSORTED', 'UNSORTED', 'PAPER', 'PAPER', 'PAPER', 'PAPER', 'PAPER', 'PAPER', 'PLASTIC', 'PLASTIC', 'PLASTIC', 'PLASTIC', 'PLASTIC', 'PLASTIC']
#        sorted_class_names = ['paper', 'aluminium/plastic', 'indifferent', 'glass']
        
        print('Running smart bin brain...')

        DEVICE = torch.device("cpu")
        model_ts = models.resnet18(pretrained=True)
        num_ftrs = model_ts.fc.in_features
        model_ts.fc = nn.Linear(num_ftrs, 20)
        model_ts.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model_ts.eval()
        model_ts = model_ts.to(DEVICE)
        

    def recognize(self, _image, _model):
        x = data_transforms['test'](Image.open(_image))
        x.unsqueeze_(0)
        x = x.to(self.DEVICE)
        output = _model(x)
        _, pred = torch.max(output, 1)
        confidence = torch.max(torch.exp(torch.nn.functional.log_softmax(output, dim=1)))
        print('It\'s a piece of {} with confidence {}'.format(self.material_class_names[pred]), confidence)
        if confidence < 0.75:
            return 'UNSORTED'
        else:
            return self.material_class_names[pred]


    def start_recognizer(self, image, model):
        self.elapsed_time.start()
        result = recognize(image, model)
        
        self.elapsed_time.pause()
        total_time = self.elapsed_time.get_actual_time()
        print('Test completed in {:.3f}s'.format(total_time))
        return result
    
    
    def getLabels(self, fileName):
        print("-----\nNEW LOCAL RECOGNITION REQUEST")
        waste = start_recognizer(fileName, self.model_ts)
        return waste

