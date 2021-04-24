from flask_apscheduler import APScheduler
from service import documents
from service import message as model_message

scheduler = APScheduler()


def scheduled_jobs():
    # test env jobs
    # schedule_stag()

    # production env jobs
    schedule_prod()

    scheduler.start()


def schedule_stag():
    scheduler.add_job(
        id='Validate documents Stag',
        func=documents.validate_documents,
        trigger='interval',
        seconds=1000,
        args=('api-stag',)
    )

    scheduler.add_job(
        id='Consult documents Stag',
        func=documents.consult_documents,
        trigger='interval',
        seconds=1800,
        jitter=32,
        args=('api-stag',)
    )

    scheduler.add_job(
        id='Process Messages Stag',
        func=model_message.job_process_messages,
        trigger='interval',
        seconds=2100,
        jitter=44,
        args=('api-stag',)
    )


def schedule_prod():
    scheduler.add_job(
        id='Validate documents Prod',
        func=documents.validate_documents,
        trigger='interval',
        seconds=600,
        args=('api-prod',)
    )

    scheduler.add_job(
        id='Consult documents Prod',
        func=documents.consult_documents,
        trigger='interval',
        seconds=700,
        jitter=32,
        args=('api-prod',)
    )

    scheduler.add_job(
        id='Process Messages Prod',
        func=model_message.job_process_messages,
        trigger='interval',
        seconds=1000,
        jitter=44,
        args=('api-prod',)
    )
