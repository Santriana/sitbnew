from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.paginator import Paginator
from .bundling_fhir import request_data_transaction_retry
from .bundling_sitb import request_data_transaction_sitb_retry
from apps.transaction.models import Transaction, TransactionStatus, TransactionSitb

logger = get_task_logger(__name__)


@shared_task()
def scheduler_transaction_retry():
    transaction = Transaction.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    logger.info("=== Scheduler transaction retry ===")
    logger.info("Start : {}".format(timezone.now()))
    logger.info("Total data : {}".format(transaction.count()))
    batch_user = Paginator(transaction, 100)
    for result in batch_user.page_range:
        page = batch_user.page(result)
        logger.info("Run Process {} ".format(page))
        batch = batch_user.page(result).object_list
        for item_batch in batch:
            result_request = request_data_transaction_retry(item_batch.id)
            logger.info("transaction id : {}".format(item_batch.id))
            logger.info("status : {}".format(result_request))
    logger.info("End : {}".format(timezone.now()))

    return "Transaction retry success"

@shared_task()
def scheduler_transaction_sitb_retry():
    transaction_sitb = TransactionSitb.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    logger.info("=== Scheduler transaction sitb retry ===")
    logger.info("Start : {}".format(timezone.now()))
    logger.info("Total data : {}".format(transaction_sitb.count()))
    batch_user = Paginator(transaction_sitb, 100)
    for result in batch_user.page_range:
        page = batch_user.page(result)
        logger.info("Run Process sitb {} ".format(page))
        batch = batch_user.page(result).object_list
        for item_batch in batch:
            result_request = request_data_transaction_sitb_retry(item_batch.id)
            logger.info("transaction sitb id : {}".format(item_batch.id))
            logger.info("status sitb : {}".format(result_request))
    logger.info("End : {}".format(timezone.now()))

    return "Transaction sitb retry success"
