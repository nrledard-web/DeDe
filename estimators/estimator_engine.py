"""
DeDe - Estimator Engine

Runs all cognitive estimators and writes their variables
into the CognitiveWorkspace.
"""

from core.cognitive_workspace import CognitiveWorkspace

from estimators.grounding_estimator import GroundingEstimator
from estimators.integration_estimator import IntegrationEstimator
from estimators.closure_estimator import ClosureEstimator
from estimators.reduction_estimator import ReductionEstimator


class EstimatorEngine:
    """
    Executes the estimation layer.

    Estimators are language-dependent.
    The variables they produce are universal.
    """

    def __init__(self):
        self.estimators = [
            GroundingEstimator(),
            IntegrationEstimator(),
            ClosureEstimator(),
            ReductionEstimator(),
        ]

    def run(self, workspace: CognitiveWorkspace) -> CognitiveWorkspace:
        for estimator in self.estimators:
            workspace = estimator.run(workspace)

        return workspace
