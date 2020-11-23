from flask_apscheduler import APScheduler
from service import documents
from service import message as model_message

scheduler = APScheduler()


def scheduled_jobs():
    scheduler.add_job(id='Validate documents', func=validate_documents, trigger='interval', seconds=300)
    scheduler.add_job(id='Consult documents', func=consult_documents, trigger='interval', seconds=600, jitter=15)
    scheduler.add_job(id='Process Messages', func=model_message.job_process_messages, trigger='interval', seconds=1000, jitter=22)
    scheduler.start()


def validate_documents():
    documents.validate_documents()


def consult_documents():
    documents.consult_documents()
