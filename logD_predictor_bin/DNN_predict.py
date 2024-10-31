import torch
import torch.nn as nn
import numpy as np

def parse_params_from_summary(summary_file_path):
    """
    Parses the summary.txt file to extract the best hyperparameters.
    """
    params = {}
    with open(summary_file_path, 'r') as f:
        lines = f.readlines()

    in_params_section = False
    for line in lines:
        line = line.strip()
        if line == 'Best parameters:':
            in_params_section = True
            continue
        if line == '' or line.endswith(':'):
            continue
        if in_params_section:
            if line.startswith('10CV Metrics:'):
                break
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Convert value to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                else:
                    try:
                        if '.' in value or 'e' in value.lower():
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                params[key] = value
    return params

class Net(nn.Module):
    def __init__(self, params, input_dim):
        super(Net, self).__init__()

        # Activation function selection
        activation_name = params.get('activation', 'relu')
        self.activation = self.get_activation_function(activation_name)

        # Regularization
        self.regularization = params.get('regularization', 'none')
        self.reg_rate = params.get('reg_rate', 0.0)

        # Layer configuration
        num_layers = params.get('num_layers', 1)
        units = params.get('units', 32)
        dropout_rate = params.get('dropout_rate', 0.0)
        use_batch_norm = params.get('use_batch_norm', False)

        layers_list = []
        in_features = input_dim

        for _ in range(num_layers):
            layers_list.append(nn.Linear(in_features, units))
            if use_batch_norm:
                layers_list.append(nn.BatchNorm1d(units))
            layers_list.append(self.activation)
            if dropout_rate > 0.0:
                layers_list.append(nn.Dropout(dropout_rate))
            in_features = units

        # Output layer
        layers_list.append(nn.Linear(in_features, 1))
        self.model = nn.Sequential(*layers_list)

        # Weight initialization
        self.init_method = params.get('weight_init', 'xavier')
        self.apply(self.init_weights)

    def get_activation_function(self, name):
        if name == 'relu':
            return nn.ReLU()
        elif name == 'tanh':
            return nn.Tanh()
        elif name == 'sigmoid':
            return nn.Sigmoid()
        elif name == 'leaky_relu':
            return nn.LeakyReLU(negative_slope=0.01)
        elif name == 'selu':
            return nn.SELU()
        else:
            raise ValueError(f"Unsupported activation function: {name}")

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            if self.init_method == 'xavier':
                nn.init.xavier_uniform_(m.weight)
            elif self.init_method == 'kaiming':
                nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
            elif self.init_method == 'normal':
                nn.init.normal_(m.weight, mean=0.0, std=0.05)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x):
        return self.model(x)

def model_predictor(model_path, structure_features, quiet=False):
    """
    Loads the model, reconstructs it based on saved hyperparameters,
    and makes a prediction on the input features.
    """
    # Define a verbose print function
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # Derive the summary.txt path from the model path
    summary_path = model_path.replace("_final_model.pth", "_summary.txt")
    params = parse_params_from_summary(summary_path)

    # Create the model
    input_dim = structure_features.shape[1]
    model = Net(params, input_dim)

    # Load model weights safely
    model_weights = torch.load(model_path, map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(model_weights)
    model.eval()

    # Ensure structure_features is a NumPy array
    if hasattr(structure_features, 'values'):
        structure_features = structure_features.values  # If it's a DataFrame, get the values

    # Convert to PyTorch tensor
    with torch.no_grad():
        input_features = torch.tensor(structure_features.astype(np.float32), dtype=torch.float32)

        # If input is 1D, add batch dimension
        if input_features.ndim == 1:
            input_features = input_features.unsqueeze(0)

        verbose_print(f"Input features shape: {input_features.shape}")

        # Make prediction
        prediction = model(input_features).item()

    return prediction
