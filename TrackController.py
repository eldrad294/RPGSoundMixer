import time, os, sys, yaml

from audioplayer import AudioPlayer # https://pypi.org/project/audioplayer/
from random import randint
from multiprocessing import Process
from pytube import YouTube, Playlist
from pydub import AudioSegment

class Track:

    def __init__(self, path):
        self.path = path
        self.ap = AudioPlayer(
            filename=path
        )
        
    def start(self, loop=False, volume=50, block=True):
        self.ap.volume=volume
        self.ap.play(
            loop=loop,
            block=block
        )

    def stop(self):
        current_volume = self.ap.volume
        for i in range(current_volume):
            self.ap.volume = self.ap.volume-1
            time.sleep(.2)
        self.ap.stop()

    def __del__(self):
        self.stop()

class TrackPlayer:

    def __init__(self, path):
        self.path = path
        self.music_track_process = None
        self.ambient_track_process = None

    @staticmethod
    def parallel_music_player(path, option):
        track_path = TrackPlayer.__generate_random_track(path=path, option=option)
        if track_path is None:
            print('No tracks for option [' + str(option) + ']')
        else:
            Track(
                os.path.join(
                    path, 
                    option, 
                    track_path
                )
            ).start(
                loop=False,
                volume=80,
                block=True
            )
            TrackPlayer.parallel_music_player(path=path, option=option)

    @staticmethod
    def parallel_ambience_player(path, option, ambient_track):
        if ambient_track is None:
            print('No tracks for option [' + str(option) + ']')
        else:
            Track(
                os.path.join(
                    path, 
                    option, 
                    ambient_track
                )
            ).start(
                loop=True,
                volume=100,
                block=True
            )
            TrackPlayer.parallel_ambience_player(path=path, option=option, ambient_track=ambient_track)

    def generate_menu(self):
        while True:
            print('\n-----RPG Sound Mixer-----')
            option, option_dic = TrackPlayer.__print_menu(path=self.path, ambience=False)

            if option_dic[option].lower() == 'exit':
                if self.music_track_process is not None:
                     self.music_track_process.terminate()
                if self.ambient_track_process is not None:
                     self.ambient_track_process.terminate()
                print('Exiting..')
                exit(0)
            elif option_dic[option].lower() == 'ambience':
                print('\n-----RPG Ambience Selection-----')
                ambient_option, ambient_dic = TrackPlayer.__print_menu(path=os.path.join(self.path,option_dic[option]), ambience=True)
                p = Process(target=TrackPlayer.parallel_ambience_player, args=(self.path, option_dic[option], ambient_dic[ambient_option]))
                p.start()
                if self.ambient_track_process is not None:
                    time.sleep(5)
                    self.ambient_track_process.terminate()
                self.ambient_track_process=p
            else:
                p = Process(target=TrackPlayer.parallel_music_player, args=(self.path, option_dic[option]))
                p.start()
                if self.music_track_process is not None:
                    time.sleep(5)
                    self.music_track_process.terminate()
                self.music_track_process=p
                
            TrackPlayer.__screen_clear()

    @staticmethod
    def __print_menu(path, ambience=False):
        option_list, option_dic = sorted(os.listdir(path)), {}
        for i in range(1, len(option_list)+1):
            print(str(i) + ') ' + option_list[i-1])
            option_dic[i] = option_list[i-1]
        if not ambience:
            option_dic[len(option_list)+1] = 'Exit'
            print(str(len(option_list)+1) + ') ' + option_dic[len(option_list)+1])
        return int(input('\nEnter number to load new track.. ')), option_dic

    @staticmethod
    def __generate_random_track(path, option):
        track_list = os.listdir(os.path.join(path, option))
        if len(track_list) == 0:
            return None
        track_index = randint(0, len(track_list)-1)
        return track_list[track_index]

    @staticmethod
    def __screen_clear():
        # for mac and linux(here, os.name is 'posix')
        if os.name == 'posix':
            _ = os.system('clear')
        else:
            # for windows platfrom
            _ = os.system('cls')

class AudioDownloader:

    @staticmethod
    def refresh_playlist(p_playlist_path, p_playlist_dictionary):
        for key, value in p_playlist_dictionary.items():
            playlist = Playlist(value)
            playlist_path = os.path.join(p_playlist_path,key)
            if not os.path.exists(playlist_path):
                os.makedirs(playlist_path)
            for url in playlist:
                try:
                    yt = YouTube(url)
                    video_path = os.path.join(playlist_path, yt.title.replace('|','')).replace('\\','/')
                    if not os.path.exists(video_path):
                        print('Downloading [' + yt.title + '] at [' + video_path + '] ..')
                        yt.streams.last().download(playlist_path)
                        
                        print('Converting to ' + video_path + '.mp3')
                        track = AudioSegment.from_file(video_path+'.webm')
                        track.export(video_path+'.mp3', format='mp3')

                        os.remove(video_path + '.webm')
                    else:
                        print('Skipping [' + yt.title + '] because exists in [' + playlist_path + '] ..')
                except Exception as e:
                    raise e       

if __name__ == '__main__':

    with open('config.yml') as f:
        config = yaml.load(f)
    
    playlist_path = config['playlist_path']
    playlist_dictionary = config['playlist']
    download_enabled = config['download_enabled']

    if download_enabled:
        AudioDownloader.refresh_playlist(playlist_path, playlist_dictionary)

    TrackPlayer(config['playlist_path']).generate_menu()