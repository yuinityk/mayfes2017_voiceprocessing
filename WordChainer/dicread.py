# -*- coding:utf-8 -*-
import os
import jtalk
import wave
import pyaudio


def speak(d,word,speaker):
    '''
    speaker: in ['kubo','oshiro','nishida','yamada','zunko']
    d: in ['easy','normal','hard','reverse']
    word: string
    '''

    if d == 'reverse':
        dif = 'hard'
    else:
        dif = d
        
    if os.path.exists('./recorded/'+dif+'/'+speaker+'/'+word+'.wav'):
        print('play wave file')
        wf = wave.open('./recorded/'+dif+'/'+speaker+'/'+word+'.wav','r')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
        chunk = 1024
        data = wf.readframes(chunk)
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)
        stream.close()
        p.terminate()
    else:
        print('wave file not found')
        jtalk.jtalk(word.encode('utf-8'))

if __name__ == '__main__':
    speak('hard','あらゆる現実を，全て自分の方へねじまげたのだ．','zunko')
