import subprocess
import configparser
import xml.etree.ElementTree as ET
from dateutil import parser
from datetime import datetime
from collections import namedtuple
import pytz
import os
import math
import click
import codecs

Person = namedtuple('Person', 'id name')
epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.UTC)

def unix_time(dt):
    """Transforms DateTime in epoch"""
    return (dt - epoch).total_seconds()

@click.group()
def cli():
    pass

@cli.group()
def gource():
    pass

@gource.command()
@click.option('--show-log',
    default=False,
    help="Prints the log")
@click.option('--create-captions',
    default=True,
    help="Create an captions.txt file")
@click.argument('ini',
    type=click.Path(exists=True))
def prepare(show_log, create_captions, ini):
    click.echo('Gerando os arquivos de log para o gource e caption')

    config = configparser.ConfigParser()
    # Use case sensitive options
    config.optionxform = lambda option: option
    config.read(ini)

    output = get_log()
    # Pipeline
    output = replace_id(output, get_people(config))
    output = remove_commits(output, get_people(config))

    with codecs.open(config['svn']['output'], "w", "utf8") as file:
        file.write(output)

    with codecs.open(config['gource']['captions'], "w", "utf8") as file:
        file.write("\n".join(gen_captions(config['svn']['output'])))

def get_log(begin='1', end='HEAD'):
    cmd = ["svn", "log", "-r", f'{begin}:{end}', "--xml", "--verbose"]

    return subprocess.check_output(
        cmd,
        encoding='utf-8',
        universal_newlines=True
    )

def get_people(config):
    people = []
    print(config)
    for key in config['names']:
        people.append(Person(id=key, name=config['names'][key]))

    return people

def remove_commits(output, config):
    # try:
    #     commits_to_remove = config['commits']['remove'].split(',')
    # except KeyError:
    #     commits_to_remove = []

    return output

def remove_path(output, config):
    try:
        remove_path = config['path']['remove']
    except KeyError:
        remove_path = ''

    # if remove_path:
    #     root = ET.fromstring(data)

    #     for item in root.findall('logentry'):
    #         path = item.get('path')

    return output

def replace_id(output, people):
    for person in people:
        print('replacing', person.id, 'for', person.name)
        output = output.replace(person.id, person.name)
    return output


def gen_captions(log_file):
    with codecs.open(log_file, encoding="utf8") as file:
        root = ET.fromstring(file.read())

        captions = []

        # Buscar o timestamp|commit para usar de base para os captions
        for item in root.iter('logentry'):
            date = math.floor(unix_time(parser.parse(item.find('date').text)))
            captions.append(str(date) + '|' + str(item.find('msg').text))

        return captions

@gource.command()
def run():
    title = "Primeira Entrega"
    avatars = 'Videos/avatars'
    captions = "captions.txt"
    output = "gource.ppm"

    params = " ".join([
        "--key",
        "--fullscreen",
        "--disable-progress",
        "--hide-filenames",
        "--highlight-users",
        "--file-extensions",
        "--hide filenames",
        "--stop-at-end",
        f"--caption-file {captions }",
        "--caption-offset 1",
        "--caption-colour FFFF0E",
        "--caption-size 30",
        "--caption-duration 5",
        "--auto-skip-seconds 1",
        "-r 60",
        "-1920x1080" # or "-1280x720"
    ])

    cmd = f"gource gource.xml -s 1 {params} --title \"{title}\" --user-image-dir {avatars} -o {output}"

    print(cmd)
    os.system(cmd)

@gource.command()
def convert():
    output = "gource.ppm"
    params = " ".join([
        "-y -r 60 -f image2pipe -vcodec ppm",
        f"-i {output} -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0",
        "-probesize 100G",
    ])

    cmd = f"ffmpeg {params} gource.x264.avi"

    print(cmd)
    os.system(cmd)

