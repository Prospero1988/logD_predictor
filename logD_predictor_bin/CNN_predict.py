import torch
import torch.nn as nn
import numpy as np

# Parser for summary.txt file (from previous steps)
def parse_params_from_summary(summary_file_path):
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
            if line == '10CV Metrics:':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Converting values to the appropriate type
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

# Net class definition (as before)
class Net(nn.Module):
    def __init__(self, params, input_dim):
        super(Net, self).__init__()

        # Activation function selection
        activation_name = params.get('activation', 'relu')
        if activation_name == 'relu':
            activation = nn.ReLU()
        elif activation_name == 'tanh':
            activation = nn.Tanh()
        elif activation_name == 'sigmoid':
            activation = nn.Sigmoid()
        elif activation_name == 'leaky_relu':
            activation = nn.LeakyReLU()
        elif activation_name == 'selu':
            activation = nn.SELU()
        else:
            activation = nn.ReLU()

        self.regularization = params.get('regularization', 'none')
        self.reg_rate = params.get('reg_rate', 1e-5) if self.regularization != 'none' else 0.0

        dropout_rate = params.get('dropout_rate', 0.0)
        use_batch_norm = params.get('use_batch_norm', False)

        # Convolutional layers
        num_conv_layers = params.get('num_conv_layers', 1)
        conv_layers = []
        in_channels = 1
        input_length = input_dim

        for i in range(num_conv_layers):
            out_channels = params.get(f'num_filters_l{i}', 16)
            kernel_size = params.get(f'kernel_size_l{i}', 3)
            stride = params.get(f'stride_l{i}', 1)
            padding = params.get(f'padding_l{i}', 0)

            conv_layers.append(nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=padding))
            if use_batch_norm:
                conv_layers.append(nn.BatchNorm1d(out_channels))
            conv_layers.append(activation)
            if dropout_rate > 0.0:
                conv_layers.append(nn.Dropout(dropout_rate))
            in_channels = out_channels

            # Calculate the new input length (dynamically handling different data lengths)
            input_length = int((input_length + 2 * padding - (kernel_size - 1) - 1) / stride + 1)
            if input_length <= 0:
                raise ValueError('Negative or zero input length. Adjust kernel_size, stride, or padding.')

        self.conv = nn.Sequential(*conv_layers)

        # Layers fully connected
        num_fc_layers = params.get('num_fc_layers', 2)
        fc_layers = []
        in_features = in_channels * input_length

        for i in range(num_fc_layers):
            out_features = params.get(f'fc_units_l{i}', 32)
            fc_layers.append(nn.Linear(in_features, out_features))
            if use_batch_norm:
                fc_layers.append(nn.BatchNorm1d(out_features))
            fc_layers.append(activation)
            if dropout_rate > 0.0:
                fc_layers.append(nn.Dropout(dropout_rate))
            in_features = out_features

        fc_layers.append(nn.Linear(in_features, 1)) 
        self.fc = nn.Sequential(*fc_layers)

        init_method = params.get('weight_init', 'xavier')
        self.apply(lambda m: self.init_weights(m, init_method))

    def init_weights(self, m, init_method):
        if isinstance(m, nn.Conv1d) or isinstance(m, nn.Linear):
            if init_method == 'xavier':
                nn.init.xavier_uniform_(m.weight)
            elif init_method == 'kaiming':
                nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
            elif init_method == 'normal':
                nn.init.normal_(m.weight, mean=0.0, std=0.05)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)  
        x = self.fc(x)
        return x


def model_predictor(model_path, structure_features, quiet):

    # Defining the function that controls printing
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    summary_path = model_path.replace("_model.pth", "_summary.txt")
    params = parse_params_from_summary(summary_path)

    input_dim = structure_features.shape[1]
    model = Net(params, input_dim)
    # Loading model weights without the whole object
    model_weights = torch.load(model_path, map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(model_weights)  # Pass only the weights to the model
    model.eval()

    # Convert `structure_features` to numeric data types and tensor PyTorch
    if hasattr(structure_features, 'values'):
        structure_features = structure_features.values  
    structure_features = structure_features.astype(np.float32)  

    verbose_print(f"Initial shape of structure_features: {structure_features.shape}")

    with torch.no_grad():
        # Remove all redundant dimensions to get a flat tensor [250].
        input_features = torch.tensor(structure_features.squeeze(), dtype=torch.float32)

        # Add dimensions for batch and channels so that the resulting tensor is [1, 1, 250].
        input_features = input_features.unsqueeze(0).unsqueeze(0)
        
        # Confirmation of final form
        verbose_print(f"Final shape of input_features for model: {input_features.shape}")

        # Transfer to the model
        prediction = model(input_features).item()


    return prediction



