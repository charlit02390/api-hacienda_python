from flask_apscheduler import APScheduler
from service import documents
from service import message as model_message

scheduler = APScheduler()


def scheduled_jobs():
    scheduler.add_job(
        id='Validate documents',
        func=documents.validate_documents,
        trigger='interval',
        seconds=400
    )
    scheduler.add_job(
        id='Consult documents',
        func=documents.consult_documents,
        trigger='interval',
        seconds=700,
        jitter=32
    )
    scheduler.add_job(
        id='Process Messages',
        func=model_message.job_process_messages,
        trigger='interval',
        seconds=1000,
        jitter=44
    )
    scheduler.start()
