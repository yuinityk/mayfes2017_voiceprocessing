#-*- coding:utf-8 -*-
import MeCab
import random
import copy
import sys
import pyaudio
import wave
import requests
import jtalk
import subprocess

accept = ['名詞-一般']
va = ['ア','ァ','カ','サ','タ','ナ','ハ','マ','ヤ','ャ','ラ','ワ','ガ','ザ','ダ','バ','パ',     'あ','ぁ','か','さ','た','な','は','ま','や','ゃ','ら','わ','が','ざ','だ','ば','ぱ']
vi = ['イ','ィ','キ','シ','チ','ニ','ヒ','ミ',          'リ',     'ギ','ジ','ヂ','ビ','ピ',     'い','ぃ','き','し','ち','に','ひ','み',          'り',     'ぎ','じ','ぢ','び','ぴ']
vu = ['ウ','ゥ','ク','ス','ツ','ヌ','フ','ム','ユ','ュ','ル',     'グ','ズ','ヅ','ブ','プ','ヴ','う','ぅ','く','す','つ','ぬ','ふ','む','ゆ','ゅ','る',     'ぐ','ず','づ','ぶ','ぷ']
ve = ['エ','ェ','ケ','セ','テ','ネ','ヘ','メ',          'レ',     'ゲ','ゼ','デ','ベ','ペ',     'え','ぇ','け','せ','て','ね','へ','め',          'れ',     'げ','ぜ','で','べ','ぺ']
vo = ['オ','ォ','コ','ソ','ト','ノ','ホ','モ','ヨ','ョ','ロ','ヲ','ゴ','ゾ','ド','ボ','ポ',     'お','ぉ','こ','そ','と','の','ほ','も','よ','ょ','ろ','を','ご','ぞ','ど','ぼ','ぽ']
yoon = ['ァ','ィ','ゥ','ェ','ォ','ャ','ュ','ョ','ぁ','ぃ','ぅ','ぇ','ぉ','ゃ','ゅ','ょ']

#wave const
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

APIKEY = '6e4a37754e6b425465433566567a643155382e4a6148425152747678616f7330593975534d616b57354136'
#path = '/home/yuinityk/OneDrive/workspace/ShiritoriAI/output.wav'
path = 'output.wav'
url = "https://api.apigw.smt.docomo.ne.jp/amiVoice/v1/recognize?APIKEY={}".format(APIKEY)

mecab = MeCab.Tagger('-Ochasen')
mecab.parse('')

def get_usbmicindex():
    p = pyaudio.PyAudio()
    count = p.get_device_count()
    for i in range(count):
        if 'USB' in p.get_device_info_by_index(i)['name']:
            return i
    return -1

def record(FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=48000, CHUNK=1024, RECORD_SECONDS=3, WAVE_OUTPUT_FILENAME="output.wav"):
    p = pyaudio.PyAudio()
    idx = get_usbmicindex()
    if idx == -1:
        print('connect USB microphone.')
        return 0

    stream = p.open(format = FORMAT,
            channels = CHANNELS,
            rate = RATE,
            input = True,
            input_device_index=idx,
            frames_per_buffer = CHUNK)
    frames = []
    print("* recording...")
    for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK,exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate
    print("* done recording.")

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
	
    subprocess.call("sox output.wav -r 16000 put.wav",shell=True)#down sampling
    subprocess.call("sox put.wav output.wav gain -n",shell=True)

def get_sentence():
    files = {"a": open(path, 'rb'), "v": "on"}
    r = requests.post(url, files=files)
    return r.json()['text'].rstrip('、。1234567890')

def get_headntail(d):
    files = {"a": open(path, 'rb'), "v": "on"}
    r = requests.post(url, files=files)
    print(r.json())
    if r.json()['results'][0]['tokens'][0]['spoken'] == '_on':
        return '_on','_on'
    if d != 'reverse':
        head = to_katakana(r.json()['results'][0]['tokens'][0]['spoken'][0])
        tail = to_katakana(get_endletter(r.json()['results'][0]['tokens'][len(r.json()['results'][0]['tokens'])-2]['spoken']))
    else:
        head = to_katakana(get_endletter(r.json()['results'][0]['tokens'][len(r.json()['results'][0]['tokens'])-2]['spoken']))
        tail = to_katakana(r.json()['results'][0]['tokens'][0]['spoken'][0])
    return head,tail

