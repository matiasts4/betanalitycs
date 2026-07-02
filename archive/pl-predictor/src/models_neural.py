import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.base import BaseEstimator, ClassifierMixin

class PyTorchMLPClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, input_dim=27, hidden_dim=64, dropout_rate=0.3, lr=0.01, epochs=80, batch_size=64, random_state=42):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.dropout_rate = dropout_rate
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state
        self.model = None
        self.classes_ = None
        
    def fit(self, X, y):
        # Determinar semilla para replicabilidad
        torch.manual_seed(self.random_state)
        np.random.seed(self.random_state)
        
        X_arr = np.array(X, dtype=np.float32)
        y_arr = np.array(y)
        
        self.classes_ = np.unique(y_arr)
        num_classes = len(self.classes_)
        
        # Red de dos capas ocultas con Dropout
        if num_classes > 2:
            # Multiclase (CrossEntropy)
            y_tensor = torch.tensor(y_arr, dtype=torch.long)
            self.model = nn.Sequential(
                nn.Linear(self.input_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Dropout(self.dropout_rate),
                nn.Linear(self.hidden_dim, self.hidden_dim // 2),
                nn.ReLU(),
                nn.Dropout(self.dropout_rate),
                nn.Linear(self.hidden_dim // 2, num_classes)
            )
            criterion = nn.CrossEntropyLoss()
        else:
            # Binario (BCE)
            y_tensor = torch.tensor(y_arr, dtype=torch.float32).unsqueeze(1)
            self.model = nn.Sequential(
                nn.Linear(self.input_dim, self.hidden_dim),
                nn.ReLU(),
                nn.Dropout(self.dropout_rate),
                nn.Linear(self.hidden_dim, self.hidden_dim // 2),
                nn.ReLU(),
                nn.Dropout(self.dropout_rate),
                nn.Linear(self.hidden_dim // 2, 1)
            )
            criterion = nn.BCEWithLogitsLoss()
            
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-4)
        
        # Preparar data loader
        X_tensor = torch.tensor(X_arr, dtype=torch.float32)
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        self.model.train()
        for epoch in range(self.epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
        return self
        
    def predict_proba(self, X):
        X_arr = np.array(X, dtype=np.float32)
        if self.model is None:
            raise ValueError("El modelo debe entrenarse primero usando .fit()")
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(X_arr, dtype=torch.float32)
            outputs = self.model(X_tensor)
            
            if len(self.classes_) > 2:
                probs = torch.softmax(outputs, dim=1).numpy()
            else:
                probs_pos = torch.sigmoid(outputs).numpy()
                probs = np.hstack([1 - probs_pos, probs_pos])
                
        return probs
        
    def predict(self, X):
        probs = self.predict_proba(X)
        return self.classes_[np.argmax(probs, axis=1)]
