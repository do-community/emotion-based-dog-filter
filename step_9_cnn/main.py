"""
Sample convolutional neural network for Face Emotion Recognition 2013 Dataset
"""

from utils import Fer2013Dataset
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import torch
import argparse


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 6, 3)
        self.conv3 = nn.Conv2d(6, 16, 3)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 48)
        self.fc3 = nn.Linear(48, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 16 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def evaluate(outputs: Variable, labels: Variable) -> float:
    """Evaluate neural network outputs against non-one-hotted labels."""
    Y = labels.data.numpy()
    Yhat = np.argmax(outputs.data.numpy(), axis=1)
    return float(np.sum(Yhat == Y) / Y.shape[0])


def save_state(epoch: int, net: Net, optimizer):
    """Save the state of training."""
    torch.save({
        'epoch': epoch + 1,
        'state_dict': net.state_dict(),
        'optimizer': optimizer.state_dict(),
    }, 'checkpoint.pth')


def train(
        net: Net,
        trainset: Fer2013Dataset,
        testset: Fer2013Dataset,
        pretrained_model: dict={}):
    """Main training loop and optimization setup."""
    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=32, shuffle=True)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    best_test_acc = 0

    def status_update(outputs: Variable, labels: Variable):
        """Print train, validation accuracies along with current loss."""
        nonlocal best_test_acc

        train_acc = evaluate(outputs, labels)
        test_acc = evaluate(net(testset.X), testset.Y)
        print('[%d, %5d] loss: %.2f train acc: %.2f val acc: %.2f' %
              (epoch + 1, i + 1, running_loss / i, train_acc, test_acc))
        if test_acc > best_test_acc:
            best_test_acc = test_acc
            save_state(epoch, net, optimizer)

    start_epoch = pretrained_model.get('epoch', 0)
    for epoch in range(start_epoch, start_epoch + 20):

        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs = Variable(data['image'].float())
            labels = Variable(data['label'].long())
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.data[0]
            if i % 100 == 99:
                status_update(outputs, labels)


def main():
    """Main script for Face Emotion Recognition 2013 dataset neural network"""
    args = argparse.ArgumentParser('Main training script for FER 2013')
    args.add_argument('action', choices=('train', 'eval'),
                      help='Script utility to invoke')
    args.add_argument('--model', help='Path to model to restore from.')
    args = args.parse_args()

    trainset = Fer2013Dataset('X_train.npy', 'Y_train.npy')
    testset = Fer2013Dataset('X_test.npy', 'Y_test.npy')
    net = Net().float()

    pretrained_model = {}
    if args.model:
        pretrained_model = torch.load(args.model)
        net.load_state_dict(pretrained_model['state_dict'])

    if args.action == 'train':
        train(net, trainset, testset, pretrained_model)

    print('=' * 10, 'Finished Training', '=' * 10)
    train_acc = evaluate(net(trainset.X), trainset.Y)
    print('Training accuracy: %.3f' % train_acc)
    test_acc = evaluate(net(testset.X), testset.Y)
    print('Validation accuracy: %.3f' % test_acc)


if __name__ == '__main__':
    main()