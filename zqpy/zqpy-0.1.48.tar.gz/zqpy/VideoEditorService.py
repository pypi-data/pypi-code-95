from moviepy.editor import *
from natsort import natsorted
from PIL import Image
import os, glob, hashlib, shutil
class VideoEditorServiceClass():
    # 视频截取
    def video_subclip(self, video_path, save_path, start_pos, end_pos, is_relative_end_pos = False):
        tempPath, save_path = self._video_path_handle(video_path, save_path)
        video = VideoFileClip(video_path)
        if is_relative_end_pos:
            # 剪辑视频，从x秒开始到视频结尾前x秒
            video = video.subclip(start_pos, video.duration-end_pos)
        else:
            # 剪辑视频，截取视频前x秒
            video = video.subclip(start_pos, end_pos)
        video.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, video, None, '')

    # 合成文件夹下所有的视频
    def video_merge_all_video_by_dir(self, dir_path, save_path, suffix_name='.mp4'):
        video_list = []
        # 访问 video 文件夹 (假设视频都放在这里面)
        for root, dirs, files in os.walk(dir_path):
            # 按文件名排序
            # files.sort() # 原 1.mp4, 2.mp4, 10.mp4.  排序后  1.mp4, 10.mp4, 2.mp4.
            files = natsorted(files) # 原 1.mp4, 2.mp4, 10.mp4. 排序后  1.mp4, 2.mp4, 10.mp4.
            # 遍历所有文件
            for file in files:
                # 如果后缀名为 .mp4
                if os.path.splitext(file)[1] == suffix_name:
                    # 拼接成完整路径
                    filePath = os.path.join(root, file)
                    video_list.append(filePath)
        if len(video_list) == 0:
            return self.result_param(False, save_path, None, None, '列表为空')
        return self.video_merge_all_video_by_list(video_list, save_path, suffix_name)

    # 合成列表所有的视频
    def video_merge_all_video_by_list(self, video_list, save_path, suffix_name='.mp4'):
        # 定义一个数组
        target_list= []
        # 遍历所有文件
        for file_path in video_list:
            # 如果后缀名为 .mp4
            if os.path.splitext(file_path)[1] == suffix_name:
                # 载入视频
                video = VideoFileClip(file_path)
                # 添加到数组
                target_list.append(video)
        if len(target_list) == 0:
            return self.result_param(False, save_path, None, None, '文件列表是空的')
        try:
            # 拼接视频
            final_clip = concatenate_videoclips(target_list)
            # 生成目标视频文件
            final_clip.to_videofile(save_path, fps=25, remove_temp=True)
            return self.result_param(True, save_path, final_clip, None, '')
        except BaseException as e:
            return self.result_param(False, save_path, None, None, str(e))

    # 视频播放区域裁剪
    def video_crop(self, video_path, save_path, x_center, y_center, width, height):
        video = VideoFileClip(video_path)
        final_clip = video.crop(x_center=x_center, y_center=y_center, width=width, height=height)
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 改变视频分辨率,可能花屏
    def video_resize(self, video_path, save_path, width, height):
        video = VideoFileClip(video_path)
        final_clip = video.resize(newsize=(width, height))
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 把文件夹下所有图片合成视频
    def video_images_clip_by_dir(self, dir_path, save_path, fps=25, suffix_name='.jpg'):
        pic_list = []
        for root, dirs, files in os.walk(dir_path):
            # 按文件名排序
            # files.sort() # 原 1.mp4, 2.mp4, 10.mp4.  排序后  1.mp4, 10.mp4, 2.mp4.
            files = natsorted(files) # 原 1.mp4, 2.mp4, 10.mp4. 排序后  1.mp4, 2.mp4, 10.mp4.
            # 遍历所有文件
            for file in files:
                # 如果后缀名为 .mp4
                if os.path.splitext(file)[1] == suffix_name:
                    # 拼接成完整路径
                    filePath = os.path.join(root, file)
                    pic_list.append(filePath)
        if len(pic_list) == 0:
            return self.result_param(False, save_path, None, None, '列表为空')
        return self.video_images_clip_by_list(pic_list, save_path, fps, suffix_name)

    # 把图片列表合成视频
    def video_images_clip_by_list(self, pic_list, save_path, fps=25, suffix_name='.jpg'):
        target_list= []
        for pic_path in pic_list:
            if os.path.splitext(pic_path)[1] == suffix_name:
                # 添加到数组
                target_list.append(pic_path)
        if len(target_list)==0:
            return self.result_param(False, save_path, None, None, '列表为空')
        try:
            final_clip = ImageSequenceClip(pic_list, fps=fps)
            final_clip.to_videofile(save_path, fps=fps, remove_temp=True)
        except BaseException as e:
            print("很大可能是图片不一样大，可以调用images_resize_by_dir 或者 images_resize_by_list 统一设置图片大小")
            return self.result_param(False, save_path, None, None, str(e))
        return self.result_param(True, save_path, final_clip, None, '')

    # 把两个视频放在一个画面上同时播放(左右)
    def video_merge_video_to_one_canvas(self, video_list, save_path):
        video1 = VideoFileClip(video_list[0])
        video2 = VideoFileClip(video_list[1])
        # 注意：.set_position([x1, y1])中的x1，y1为视频左上角的坐标
        target1 = video1.set_position([0, 0])
        target2 = video2.set_position([video1.w, 0])
        final_clip = CompositeVideoClip([target1, target2], size=(video1.w+video2.w, video1.h))
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 把两个视频放在一个画面上同时播放(自定义位置)
    def video_merge_video_to_one_canvas_by_pos(self, video_list, save_path, position):
        video1 = VideoFileClip(video_list[0])
        video2 = VideoFileClip(video_list[1])
        # 注意：.set_position([x1, y1])中的x1，y1为视频左上角的坐标
        target1 = video1.set_position([0, 0])
        target2 = video2.set_position(position)
        final_clip = CompositeVideoClip([target1, target2], size=(video1.w+video2.w, video1.h))
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 路径需要带后缀 VideoFileClipPathList
    def video_merge_list_all_video(self, video_path_list, save_path):
        clips = []
        clip = None
        for videoPath in video_path_list:
            try:
                clip = VideoFileClip(videoPath)
            except BaseException as e:
                print("video_merge_list_all_video Error " + str(e))
                clip = None
            finally:
                if clip != None:
                    clips.append(clip)
        if len(clips) == 0 :
            return self.result_param(False, save_path, None, None, '列表为空')
        
        final_clip = concatenate_videoclips(clips)
        # mp4文件默认用libx264编码， 比特率单位bps
        # final_clip.write_videofile(save_path, codec="libx264", bitrate="10000000") 
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 改变视频MD5，路径需要带后缀 VideoFileClipPath
    def video_change_md5(self, videoPath, save_path):
        tempPath, save_path = self._video_path_handle(videoPath, save_path)
        return self.video_merge_list_all_video([tempPath], save_path)

    # 视频路径处理，重名那种
    def _video_path_handle(self, videoPath, save_path):
        tempPath = videoPath
        if videoPath == save_path:
            tempFileName = "tempVideo"
            [dirName,fileName]=os.path.split(videoPath)
            fileName = "-y.mp4"
            if dirName == "":
                tempPath = "{}_{}".format(tempFileName,fileName)
            else:
                tempPath = "{}/{}_{}".format(dirName,tempFileName,fileName)
            shutil.copyfile(videoPath,tempPath)
        return tempPath, save_path

    # 视频添加LOG  VideoClipAddLogoPath
    def video_add_log(self, videoPath, save_path, logoPngPath = None, logoTextStr = None, color='white', align='center', fontsize = 25, left=0, top=0, right=0, bottom=0, opacity=0, pos=('center','center'), fontPath=None):
        tempPath, save_path = self._video_path_handle(videoPath, save_path)
        if logoPngPath == None and logoTextStr == None:
            return self.result_param(False, save_path, None, None, '没有设置水印')

        clipList = []        
        video = VideoFileClip(tempPath)
        clipList.append(video)
        logoPngClip = None
        logoTextClip = None
        if logoPngPath != None:
            logoPngClip = (ImageClip(logoPngPath)
                    .set_duration(video.duration)  # 水印持续时间
                    .resize(height=50)  # 水印的高度，会等比缩放
                    .margin(left=left, top=top, right=right, bottom=bottom, opacity = opacity)# 水印边距和透明度
                    .set_pos(pos))  # 水印的位置
            clipList.append(logoPngClip)

        if logoTextStr != None:
            FONT_URL = fontPath or r'C:/Windows/Fonts/simsun.ttc'  #r'C:\Windows\Fonts\simhei.ttf'    #C:\Windows\Fonts\STXINGKA.TTF'
            if not os.path.exists(FONT_URL):
                print("字体文件不存在 %s"%FONT_URL)
                return False
            logoTextClip = (TextClip(txt=logoTextStr, color=color, size=(640, 480), method='caption',
                    align=align, fontsize=fontsize, font=FONT_URL)
                    .set_duration(video.duration)
                    .margin(left=left, top=top, right=right, bottom=bottom, opacity = opacity)
                    .set_pos(pos))  # 水印的位置
            clipList.append(logoTextClip)

        if len(clipList) == 0:
            return self.result_param(False, save_path, None, None, '列表为空')
        final_clip = CompositeVideoClip(clipList)
        # mp4文件默认用libx264编码， 比特率单位bps
        # final_clip.write_videofile(save_path, codec="libx264", bitrate="10000000") 
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return self.result_param(True, save_path, final_clip, None, '')

    # 视频添加封面
    def video_add_cover(self, pic_list, video_path, save_path, cover_video_path=None, fps=25, suffix_name='.jpg'):
        video = VideoFileClip(video_path)
        if not cover_video_path:
            cover_video_path = save_path
        for item in pic_list:
            img = Image.open(item)
            if video.size != list(img.size):
                try:
                    new_img = img.resize((video.w, video.h), Image.BILINEAR)
                    new_img.save(item)
                except Exception as e:
                    print(e)
            
        result = self.video_images_clip_by_list(pic_list, cover_video_path, fps, suffix_name)
        if result and result['status']:
            return self.video_merge_all_video_by_list([cover_video_path, video_path], save_path)
        return self.result_param(False, save_path, None, result, result['msg'])

    # 视频添加封面
    def video_add_cover_by_num(self, pic, video_path, save_path, cover_video_path=None, picNum=25, fps=25, suffix_name='.jpg'):
        picList = []
        for item in range(0, picNum):
            picList.append(pic)
        else:
            picList.append(pic)
        return self.video_add_cover(picList, video_path, save_path, cover_video_path, fps, suffix_name)

    # 提取视频中的音频
    def video_get_audio(self, video_path, out_audio_path):
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(out_audio_path)
        return self.result_param(True, out_audio_path, video, audio, '')

    # 为视频添加另一个视频的音频  source 声音添加到 target
    def video_add_audio_by_video(self, video_path_source, video_path_target, out_video_path):
        video_source = VideoFileClip(video_path_source)
        video_target = VideoFileClip(video_path_target)
        audio = video_source.audio
        videoclip = video_target.set_audio(audio)
        videoclip.write_videofile(out_video_path, audio_codec="aac")
        return self.result_param(True, out_video_path, videoclip, None, '')

    # 为视频添加的音频
    def video_add_audio_by_audio(self, video_path, audio_path, out_video_path):
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path).subclip(0, video.duration)
        videoclip = video.set_audio(audio)
        videoclip.write_videofile(out_video_path, audio_codec="aac")
        return self.result_param(True, out_video_path, videoclip, None, '')

    # --------------------------------------------Tools Start------------------------------------------------
    # 常规返回数据类型
    def result_param(self, status, path, video, obj, msg):
        return {'status':status, 'path': path, 'video': video, 'obj': obj, 'msg': msg}

    # 获取某个文件夹下的所有指定后缀的文件
    def get_dir_all_suffix_name_file(self, dir_path, suffix_name='.png'):
        target_list = []
        for jpgfile in glob.glob(dir_path+'*'+suffix_name):
            target_list.append(jpgfile)
        return target_list

    # 改变某个文件夹下所有指定后缀文件的大小，并保存到指定文件夹下
    def images_resize_by_dir(self, dir_path, save_dir_path, width, height, suffix_name='.png'):
        source_list = self.get_dir_all_suffix_name_file(dir_path, suffix_name)
        for img_path in source_list:
            img_dir = os.path.dirname(img_path)
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            img = Image.open(img_path)
            try:
                new_img = img.resize((width, height), Image.BILINEAR)
                new_img.save(os.path.join(save_dir_path, os.path.basename(img_path)))
            except Exception as e:
                print(e)
        return self.result_param(True, save_dir_path, None, None, '')

    #大文件的MD5值
    def video_file_md5(self, filename):
        if not os.path.isfile(filename):
            return
        myhash = hashlib.md5()
        f = open(filename,'rb')
        while True:
            b = f.read(8096)
            if not b :
                break
            myhash.update(b)
        f.close()
        return myhash.hexdigest()
