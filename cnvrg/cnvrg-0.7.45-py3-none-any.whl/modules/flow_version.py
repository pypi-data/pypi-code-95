from cnvrg.modules.project import Project
from cnvrg.helpers.url_builder_helper import url_join

import cnvrg.helpers.param_build_helper as param_build_helper
import cnvrg.helpers.apis_helper as apis_helper


class FlowVersion():
    def __init__(self, flow, slug, title, project=None):
        owner, project_slug, flow_slug = param_build_helper.parse_params(flow.slug, param_build_helper.FLOW)

        p = Project.factory(owner, project)

        if p is None:
            p = Project(url_join(owner, project_slug))

        self.slug = slug
        self.title = title
        self.owner = owner
        self.flow = flow
        self.project = p

    def info(self):
        resp = apis_helper.get_v2(
            url_join(
                self.project.get_base_url(api="v2"),
                'flows',
                self.flow.slug,
                "flow-versions",
                self.slug,
                'info'
            )
        )

        return resp.json()["data"]["attributes"].get("fv_status")
