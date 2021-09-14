import requests
import urllib3


__ALL__ = ["deluge_rpc_api"]


urllib3.disable_warnings()


class deluge_rpc_api:
    def __init__(self, secured: bool = False, host: str = "127.0.0.1", port: int = 8112):
        self.rpc_url = "http{}://{}:{}/json".format("s" if secured else "", host, port)
        self.call_id = 0
        self.s = requests.Session()
        self.core = core_rpc_api()
        self.core.post = self.post
        self.daemon = daemon_rpc_api()
        self.daemon.post = self.post
        self.autoadd = autoadd_rpc_api()
        self.autoadd.post = self.post
        self.blocklist = blocklist_rpc_api()
        self.blocklist.post = self.post
        self.execute = execute_rpc_api()
        self.execute.post = self.post
        self.extractor = extractor_rpc_api()
        self.extractor.post = self.post
        self.label = label_rpc_api()
        self.label.post = self.post
        self.notifications = notifications_rpc_api()
        self.notifications.post = self.post
        self.scheduler = scheduler_rpc_api()
        self.scheduler.post = self.post
        self.stats = stats_rpc_api()
        self.stats.post = self.post
        self.toggle = toggle_rpc_api()
        self.toggle.post = self.post
        self.webui = webui_rpc_api()
        self.webui.post = self.post
        self.auth = auth_rpc_api()
        self.auth.post = self.post
        self.web = web_rpc_api()
        self.web.post = self.post
        self.webutils = webutils_rpc_api()
        self.webutils.post = self.post

    def post(self, method, params):
        self.call_id += 1
        return self.s.post(
            self.rpc_url,
            json={
                "id": self.call_id,
                "method": method,
                "params": params or [],
            },
            verify=False
        ).json()
        
    