def load_dic(diff):
    """
    難易度diffの辞書をcsvから読み込んで返す
    """
    wdic = {}
    f = open('dic_' + diff + '.csv','r')
    for line in f:
        t,w = line.split(",")
        w = w.rstrip()
        if t in wdic.keys():
            wdic[t].append(w)
        else:
            wdic[t]=[w]
    f.close()
    return wdic

def to_katakana(h):
    dic = {'あ':'ア', 'い':'イ', 'う':'ウ', 'え':'エ', 'お':'オ',
           'か':'カ', 'き':'キ', 'く':'ク', 'け':'ケ', 'こ':'コ',
           'さ':'サ', 'し':'シ', 'す':'ス', 'せ':'セ', 'そ':'ソ',
           'た':'タ', 'ち':'チ', 'つ':'ツ', 'て':'テ', 'と':'ト',
           'な':'ナ', 'に':'ニ', 'ぬ':'ヌ', 'ね':'ネ', 'の':'ノ',
           'は':'ハ', 'ひ':'ヒ', 'ふ':'フ', 'へ':'ヘ', 'ほ':'ホ',
           'ま':'マ', 'み':'ミ', 'む':'ム', 'め':'メ', 'も':'モ',
           'や':'ヤ',            'ゆ':'ユ',            'よ':'ヨ',
           'ら':'ラ', 'り':'リ', 'る':'ル', 'れ':'レ', 'ろ':'ロ',
           'わ':'ワ',                                  'を':'ヲ',
           'ん':'ン',
           'が':'ガ', 'ぎ':'ギ', 'ぐ':'グ', 'げ':'ゲ', 'ご':'ゴ',
           'ざ':'ザ', 'じ':'ジ', 'ず':'ズ', 'ぜ':'ゼ', 'ぞ':'ゾ',
           'だ':'ダ', 'ぢ':'ヂ', 'づ':'ヅ', 'で':'デ', 'ど':'ド',
           'ば':'バ', 'び':'ビ', 'ぶ':'ブ', 'べ':'ベ', 'ぼ':'ボ',
           'ぱ':'パ', 'ぴ':'ピ', 'ぷ':'プ', 'ぺ':'ペ', 'ぽ':'ポ',
           'うぇ':'ウェ', 
           'きゃ':'キャ',        'きゅ':'キュ',        'きょ':'キョ',
           'ぎゃ':'ギャ',        'ぎゅ':'ギュ',        'ぎょ':'ギョ',
           'くぃ':'クィ',
           'しゃ':'シャ', 'しゅ':'シュ', 'しぇ':'シェ', 'しょ':'ショ',
           'じゃ':'ジャ', 'じゅ':'ジュ', 'じぇ':'ジェ', 'じょ':'ジョ',
           'ちゃ':'チャ', 'ちゅ':'チュ', 'ちぇ':'チェ', 'ちょ':'チョ',
           'つぁ':'ツァ', 'つぃ':'ツィ', 'つぇ':'ツェ', 'つぉ':'ツォ',
           'てぃ':'ティ', 'てゅ':'テュ', 'でぃ':'ディ', 'でゅ':'デュ',
           'とぅ':'トゥ', 'どぅ':'ドゥ',
           'にゃ':'ニャ',        'にゅ':'ニュ',        'にょ':'ニョ',
           'ひゃ':'ヒャ',        'ひゅ':'ヒュ',        'ひょ':'ヒョ',
           'びゃ':'ビャ',        'びゅ':'ビュ',        'びょ':'ビョ',
           'ぴゃ':'ピャ',        'ぴゅ':'ピュ',        'ぴょ':'ピョ',
           'ふぁ':'ファ','ふぃ':'フィ','ふゅ':'フュ','ふぇ':'フェ','ふぉ':'フォ',
           'みゃ':'ミャ',        'みゅ':'ミュ',        'みょ':'ミョ',
           'りゃ':'リャ',        'りゅ':'リュ',        'りょ':'リョ',
           'ア':'ア', 'イ':'イ', 'ウ':'ウ', 'エ':'エ', 'オ':'オ',
           'カ':'カ', 'キ':'キ', 'ク':'ク', 'ケ':'ケ', 'コ':'コ',
           'サ':'サ', 'シ':'シ', 'ス':'ス', 'セ':'セ', 'ソ':'ソ',
           'タ':'タ', 'チ':'チ', 'ツ':'ツ', 'テ':'テ', 'ト':'ト',
           'ナ':'ナ', 'ニ':'ニ', 'ヌ':'ヌ', 'ネ':'ネ', 'ノ':'ノ',
           'ハ':'ハ', 'ヒ':'ヒ', 'フ':'フ', 'ヘ':'ヘ', 'ホ':'ホ',
           'マ':'マ', 'ミ':'ミ', 'ム':'ム', 'メ':'メ', 'モ':'モ',
           'ヤ':'ヤ',            'ユ':'ユ',            'ヨ':'ヨ',
           'ラ':'ラ', 'リ':'リ', 'ル':'ル', 'レ':'レ', 'ロ':'ロ',
           'ワ':'ワ',                                  'ヲ':'ヲ',
           'ン':'ン',
           'ガ':'ガ', 'ギ':'ギ', 'グ':'グ', 'ゲ':'ゲ', 'ゴ':'ゴ',
           'ザ':'ザ', 'ジ':'ジ', 'ズ':'ズ', 'ゼ':'ゼ', 'ゾ':'ゾ',
           'ダ':'ダ', 'ヂ':'ヂ', 'ヅ':'ヅ', 'デ':'デ', 'ド':'ド',
           'バ':'バ', 'ビ':'ビ', 'ブ':'ブ', 'ベ':'ベ', 'ボ':'ボ',
           'パ':'パ', 'ピ':'ピ', 'プ':'プ', 'ペ':'ペ', 'ポ':'ポ',
           'ウェ':'ウェ', 
           'キャ':'キャ',        'キュ':'キュ',        'キョ':'キョ',
           'ギャ':'ギャ',        'ギュ':'ギュ',        'ギョ':'ギョ',
           'クィ':'クィ',
           'シャ':'シャ', 'シュ':'シュ', 'シェ':'シェ', 'ショ':'ショ',
           'ジャ':'ジャ', 'ジュ':'ジュ', 'ジェ':'ジェ', 'ジョ':'ジョ',
           'チャ':'チャ', 'チュ':'チュ', 'チェ':'チェ', 'チョ':'チョ',
           'ツァ':'ツァ', 'ツィ':'ツィ', 'ツェ':'ツェ', 'ツォ':'ツォ',
           'ティ':'ティ', 'テュ':'テュ', 'ディ':'ディ', 'デュ':'デュ',
           'トゥ':'トゥ', 'ドゥ':'ドゥ',
           'ニャ':'ニャ',        'ニュ':'ニュ',        'ニョ':'ニョ',
           'ヒャ':'ヒャ',        'ヒュ':'ヒュ',        'ヒョ':'ヒョ',
           'ビャ':'ビャ',        'ビュ':'ビュ',        'ビョ':'ビョ',
           'ピャ':'ピャ',        'ピュ':'ピュ',        'ピョ':'ピョ',
           'ファ':'ファ','フィ':'フィ','フュ':'フュ','フェ':'フェ','フォ':'フォ',
           'ミャ':'ミャ',        'ミュ':'ミュ',        'ミョ':'ミョ',
           'リャ':'リャ',        'リュ':'リュ',        'リョ':'リョ',
           }
    return dic[h]

