
from pathlib import Path

import joblib
import numpy as np
import torch
from torch import nn

from qiskit import QuantumCircuit
from qiskit.circuit.library import real_amplitudes, zz_feature_map
from qiskit_machine_learning.neural_networks import EstimatorQNN
from qiskit_machine_learning.connectors import TorchConnector


BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = BASE_DIR / "artifacts"

FEATURES = [
    "rainfall_mm",
    "temperature_c",
    "soil_moisture_pct",
    "ndvi",
]


def load_quantum_model():
    num_qubits = 4

    feature_map = zz_feature_map(
        feature_dimension=num_qubits,
        reps=1,
    )

    ansatz = real_amplitudes(
        num_qubits=num_qubits,
        reps=1,
    )

    circuit = QuantumCircuit(num_qubits)
    circuit.compose(feature_map, inplace=True)
    circuit.compose(ansatz, inplace=True)

    qnn = EstimatorQNN(
        circuit=circuit,
        input_params=list(feature_map.parameters),
        weight_params=list(ansatz.parameters),
        input_gradients=True,
    )

    initial_weights = 0.1 * torch.randn(len(ansatz.parameters))
    quantum_layer = TorchConnector(qnn, initial_weights)

    model = nn.Sequential(
        quantum_layer,
        nn.Linear(1, 1),
    )

    weights_path = ARTIFACT_DIR / "quantum_model_weights.pt"

    state_dict = torch.load(
        weights_path,
        map_location="cpu",
        weights_only=True,
    )
    model.load_state_dict(state_dict)
    model.eval()

    x_scaler = joblib.load(ARTIFACT_DIR / "x_scaler.joblib")
    y_scaler = joblib.load(ARTIFACT_DIR / "y_scaler.joblib")

    return model, x_scaler, y_scaler


model, x_scaler, y_scaler = load_quantum_model()


def predict_yield(
    rainfall_mm: float,
    temperature_c: float,
    soil_moisture_pct: float,
    ndvi: float,
) -> float:
    raw_features = np.array(
        [[rainfall_mm, temperature_c, soil_moisture_pct, ndvi]],
        dtype=np.float64,
    )

    scaled_features = x_scaler.transform(raw_features)
    encoded_features = scaled_features * (2 * np.pi) - np.pi

    input_tensor = torch.tensor(encoded_features, dtype=torch.float32)

    with torch.no_grad():
        scaled_prediction = model(input_tensor).numpy()

    yield_prediction = y_scaler.inverse_transform(scaled_prediction)

    return max(0.0, float(yield_prediction[0, 0]))