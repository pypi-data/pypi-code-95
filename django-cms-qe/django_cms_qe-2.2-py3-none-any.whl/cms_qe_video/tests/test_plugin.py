import re
from pytest_data import use_data

from cms_qe_test import render_plugin

from ..cms_plugins import HostingVideoPlayerPlugin, SourceFileVideoPlayerPlugin


@use_data(cms_qe_video_source_file_video_player_model_data={'source_file': None})
def test_render_source_file_video_plugin_without_source_file(cms_qe_video_source_file_video_player_model):
    html = render_plugin(SourceFileVideoPlayerPlugin, cms_qe_video_source_file_video_player_model)
    assert re.search(r'<p>Video file is missing</p>', html)


def test_render_source_file_video_plugin(cms_qe_video_source_file_video_player_model):
    html = render_plugin(SourceFileVideoPlayerPlugin, cms_qe_video_source_file_video_player_model)
    assert not re.search(r'<iframe(\s|.)*</iframe>', html)


def test_render_hosting_video_plugin(cms_qe_video_hosting_video_player_model):
    html = render_plugin(HostingVideoPlayerPlugin, cms_qe_video_hosting_video_player_model)
    assert not re.search(r'<video(\s|.)*</video>', html)
    assert re.search(r'<iframe(\s|.)*</iframe>', html)