def get_endletter(w): 
    """
    与えられた文字列の最後の文字を取得する.
    APIで返ってきた認識結果の末尾には、。が入っていることが多いのでsplitで取り除き,
    末尾がーであれば母音を返す.また,"しょ"などは2文字で1つとして扱う.

    引数
        w : 最後の文字を取得したい文字(str)
    返り値
        wの最後の文字(str)
    """
    if w.rstrip('、。0123456789')[-1] == 'ー':
        endletter = mecab.parse(w.rstrip('ー、。0123456789')).split('\t')[-5][-1]
        if endletter in va:
            return 'ア'
        elif endletter in vi:
            return 'イ'
        elif endletter in vu:
            return 'ウ'
        elif endletter in ve:
            return 'エ'
        elif endletter in vo:
            return 'オ'
        elif endletter in ['ン','ん']:
            return 'ン'
        else:
            f = open('error.log','a')
            f.write('get_endletter error(-): ' + endletter + '\n')
            f.close()

    endletter = mecab.parse(w.rstrip('ー、。0123456789')).split('\t')[-5][-1]
    if endletter in yoon:
        el = mecab.parse(w.rstrip('ー、。0123456789')).split('\t')[-5]
        #「きょうじゅ」が「きょうじ+ゅ」になったりする
        if len(el) == 1:
            if el in ['ャ','ゃ']:
                return 'ヤ'
            elif el in ['ュ','ゅ']:
                return 'ユ'
            elif el in ['ョ','ゅ']:
                return 'ヨ'
            elif el in ['ァ','ぁ']:
                return 'ア'
            elif el in ['ィ','ぃ']:
                return 'イ'
            elif el in ['ゥ','ぅ']:
                return 'ウ'
            elif el in ['ェ','ぇ']:
                return 'エ'
            elif el in ['ォ','ぉ']:
                return 'オ'
        else:
            return el[-2:]
    elif endletter in va or endletter in vi or endletter in vu or endletter in ve or endletter in vo:
        return mecab.parse(w.rstrip('ー、。0123456789')).split('\t')[-5][-1]
    elif endletter in ['ン','ん']:
        return 'ン'
    else:
        f = open('error.log','a')
        f.write('get_endletter error(parse): ' + endletter + '\n')
        f.close()

