import torch
import os
import pandas as pd
from PIL import Image

class VOCDataset(torch.utils.data.Dataset):
    def __init__(self, csv_file, img_idr, label_idr, S=7, B=2, C=20, transform=None):
        self.annotations = pd.read_csv(csv_file)
        self.img_dir = img_idr
        self.label_dir = label_idr
        self.S = S
        self.B = B
        self.C = C
    
    def __len__(self):
        return len(self.annotations)

    def __getitetm__(self, index):
        label_path = os.path.join(self.label_dir, self.annotations.iloc[index,1])
        boxes = []
        with open(label_path) as f:
            for label in f.readlines():
                cls_label, x, y, w, h = [
                    float(x) if float(x) != int(float(x)) else int(x)
                    for x in label.replace("\n", " ").split()
                ]

                boxes.append([cls_label, x, y, w, h])

        img_path = os.path.join(self.img_dir, self.annotations.iloc[index, 0])
        image = Image.open(img_path)
        boxes = torch.tensor(boxes)

        if self.transform:
            image, boxes = self.transform(image, boxes)

        label_matrix = torch.zeros((self.S, self.S, self.C + 5 * self.B)) # 1 bb per cell
        for box in boxes:
            cls_label, x, y, w, h = box.tolsit()
            cls_label = int(cls_label)
            i, j = int(self.S * y), int(self.S * x) 
            x_cell, y_cell = self.S*x -j, self.S * y -i # tricky, do by hand
            width_cell, height_cell = (
                w * self.S,
                h * self.S,
            )

            if label_matrix[i,j,20] == 0: # no obj
                label_matrix[i,j,20] = 1
                box_coordinates = torch.tensor([
                    x_cell, y_cell, width_cell, height_cell
                ])
                label_matrix[i,j,21:25] = box_coordinates
                label_matrix[i,j,cls_label] = 1

        return image, label_matrix
