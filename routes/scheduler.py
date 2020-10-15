from flask_apscheduler import APScheduler
from service import documents

scheduler = APScheduler()


def scheduled_jobs():
    scheduler.add_job(id='Validate documents', func=validate_documents, trigger='interval', seconds=300)
    scheduler.add_job(id='Consult documents', func=consult_documents, trigger='interval', seconds=600)
    scheduler.start()


def validate_documents():
    print("Start Validate Documents")
    result = documents.validate_documents()
    print("End validate document" + "Result" + result)


def consult_documents():
    print("Start Cosult Documents")
    result = documents.consult_documents()
    print("End consult document" + "Result" + result)