def return_word(el,wdic):
    return random.choice(wdic[el])

def learn_word(words,savedic): 
    """
    wdicにない単語をsaveに入れて返す.
    wordsに含まれる一般名詞を保存する.

    引数
        words : 保存する単語
        savedic : 保存する単語のリスト
    返り値
        savedicのディープコピーsaveを返す.
        wordsがsavedicに含まれていないならば加える.
    """
    wdic = load_dic('hard')
    save = copy.deepcopy(savedic)
    parsed = mecab.parse(words.rstrip('、。')).split('\t')
    for i in range(len(parsed)):
        if parsed[i] in accept:
            if len(parsed[i-2]) == len([ch for ch in parsed[i-2] if "ア" <= ch <= "ン"]):
                if len(parsed[i-2]) > 1 and parsed[i-2][1] in yoon: #2文字目がャなどのときは最初の2文字をまとめて見る
                        if parsed[i-2] not in wdic[parsed[i-2][:2]]:
                            if parsed[i-2][:2] in save.keys():
                                save[parsed[i-2][:2]].append(parsed[i-2])
                            else:
                                save[parsed[i-2][:2]] = [parsed[i-2]]
                elif parsed[i-2] not in wdic[parsed[i-2][:1]]:
                    if parsed[i-2][:1] in save.keys():
                        save[parsed[i-2][:1]].append(parsed[i-2])
                    else:
                        save[parsed[i-2][:1]] = [parsed[i-2]]
    return save

def dict_update(wdic,add):
    for key in add.keys():
        wdic[key].extend(add[key])

def save_dic(add,mode='a'):
    """
    辞書addに含まれている単語をhardの辞書データに書き込む.
    addはlearn_wordの返り値を投げるようにしている.
    """
    f = open('dic_hard.csv',mode)
    keys = list(add.keys())
    keys.sort()
    for key in keys:
        for word in add[key]:
            f.write(key + ',' + word + '\n')
    f.close()

def wordinput(inputmode = 'rec'):
    """
    しりとりの中プレイヤーの入力部分.
    キーボード入力と音声入力に対応.

    引数
        inputmode : 入力の形式. 'key'ならキーボード入力, 'rec'なら音声入力
    返り値
        入力された単語の末尾の文字
    """
    if inputmode == 'key':
        print('you:',end='')
        w = input()
        return get_endletter(w)
    else:
        print('press any key to record')
        _ = input()
        record()
        w = word_recognize()
        print('you:'+w.strip('、。'))
        return get_endletter(w)

def play(mode = 'endless', diff = 'easy', inputmode = 'rec'):
    """
    しりとり実行

    引数
        mode : endlessかvs(対戦)モードを指定する
        diff : 難易度
        inputmode : 入力の形式. 'key'ならキーボード入力, 'rec'なら音声入力
    """
    wdic = load_dic(diff)
    while 1:
        el = wordinput(inputmode)
        if el == 'ン':
            print('You lose!')
            exit()
        if len(wdic[el]) == 0:
            print('I lose!')
            #savedic = learn_word(w,{})
            save_dic(savedic)
            exit()
        else:
            re = return_word(el,wdic)
            print('me:'+re)
            jtalk.jtalk(re.encode('utf-8'))
            #savedic = learn_word(w,{})
            save_dic(savedic)
            if mode != 'endless':
                wdic[el].remove(re)

if __name__ == '__main__':
    print('Which mode?(endless,vs)> ',end='')
    while(1):
        mode = input()
        if mode in ['endless','vs']:
            break
        print('Input any one word of "endless" and "vs".')
    print('Choose difficulty:easy,normal,hard.> ',end='')
    while(1):
        diff = input()
        if diff in ['easy','normal','hard']:
            break
        print('Input any one word of "easy", "normal" and "hard".')
    play(mode,diff)
