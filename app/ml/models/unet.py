import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    """(Convolution => BatchNorm => ReLU) * 2"""
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class UNet(nn.Module):
    """
    Lightweight 4-Depth U-Net for Microscopy Binary Image Segmentation.
    Designed for small datasets and efficient CPU/GPU training/inference.
    """
    def __init__(self, in_channels: int = 3, out_channels: int = 1, base_features: int = 32):
        super().__init__()
        self.inc = DoubleConv(in_channels, base_features)
        
        # Downsampling Encoder
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_features, base_features * 2))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_features * 2, base_features * 4))
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_features * 4, base_features * 8))
        
        # Bottleneck Bridge
        self.bot = nn.Sequential(nn.MaxPool2d(2), DoubleConv(base_features * 8, base_features * 16))
        
        # Upsampling Decoder
        self.up1 = nn.ConvTranspose2d(base_features * 16, base_features * 8, kernel_size=2, stride=2)
        self.conv_up1 = DoubleConv(base_features * 16, base_features * 8)
        
        self.up2 = nn.ConvTranspose2d(base_features * 8, base_features * 4, kernel_size=2, stride=2)
        self.conv_up2 = DoubleConv(base_features * 8, base_features * 4)
        
        self.up3 = nn.ConvTranspose2d(base_features * 4, base_features * 2, kernel_size=2, stride=2)
        self.conv_up3 = DoubleConv(base_features * 4, base_features * 2)
        
        self.up4 = nn.ConvTranspose2d(base_features * 2, base_features, kernel_size=2, stride=2)
        self.conv_up4 = DoubleConv(base_features * 2, base_features)
        
        # Output Convolution Head (Raw logits)
        self.outc = nn.Conv2d(base_features, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        
        x_bot = self.bot(x4)
        
        x_up1 = self.up1(x_bot)
        x_up1 = torch.cat([x4, x_up1], dim=1)
        x_up1 = self.conv_up1(x_up1)
        
        x_up2 = self.up2(x_up1)
        x_up2 = torch.cat([x3, x_up2], dim=1)
        x_up2 = self.conv_up2(x_up2)
        
        x_up3 = self.up3(x_up2)
        x_up3 = torch.cat([x2, x_up3], dim=1)
        x_up3 = self.conv_up3(x_up3)
        
        x_up4 = self.up4(x_up3)
        x_up4 = torch.cat([x1, x_up4], dim=1)
        x_up4 = self.conv_up4(x_up4)
        
        logits = self.outc(x_up4)
        return logits
