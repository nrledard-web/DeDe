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
from estimators.consensus_trend_estimator import (
    ConsensusTrendEstimator,
)


class EstimatorEngine:
    """
    Executes the estimation layer.

    Estimators may use different detection methods.
    The cognitive variables they produce are stored
    in a common universal workspace.
    """

    def __init__(self) -> None:
        self.estimators = [
            GroundingEstimator(),
            IntegrationEstimator(),
            ClosureEstimator(),
            ReductionEstimator(),
            ConsensusTrendEstimator(),
        ]

    def run(
        self,
        workspace: CognitiveWorkspace,
    ) -> CognitiveWorkspace:

        for estimator in self.estimators:
            workspace = estimator.run(
                workspace
            )

        return workspace
