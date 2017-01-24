import csv
import json
import os
import random
import requests
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit

base_url = 'https://www.khanacademy.org/'
topic_api_url = urljoin(base_url, 'api/v1/topic/{}')
ext_video_api_url = urljoin(base_url, 'api/v1/videos/{}')
int_video_api_url = urljoin(base_url, 'api/internal/videos/{}/transcript')
text_format = '{}.txt'

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
data_dir = os.path.join(parent_dir, 'data')
transcript_path= os.path.join(data_dir, 'transcripts')
subjects = ['calculus-home', 'physics', 'chemistry', 'biology', 
            'us-history', 'computer-science', 'music', 'grammar']
videos_per_subject = 1


def get_json(url):
    page = requests.get(url)
    return json.loads(page.content.decode('UTF-8'))


def get_child_slugs(slug):
    slug_url = topic_api_url.format(slug)
    slug_json = get_json(slug_url)
    return [child['node_slug'] for child in slug_json['children']]


def get_video_youtube_id(slug):
    slug_url = ext_video_api_url.format(slug)
    slug_json = get_json(slug_url)
    return slug_json['youtube_id']


def get_videos(subject):
    topic = random.choice(get_child_slugs(subject))
    section = random.choice(get_child_slugs(topic))
    content = get_child_slugs(section)
    is_video = lambda c: c[0] == 'v'
    return list(filter(is_video, content))


def get_transcript(youtube_id):
    video_url = int_video_api_url.format(youtube_id)
    video_json = get_json(video_url)
    text = [part['text'] for part in video_json]
    return ' '.join(text).replace('\n', ' ')

try:
    os.mkdir(transcript_path)
except OSError:
    shutil.rmtree(transcript_path)
    os.mkdir(transcript_path)

data = {}

for subject in subjects:
    subject_videos = []
    while len(subject_videos) < videos_per_subject:
        videos = get_videos(subject)
        if len(videos) == 0:
            continue
        chosen_video = random.choice(videos)
        subject_videos.append(chosen_video[2:])
    for video in subject_videos:
        youtube_id = get_video_youtube_id(video)
        transcript = get_transcript(youtube_id)
        video_fname = text_format.format(video)
        video_path = os.path.join(transcript_path, video_fname)
        with open(video_path, 'w') as f:
            f.write(transcript)
        data[video_fname] = subject
        
data_csv_path = os.path.join(data_dir, 'data.csv')
with open(data_csv_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data.items())
