from xml.dom import minidom


class BilibiliGenerator:
    def __init__(self):
        self.root = minidom.Document()
        self.entry_container = self.root.createElement('i')
        self.root.appendChild(self.entry_container)

    def append(self, text, send_time, type=1, size=25, color=0xFFFFFF, create_time=0, pool_type=0, sender_id=0, database_id=0):
        entry = minidom.Document().createElement('d')
        entry.setAttribute('p', '%f,%d,%d,%d,%d,%d,%d,%d' % (
            send_time,          # 1. 弹幕发送相对视频的时间（以前是以秒为单位的整数，现在用浮点记了，更精准）
            type,               # 2. 弹幕类型：1~3（但貌似只见过1）滚动弹幕、4底端弹幕、5顶端弹幕、6逆向弹幕、7精准定位、8高级弹幕【默认是1，基本以1、4、5多见】
            size,               # 3. 字号：12非常小,16特小,18小,25中,36大,45很大,64特别大【默认是25】
            color,              # 4. 字体颜色：不是RGB而是十进制
            create_time,        # 5. 弹幕发送时的UNIX时间戳，基准时间1970-1-1 08:00:00
            pool_type,          # 6. 弹幕池类型：0普通 1字幕 2特殊
            sender_id,          # 7. 发送者ID【注意不是uid，具体怎么关联的还不清楚，屏蔽用】
            database_id         # 8. 弹幕在数据库的ID
        ))
        entry.appendChild(minidom.Document().createTextNode(text))
        self.entry_container.appendChild(entry)

    def output(self):
        return self.root.toprettyxml(encoding='utf-8')