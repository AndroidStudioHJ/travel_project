# ------------------------------------------------------------------------
# Copyright (c) 2022 megvii-model. All Rights Reserved.
# ------------------------------------------------------------------------
# Modified from BasicSR (https://github.com/xinntao/BasicSR)
# Copyright 2018-2020 BasicSR Authors
# ------------------------------------------------------------------------
import os
import random
import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
from basicsr.utils.registry import DATASET_REGISTRY

@DATASET_REGISTRY.register()
class ImageDataset(Dataset):
    """Image dataset for image restoration.

    Args:
        opt (dict): Config for train datasets. It contains the following keys:
            dataroot_gt (str): Data root path for gt.
            dataroot_lq (str): Data root path for lq.
            meta_info_file (str): Path for meta information file.
            io_backend (dict): IO backend type and other kwarg.
            gt_size (int): Cropped patched size for gt patches.
            use_flip (bool): Use horizontal flips.
            use_rot (bool): Use rotation (use vertical flip and transposing h
                and w for implementation).
            scale (bool): Scale, which will be added automatically.
            phase (str): 'train' or 'val'.
    """

    def __init__(self, opt):
        super(ImageDataset, self).__init__()
        self.opt = opt
        # file client (io backend)
        self.file_client = None
        self.io_backend_opt = opt['io_backend']
        self.mean = opt['mean'] if 'mean' in opt else None
        self.std = opt['std'] if 'std' in opt else None

        self.gt_folder = opt['dataroot_gt']
        self.lq_folder = opt['dataroot_lq']
        self.gt_size = opt['gt_size']
        self.use_flip = opt['use_flip']
        self.use_rot = opt['use_rot']

        self.paths = []
        self.gt_paths = []
        self.lq_paths = []

        # get image paths
        self.gt_paths = sorted([os.path.join(self.gt_folder, f) for f in os.listdir(self.gt_folder)])
        self.lq_paths = sorted([os.path.join(self.lq_folder, f) for f in os.listdir(self.lq_folder)])

        # transform
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.mean, std=self.std) if self.mean is not None else transforms.Lambda(lambda x: x)
        ])

    def __getitem__(self, index):
        # Load gt and lq images
        gt_path = self.gt_paths[index]
        lq_path = self.lq_paths[index]

        # Read images
        gt_img = Image.open(gt_path).convert('RGB')
        lq_img = Image.open(lq_path).convert('RGB')

        # Random crop
        if self.gt_size is not None:
            gt_img = self._random_crop(gt_img, self.gt_size)
            lq_img = self._random_crop(lq_img, self.gt_size)

        # Random flip
        if self.use_flip:
            gt_img, lq_img = self._random_flip(gt_img, lq_img)

        # Random rotation
        if self.use_rot:
            gt_img, lq_img = self._random_rot(gt_img, lq_img)

        # Transform
        gt_img = self.transform(gt_img)
        lq_img = self.transform(lq_img)

        return {'lq': lq_img, 'gt': gt_img, 'lq_path': lq_path, 'gt_path': gt_path}

    def __len__(self):
        return len(self.gt_paths)

    def _random_crop(self, img, size):
        """Random crop image.

        Args:
            img (PIL.Image): Image to be cropped.
            size (int): Cropped size.

        Returns:
            PIL.Image: Cropped image.
        """
        w, h = img.size
        if w < size or h < size:
            raise ValueError(f'Image size ({w}, {h}) is smaller than crop size {size}')
        x = random.randint(0, w - size)
        y = random.randint(0, h - size)
        return img.crop((x, y, x + size, y + size))

    def _random_flip(self, gt_img, lq_img):
        """Random flip images.

        Args:
            gt_img (PIL.Image): Ground truth image.
            lq_img (PIL.Image): Low quality image.

        Returns:
            tuple: Flipped images.
        """
        if random.random() < 0.5:
            gt_img = gt_img.transpose(Image.FLIP_LEFT_RIGHT)
            lq_img = lq_img.transpose(Image.FLIP_LEFT_RIGHT)
        return gt_img, lq_img

    def _random_rot(self, gt_img, lq_img):
        """Random rotate images.

        Args:
            gt_img (PIL.Image): Ground truth image.
            lq_img (PIL.Image): Low quality image.

        Returns:
            tuple: Rotated images.
        """
        if random.random() < 0.5:
            gt_img = gt_img.transpose(Image.ROTATE_90)
            lq_img = lq_img.transpose(Image.ROTATE_90)
        return gt_img, lq_img 