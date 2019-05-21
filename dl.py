"""
dl.py
=====

Generate *proper* MP3 files downloaded from youtube playlist, if needed.
"""
from io import BytesIO
from os import path, walk
from subprocess import run
from sys import argv

from mutagen.id3 import ID3, TPE1, APIC
from PIL import Image

if __name__ == '__main__':
    if len(argv) > 1:
        run(['youtube-dl', '--extract-audio', '--audio-format', 'mp3',
             '--embed-thumbnail', '--add-metadata', '-o', '%(title)s.%(ext)s',
             argv[1]])

    for subdir, dirs, files in walk('.'):
        for file in files:
            ext = path.splitext(file)[-1].lower()
            if ext == '.mp3':
                print('file name: %s' % file)
                tags = ID3(file)
                artist_name: str = tags['TPE1'].text[0]
                artist_name = artist_name.replace(' - Topic', '')
                tags['TPE1'] = TPE1(encoding=3, text=artist_name)
                pict_data = tags.get('APIC:"Album cover"').data
                im = Image.open(BytesIO(pict_data))
                w, h = im.size
                cropped = im.crop((w // 2 - h // 2, 0, w // 2 + h // 2, h))
                cropped_out = BytesIO()
                cropped.save(cropped_out, format='JPEG')
                cropped_data = cropped_out.getvalue()
                tags['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3,
                                    desc='Cover', data=cropped_data)
                tags.save()