# 日志系统
# __log = LogServiceClass(tag="VideoEditorServiceClass")
# LogD = __log.LogD
# LogW = __log.LogW
# LogE = __log.LogE
# --------------------------------------------Tools End-------------------------------------------------------

if __name__ == "__main__":
    dir_path = os.path.dirname(__file__)
    VideoEditorService = VideoEditorServiceClass()
    # print(VideoEditorService.video_subclip('%s/video/6718334266993855751-y.mp4'%dir_path, '%s/testinput/video_subclip.mp4'%dir_path, 0, 2, True))
    # print(VideoEditorService.video_subclip('%s/video/6763209833844968715.mp4'%dir_path, '%s/testinput/video_subclip.mp4'%dir_path, 4, 2, True))
    
    # print(VideoEditorService.video_merge_all_video_by_dir('%s/video/'%dir_path, '%s/testinput/video_merge_all_video_by_dir.mp4'%dir_path))
    # print(VideoEditorService.video_crop('%s/video/6763209833844968715.mp4'%dir_path, '%s/testinput/video_crop.mp4'%dir_path, 0, 0, 100, 100)) # 未成功
    # print(VideoEditorService.video_resize('%s/video/6763209833844968715.mp4'%dir_path, '%s/testinput/video_resize.mp4'%dir_path, 300, 300))

    # VideoEditorService.images_resize_by_dir('%s/restricted/'%dir_path, '%s/resizeimg/'%dir_path, 100, 100, '.png')
    # print(VideoEditorService.video_images_clip_by_dir('%s/resizeimg'%dir_path, '%s/testinput/video_images_clip_by_dir.mp4'%dir_path, 10, '.png'))

    # print(VideoEditorService.video_merge_video_to_one_canvas(['%s/video/6763209833844968715.mp4'%dir_path, '%s/video/6763449160764034315.mp4'%dir_path], '%s/testinput/video_merge_video_to_one_canvas.mp4'%dir_path))