class core_rpc_api:
    def add_torrent_file_async(self, filename=None, filedump=None, options=None, save_state=True):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L407
        data = {"method": "core.add_torrent_file_async", "params": [filename, filedump, options, save_state]}
        return self.post(**data)

    def prefetch_magnet_metadata(self, magnet=None, timeout=30):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L439
        data = {"method": "core.prefetch_magnet_metadata", "params": [magnet, timeout]}
        return self.post(**data)

    def add_torrent_file(self, filename=None, filedump=None, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L465
        data = {"method": "core.add_torrent_file", "params": [filename, filedump, options]}
        return self.post(**data)

    def add_torrent_files(self, torrent_files=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L490
        data = {"method": "core.add_torrent_files", "params": [torrent_files]}
        return self.post(**data)

    def add_torrent_url(self, url=None, options=None, headers=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L518
        data = {"method": "core.add_torrent_url", "params": [url, options, headers]}
        return self.post(**data)

    def add_torrent_magnet(self, uri=None, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L556
        data = {"method": "core.add_torrent_magnet", "params": [uri, options]}
        return self.post(**data)

    def remove_torrent(self, torrent_id=None, remove_data=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L574
        data = {"method": "core.remove_torrent", "params": [torrent_id, remove_data]}
        return self.post(**data)

    def remove_torrents(self, torrent_ids=None, remove_data=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L592
        data = {"method": "core.remove_torrents", "params": [torrent_ids, remove_data]}
        return self.post(**data)

    def get_session_status(self, keys=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L628
        data = {"method": "core.get_session_status", "params": [keys]}
        return self.post(**data)

    def force_reannounce(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L659
        data = {"method": "core.force_reannounce", "params": [torrent_ids]}
        return self.post(**data)

    def pause_torrent(self, torrent_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L665
        data = {"method": "core.pause_torrent", "params": [torrent_id]}
        return self.post(**data)

    def pause_torrents(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L674
        data = {"method": "core.pause_torrents", "params": [torrent_ids]}
        return self.post(**data)

    def connect_peer(self, torrent_id=None, ip=None, port=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L682
        data = {"method": "core.connect_peer", "params": [torrent_id, ip, port]}
        return self.post(**data)

    def move_storage(self, torrent_ids=None, dest=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L688
        data = {"method": "core.move_storage", "params": [torrent_ids, dest]}
        return self.post(**data)

    def pause_session(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L695
        data = {"method": "core.pause_session", "params": []}
        return self.post(**data)

    def resume_session(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L702
        data = {"method": "core.resume_session", "params": []}
        return self.post(**data)

    def is_session_paused(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L711
        data = {"method": "core.is_session_paused", "params": []}
        return self.post(**data)

    def resume_torrent(self, torrent_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L716
        data = {"method": "core.resume_torrent", "params": [torrent_id]}
        return self.post(**data)

    def resume_torrents(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L725
        data = {"method": "core.resume_torrents", "params": [torrent_ids]}
        return self.post(**data)

    def get_torrent_status(self, torrent_id=None, keys=None, diff=False):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L758
        data = {"method": "core.get_torrent_status", "params": [torrent_id, keys, diff]}
        return self.post(**data)

    def get_torrents_status(self, filter_dict=None, keys=None, diff=False):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L772
        data = {"method": "core.get_torrents_status", "params": [filter_dict, keys, diff]}
        return self.post(**data)

    def get_filter_tree(self, show_zero_hits=True, hide_cat=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L793
        data = {"method": "core.get_filter_tree", "params": [show_zero_hits, hide_cat]}
        return self.post(**data)

    def get_session_state(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L801
        data = {"method": "core.get_session_state", "params": []}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L807
        data = {"method": "core.get_config", "params": []}
        return self.post(**data)

    def get_config_value(self, key=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L812
        data = {"method": "core.get_config_value", "params": [key]}
        return self.post(**data)

    def get_config_values(self, keys=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L817
        data = {"method": "core.get_config_values", "params": [keys]}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L822
        data = {"method": "core.set_config", "params": [config]}
        return self.post(**data)

    def get_listen_port(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L831
        data = {"method": "core.get_listen_port", "params": []}
        return self.post(**data)

    def get_proxy(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L836
        data = {"method": "core.get_proxy", "params": []}
        return self.post(**data)

    def get_available_plugins(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L868
        data = {"method": "core.get_available_plugins", "params": []}
        return self.post(**data)

    def get_enabled_plugins(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L873
        data = {"method": "core.get_enabled_plugins", "params": []}
        return self.post(**data)

    def enable_plugin(self, plugin=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L878
        data = {"method": "core.enable_plugin", "params": [plugin]}
        return self.post(**data)

    def disable_plugin(self, plugin=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L882
        data = {"method": "core.disable_plugin", "params": [plugin]}
        return self.post(**data)

    def force_recheck(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L886
        data = {"method": "core.force_recheck", "params": [torrent_ids]}
        return self.post(**data)

    def set_torrent_options(self, torrent_ids=None, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L892
        data = {"method": "core.set_torrent_options", "params": [torrent_ids, options]}
        return self.post(**data)

    def set_torrent_trackers(self, torrent_id=None, trackers=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L909
        data = {"method": "core.set_torrent_trackers", "params": [torrent_id, trackers]}
        return self.post(**data)

    def get_path_size(self, path=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L986
        data = {"method": "core.get_path_size", "params": [path]}
        return self.post(**data)

    def create_torrent(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L992
        data = {"method": "core.create_torrent", "params": []}
        return self.post(**data)

    def upload_plugin(self, filename=None, filedump=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1058
        data = {"method": "core.upload_plugin", "params": [filename, filedump]}
        return self.post(**data)

    def rescan_plugins(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1076
        data = {"method": "core.rescan_plugins", "params": []}
        return self.post(**data)

    def rename_files(self, torrent_id=None, filenames=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1083
        data = {"method": "core.rename_files", "params": [torrent_id, filenames]}
        return self.post(**data)

    def rename_folder(self, torrent_id=None, folder=None, new_folder=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1106
        data = {"method": "core.rename_folder", "params": [torrent_id, folder, new_folder]}
        return self.post(**data)

    def queue_top(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1128
        data = {"method": "core.queue_top", "params": [torrent_ids]}
        return self.post(**data)

    def queue_up(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1142
        data = {"method": "core.queue_up", "params": [torrent_ids]}
        return self.post(**data)

    def queue_down(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1167
        data = {"method": "core.queue_down", "params": [torrent_ids]}
        return self.post(**data)

    def queue_bottom(self, torrent_ids=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1192
        data = {"method": "core.queue_bottom", "params": [torrent_ids]}
        return self.post(**data)

    def glob(self, path=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1206
        data = {"method": "core.glob", "params": [path]}
        return self.post(**data)

    def test_listen_port(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1210
        data = {"method": "core.test_listen_port", "params": []}
        return self.post(**data)

    def get_free_space(self, path=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1235
        data = {"method": "core.get_free_space", "params": [path]}
        return self.post(**data)

    def get_external_ip(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1259
        data = {"method": "core.get_external_ip", "params": []}
        return self.post(**data)

    def get_libtorrent_version(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1266
        data = {"method": "core.get_libtorrent_version", "params": []}
        return self.post(**data)

    def get_completion_paths(self, args=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1277
        data = {"method": "core.get_completion_paths", "params": [args]}
        return self.post(**data)

    def get_known_accounts(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1284
        data = {"method": "core.get_known_accounts", "params": []}
        return self.post(**data)

    def get_auth_levels_mappings(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1288
        data = {"method": "core.get_auth_levels_mappings", "params": []}
        return self.post(**data)

    def create_account(self, username=None, password=None, authlevel=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1292
        data = {"method": "core.create_account", "params": [username, password, authlevel]}
        return self.post(**data)

    def update_account(self, username=None, password=None, authlevel=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1296
        data = {"method": "core.update_account", "params": [username, password, authlevel]}
        return self.post(**data)

    def remove_account(self, username=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/core.py#L1300
        data = {"method": "core.remove_account", "params": [username]}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class daemon_rpc_api:
    def shutdown(self, *args, **kwargs):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/daemon.py#L171
        data = {"method": "daemon.shutdown", "params": [args, kwargs]}
        return self.post(**data)

    def get_method_list(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/daemon.py#L181
        data = {"method": "daemon.get_method_list", "params": []}
        return self.post(**data)

    def get_version(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/daemon.py#L186
        data = {"method": "daemon.get_version", "params": []}
        return self.post(**data)

    def authorized_call(self, rpc=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/core/daemon.py#L191
        data = {"method": "daemon.authorized_call", "params": [rpc]}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class autoadd_rpc_api:
    def set_options(self, watchdir_id=None, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L121
        data = {"method": "autoadd.set_options", "params": [watchdir_id, options]}
        return self.post(**data)

    def enable_watchdir(self, watchdir_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L362
        data = {"method": "autoadd.enable_watchdir", "params": [watchdir_id]}
        return self.post(**data)

    def disable_watchdir(self, watchdir_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L377
        data = {"method": "autoadd.disable_watchdir", "params": [watchdir_id]}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L391
        data = {"method": "autoadd.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L400
        data = {"method": "autoadd.get_config", "params": []}
        return self.post(**data)

    def get_watchdirs(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L405
        data = {"method": "autoadd.get_watchdirs", "params": []}
        return self.post(**data)

    def add(self, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L437
        data = {"method": "autoadd.add", "params": [options]}
        return self.post(**data)

    def remove(self, watchdir_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L462
        data = {"method": "autoadd.remove", "params": [watchdir_id]}
        return self.post(**data)

    def is_admin_level(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L517
        data = {"method": "autoadd.is_admin_level", "params": []}
        return self.post(**data)

    def get_auth_user(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/AutoAdd/deluge_autoadd/core.py#L521
        data = {"method": "autoadd.get_auth_user", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class blocklist_rpc_api:
    def check_import(self, force=False):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Blocklist/deluge_blocklist/core.py#L132
        data = {"method": "blocklist.check_import", "params": [force]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Blocklist/deluge_blocklist/core.py#L169
        data = {"method": "blocklist.get_config", "params": []}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Blocklist/deluge_blocklist/core.py#L179
        data = {"method": "blocklist.set_config", "params": [config]}
        return self.post(**data)

    def get_status(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Blocklist/deluge_blocklist/core.py#L254
        data = {"method": "blocklist.get_status", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class execute_rpc_api:
    def add_command(self, event=None, command=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Execute/deluge_execute/core.py#L156
        data = {"method": "execute.add_command", "params": [event, command]}
        return self.post(**data)

    def get_commands(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Execute/deluge_execute/core.py#L165
        data = {"method": "execute.get_commands", "params": []}
        return self.post(**data)

    def remove_command(self, command_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Execute/deluge_execute/core.py#L169
        data = {"method": "execute.remove_command", "params": [command_id]}
        return self.post(**data)

    def save_command(self, command_id=None, event=None, cmd=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Execute/deluge_execute/core.py#L180
        data = {"method": "execute.save_command", "params": [command_id, event, cmd]}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class extractor_rpc_api:
    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Extractor/deluge_extractor/core.py#L183
        data = {"method": "extractor.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Extractor/deluge_extractor/core.py#L190
        data = {"method": "extractor.get_config", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class label_rpc_api:
    def get_labels(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L173
        data = {"method": "label.get_labels", "params": []}
        return self.post(**data)

    def add(self, label_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L178
        data = {"method": "label.add", "params": [label_id]}
        return self.post(**data)

    def remove(self, label_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L193
        data = {"method": "label.remove", "params": [label_id]}
        return self.post(**data)

    def set_options(self, label_id=None, options_dict=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L272
        data = {"method": "label.set_options", "params": [label_id, options_dict]}
        return self.post(**data)

    def get_options(self, label_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L307
        data = {"method": "label.get_options", "params": [label_id]}
        return self.post(**data)

    def set_torrent(self, torrent_id=None, label_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L312
        data = {"method": "label.set_torrent", "params": [torrent_id, label_id]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L334
        data = {"method": "label.get_config", "params": []}
        return self.post(**data)

    def set_config(self, options=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Label/deluge_label/core.py#L341
        data = {"method": "label.set_config", "params": [options]}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class notifications_rpc_api:
    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Notifications/deluge_notifications/core.py#L219
        data = {"method": "notifications.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Notifications/deluge_notifications/core.py#L226
        data = {"method": "notifications.get_config", "params": []}
        return self.post(**data)

    def get_handled_events(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Notifications/deluge_notifications/core.py#L231
        data = {"method": "notifications.get_handled_events", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class scheduler_rpc_api:
    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Scheduler/deluge_scheduler/core.py#L154
        data = {"method": "scheduler.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Scheduler/deluge_scheduler/core.py#L162
        data = {"method": "scheduler.get_config", "params": []}
        return self.post(**data)

    def get_state(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Scheduler/deluge_scheduler/core.py#L167
        data = {"method": "scheduler.get_state", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class stats_rpc_api:
    def get_stats(self, keys=None, interval=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L175
        data = {"method": "stats.get_stats", "params": [keys, interval]}
        return self.post(**data)

    def get_totals(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L190
        data = {"method": "stats.get_totals", "params": []}
        return self.post(**data)

    def get_session_totals(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L198
        data = {"method": "stats.get_session_totals", "params": []}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L209
        data = {"method": "stats.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L216
        data = {"method": "stats.get_config", "params": []}
        return self.post(**data)

    def get_intervals(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Stats/deluge_stats/core.py#L221
        data = {"method": "stats.get_intervals", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class toggle_rpc_api:
    def get_status(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Toggle/deluge_toggle/core.py#L39
        data = {"method": "toggle.get_status", "params": []}
        return self.post(**data)

    def toggle(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/Toggle/deluge_toggle/core.py#L43
        data = {"method": "toggle.toggle", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class webui_rpc_api:
    def got_deluge_web(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/WebUi/deluge_webui/core.py#L54
        data = {"method": "webui.got_deluge_web", "params": []}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/WebUi/deluge_webui/core.py#L94
        data = {"method": "webui.set_config", "params": [config]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/plugins/WebUi/deluge_webui/core.py#L118
        data = {"method": "webui.get_config", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class auth_rpc_api:
    def change_password(self, old_password=None, new_password=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/auth.py#L208
        data = {"method": "auth.change_password", "params": [old_password, new_password]}
        return self.post(**data)

    def check_session(self, session_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/auth.py#L222
        data = {"method": "auth.check_session", "params": [session_id]}
        return self.post(**data)

    def delete_session(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/auth.py#L232
        data = {"method": "auth.delete_session", "params": []}
        return self.post(**data)

    def login(self, password=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/auth.py#L243
        data = {"method": "auth.login", "params": [password]}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class web_rpc_api:
    def connect(self, host_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L455
        data = {"method": "web.connect", "params": [host_id]}
        return self.post(**data)

    def connected(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L470
        data = {"method": "web.connected", "params": []}
        return self.post(**data)

    def disconnect(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L480
        data = {"method": "web.disconnect", "params": []}
        return self.post(**data)

    def update_ui(self, keys=None, filter_dict=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L493
        data = {"method": "web.update_ui", "params": [keys, filter_dict]}
        return self.post(**data)

    def get_torrent_status(self, torrent_id=None, keys=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L637
        data = {"method": "web.get_torrent_status", "params": [torrent_id, keys]}
        return self.post(**data)

    def get_torrent_files(self, torrent_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L645
        data = {"method": "web.get_torrent_files", "params": [torrent_id]}
        return self.post(**data)

    def download_torrent_from_url(self, url=None, cookie=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L660
        data = {"method": "web.download_torrent_from_url", "params": [url, cookie]}
        return self.post(**data)

    def get_torrent_info(self, filename=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L690
        data = {"method": "web.get_torrent_info", "params": [filename]}
        return self.post(**data)

    def get_magnet_info(self, uri=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L717
        data = {"method": "web.get_magnet_info", "params": [uri]}
        return self.post(**data)

    def add_torrents(self, torrents=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L722
        data = {"method": "web.add_torrents", "params": [torrents]}
        return self.post(**data)

    def get_hosts(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L777
        data = {"method": "web.get_hosts", "params": []}
        return self.post(**data)

    def get_host_status(self, host_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L785
        data = {"method": "web.get_host_status", "params": [host_id]}
        return self.post(**data)

    def add_host(self, host=None, port=None, username='', password=''):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L800
        data = {"method": "web.add_host", "params": [host, port, username, password]}
        return self.post(**data)

    def edit_host(self, host_id=None, host=None, port=None, username='', password=''):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L821
        data = {"method": "web.edit_host", "params": [host_id, host, port, username, password]}
        return self.post(**data)

    def remove_host(self, host_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L838
        data = {"method": "web.remove_host", "params": [host_id]}
        return self.post(**data)

    def start_daemon(self, port=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L851
        data = {"method": "web.start_daemon", "params": [port]}
        return self.post(**data)

    def stop_daemon(self, host_id=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L858
        data = {"method": "web.stop_daemon", "params": [host_id]}
        return self.post(**data)

    def get_config(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L893
        data = {"method": "web.get_config", "params": []}
        return self.post(**data)

    def set_config(self, config=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L907
        data = {"method": "web.set_config", "params": [config]}
        return self.post(**data)

    def get_plugins(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L922
        data = {"method": "web.get_plugins", "params": []}
        return self.post(**data)

    def get_plugin_info(self, name=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L939
        data = {"method": "web.get_plugin_info", "params": [name]}
        return self.post(**data)

    def get_plugin_resources(self, name=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L944
        data = {"method": "web.get_plugin_resources", "params": [name]}
        return self.post(**data)

    def upload_plugin(self, filename=None, path=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L949
        data = {"method": "web.upload_plugin", "params": [filename, path]}
        return self.post(**data)

    def register_event_listener(self, event=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L976
        data = {"method": "web.register_event_listener", "params": [event]}
        return self.post(**data)

    def deregister_event_listener(self, event=None):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L986
        data = {"method": "web.deregister_event_listener", "params": [event]}
        return self.post(**data)

    def get_events(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L996
        data = {"method": "web.get_events", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass


class webutils_rpc_api:
    def get_languages(self):
        # https://github.com/deluge-torrent/deluge/tree/develop/deluge/ui/web/json_api.py#L1012
        data = {"method": "webutils.get_languages", "params": []}
        return self.post(**data)

    def post(self, *args, **kwargs):
        pass

