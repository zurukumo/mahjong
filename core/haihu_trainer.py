import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from torch.optim.adam import Adam
from torch.utils.data import DataLoader, TensorDataset

from core.mode import Mode


class MyModel(nn.Module):
    def __init__(self, n_channel: int, n_output: int) -> None:
        H = 1
        W = 34
        super(MyModel, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=n_channel, out_channels=32, kernel_size=(5, 2), padding='same')
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5, 2), padding='same')
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(5, 2), padding='same')
        self.dropout = nn.Dropout(0.2)
        self.fc1 = nn.Linear(128 * H * W, 128)
        self.fc2 = nn.Linear(128, n_output)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x))
        x = self.dropout(x)
        x = F.relu(self.conv2(x))
        x = self.dropout(x)
        x = F.relu(self.conv3(x))
        x = self.dropout(x)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.softmax(self.fc2(x), dim=1)
        return x


class HaihuTrainer:
    def __init__(self, mode: Mode, batch_size: int, n_epoch: int):
        match mode:
            case Mode.DAHAI:
                self.n_channel = 140
                self.n_output = 34
                self.filename = 'dahai'
            case Mode.RIICHI:
                self.n_channel = 140
                self.n_output = 2
                self.filename = 'riichi'
            case Mode.ANKAN:
                self.n_channel = 140
                self.n_output = 34
                self.filename = 'ankan'
            case Mode.RON_DAMINKAN_PON_CHII:
                self.n_channel = 140
                self.n_output = 7
                self.filename = 'ron_daiminkan_pon_chii'
            case _:
                raise ValueError('Invalid mode')

        self.model = MyModel(self.n_channel, self.n_output)
        self.batch_size = batch_size
        self.n_epoch = n_epoch

        x, t = self.prepare_data()
        x_train, x_test, t_train, t_test = train_test_split(x, t, test_size=0.2, shuffle=True)

        train_data = TensorDataset(torch.tensor(x_train, dtype=torch.float32), torch.tensor(t_train, dtype=torch.long))
        test_data = TensorDataset(torch.tensor(x_test, dtype=torch.float32), torch.tensor(t_test, dtype=torch.long))

        self.train_loader = DataLoader(train_data, batch_size=self.batch_size, shuffle=True)
        self.test_loader = DataLoader(test_data, batch_size=self.batch_size, shuffle=False)

        optimizer = Adam(self.model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        for epoch in range(self.n_epoch):
            train_loss = self.train_model(optimizer, criterion)
            accuracy, test_loss = self.evaluate_model(criterion)
            print(', '.join([
                f'Epoch {epoch+1}/{self.n_epoch}',
                f'Train Loss: {train_loss:.4f}',
                f'Test Loss: {test_loss:.4f}',
                f'Accuracy: {accuracy*100:.2f}%'
            ]))

        # モデルを保存
        current_dir = os.path.dirname(__file__)
        torch.save(self.model.state_dict(), os.path.join(current_dir, f'../models/{self.filename}.pth'))
        print(f'Model saved as {self.filename}_model.pth')

    # データ準備関数
    def prepare_data(self):
        current_dir = os.path.dirname(__file__)
        filepath = os.path.join(current_dir, f'../datasets/{self.filename}.csv')
        data = np.genfromtxt(filepath, delimiter=',', dtype=np.int8)
        t, x = np.hsplit(data, [1])
        x = x.reshape(-1, self.n_channel, 1, 34)
        return x, t

    # 学習用関数
    def train_model(self, optimizer, criterion):
        self.model.train()
        running_loss = 0.0
        for inputs, labels in self.train_loader:
            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels.squeeze())
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        return running_loss / len(self.train_loader)

    # 評価用関数
    def evaluate_model(self, criterion):
        self.model.eval()
        correct = 0
        total = 0
        running_loss = 0.0
        with torch.no_grad():
            for inputs, labels in self.test_loader:
                outputs = self.model(inputs)
                loss = criterion(outputs, labels.squeeze())
                running_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels.squeeze()).sum().item()
        return correct / total, running_loss / len(self.test_loader)
