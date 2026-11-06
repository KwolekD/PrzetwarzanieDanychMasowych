from celery import Celery

app = Celery(
    "lab5",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="rpc://",
    include=["tasks"],
)
app.conf.task_routes = {
    "tasks.get_nth_word": {"queue": "scraper"},
    "tasks.write_word": {"queue": "poem"},
}
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True
