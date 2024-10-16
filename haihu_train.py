import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

# 定数
N_OUTPUT = {'ron_minkan_pon_chii': 7}
N_CHANNEL = {'ron_minkan_pon_chii': 128}
BATCH_SIZE = 32
EPOCHS = 10
H = 1
W = 34


class ConvNet(nn.Module):
    def __init__(self, n_channel, n_output):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=n_channel, out_channels=32, kernel_size=(5, 2), padding='same')
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5, 2), padding='same')
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=(5, 2), padding='same')
        self.dropout = nn.Dropout(0.2)
        self.fc1 = nn.Linear(128 * H * W, 128)
        self.fc2 = nn.Linear(128, n_output)

    def forward(self, x):
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


# データ準備関数
def prepare_data(model: str):
    current_dir = os.path.dirname(__file__)
    data = np.genfromtxt(os.path.join(current_dir, f'datasets/{model}.csv'), delimiter=',', dtype=np.int8)
    t, x = np.hsplit(data, [1])
    x = x.reshape(-1, N_CHANNEL[model], 1, 34)
    return x, t


# 学習用関数
def train_model(model, train_loader, optimizer, criterion):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = torch.tensor(inputs, dtype=torch.float32), torch.tensor(labels, dtype=torch.long)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels.squeeze())
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    return running_loss / len(train_loader)


# 評価用関数
def evaluate_model(model, test_loader, criterion):
    model.eval()
    correct = 0
    total = 0
    running_loss = 0.0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = torch.tensor(inputs, dtype=torch.float32), torch.tensor(labels, dtype=torch.long)
            outputs = model(inputs)
            loss = criterion(outputs, labels.squeeze())
            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels.squeeze()).sum().item()
    return correct / total, running_loss / len(test_loader)


# 学習プロセス
if __name__ == '__main__':
    model_name = "ron_minkan_pon_chii"
    n_channel = N_CHANNEL[model_name]
    n_output = N_OUTPUT[model_name]

    x, t = prepare_data(model_name)
    x_train, x_test, t_train, t_test = train_test_split(x, t, test_size=0.2, shuffle=True)

    train_data = TensorDataset(torch.tensor(x_train, dtype=torch.float32), torch.tensor(t_train, dtype=torch.long))
    test_data = TensorDataset(torch.tensor(x_test, dtype=torch.float32), torch.tensor(t_test, dtype=torch.long))

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=False)

    model = ConvNet(n_channel, n_output)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(EPOCHS):
        train_loss = train_model(model, train_loader, optimizer, criterion)
        accuracy, test_loss = evaluate_model(model, test_loader, criterion)
        print(', '.join([
            f'Epoch {epoch+1}/{EPOCHS}',
            f'Train Loss: {train_loss:.4f}',
            f'Test Loss: {test_loss:.4f}',
            f'Accuracy: {accuracy*100:.2f}%'
        ]))

    # モデルを保存
    current_dir = os.path.dirname(__file__)
    torch.save(model.state_dict(), os.path.join(current_dir, f'models/{model_name}_model.pth'))
    print(f'Model saved as {model_name}_model.pth')
