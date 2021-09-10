from mlflow.store.artifact.s3_artifact_repo import S3ArtifactRepository


class InfinStorArtifactRepository(S3ArtifactRepository):
    """LocalArtifactRepository provided through plugin system"""
    is_plugin = True
