from typing import List

import joblib

from microcosm_sagemaker.artifact import BundleInputArtifact, BundleOutputArtifact
from microcosm_sagemaker.bundle import Bundle


class PicklingBundle(Bundle):
    """
    Automatically defines save and load to pickle and load a list of attrs
    specified in `pickle_attrs`

    """
    pickle_attrs: List[str]

    def save(self, output_artifact: BundleOutputArtifact) -> None:
        """
        Save the trained model

        """
        for pickle_attr in self.pickle_attrs:
            joblib.dump(
                getattr(self, pickle_attr),
                output_artifact.path / f"{pickle_attr}.pkl",
            )

    def load(self, input_artifact: BundleInputArtifact) -> None:
        """
        Load the trained model

        """
        for pickle_attr in self.pickle_attrs:
            setattr(
                self,
                pickle_attr,
                joblib.load(input_artifact.path / f"{pickle_attr}.pkl")
            )
