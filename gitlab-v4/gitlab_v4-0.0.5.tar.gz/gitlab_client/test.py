from gitlab_client.gitlab_client import Gitlab


client = Gitlab(
    access_token="AvBRFHiek-C4zNs63zF6",
    project_id="28351523",
    gitlab_base_url="https://gitlab.com/api/v4"
)

pipeline = client.get_pipeline(357206368)

print(pipeline)
