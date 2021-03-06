from flask import Flask, jsonify, Response
from flask_restx import Resource, Namespace, fields #https://flask-restx.readthedocs.io/en/latest/quickstart.html
from core.speech import Recognizer
import pymongo
import os
import json

from threading import Thread

from db import DRVideoNotFound, DRVideo
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# DB
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)
# Namespace
api = Namespace('speech', description='Speech transcription related operations')

transcribe = api.model('Transcript', {
    'transcript': fields.String(required=True, description='Full Transcript'),
    'transcript_times': fields.String(required=True, description= 'Transcript with words and timestamps'),
})


@api.errorhandler(DRVideoNotFound)
@api.route('/post/<path:file>&<model>&<int:minutes_per_split>')
@api.param('model','Model to be used for speech')
@api.param('minutes_per_split','Number of minutes per split')
@api.param('file','File to be transcribed')
class SpeechTranscript(Resource):
    

    def post(self, minutes_per_split, model, file):        
        gid = file
        # check if file exists else
        file = f"core/temp/{file}.wav"
        if not os.path.isfile(file):
            api.abort(404)
        
        doc = DRVideo(gid=gid, transcript="", status='In Process')
        repository.upload_one(doc)
        
        Thread(target = self.transcribe_task, args=(file, minutes_per_split, model, gid)).start()
        return {
            'status':'running'
        }

    # Thread to spawn more processes and transcribe in background
    def transcribe_task(self, file, minutes_per_split, model, gid):
        # Transcribe
        r = Recognizer(
            wav_audio = file, 
            workers=4, 
            min_per_split= int(minutes_per_split),
            model = model
        )
        r.transcribe()
        
        # load again to prevent double-encoding
        output = {
            'transcript': r.transcript,
            'transcript_times': json.loads(r.timestamped_text)
            }
        
        # //TODO more efficient way?
        repository.update(dr_key = gid, field= 'transcript', data=output)
        repository.update(dr_key = gid, field= 'status', data="Success")
        print('Transcribed')


@api.errorhandler(DRVideoNotFound)
@api.route('/get/<file_id>')
@api.param('file_id','File ID')
class SpeechTranscriptResponse(Resource):

    def get(self, file_id):
        data = repository.get_transcript(file_id)
        return jsonify(data)
