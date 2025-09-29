import os
import roboto

from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.s3_event import S3Event, S3EventRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from roboto_s3_lambda.dataset_grouping import DatasetUniquenessQueries
from roboto_s3_lambda.model import RobotoCreateDatasetArgs, RobotoImportFileArgs
from roboto_s3_lambda.logger import logger


# You need to set these environment variables on your Lambda in order for calls to Roboto to work.
#
# Under the hood, calling roboto.Dataset.create_if_not_exists() and roboto.File.import_one() will construct
# a roboto client using the ROBOTO_API_KEY, and will target the organization specified by ROBOTO_ORG_ID (only
# required if you're a member of multiple orgs)
#
# It is advised to create a device called `s3-importer` or similar via `roboto devices register s3-importer`, and to
# use that device's API key for this ROBOTO_API_KEY. That way, requests will not be attributed to your personal user
# creds, and anyone in your org can toggle the device's Roboto access on or off if required.
ROBOTO_API_KEY = os.getenv("ROBOTO_API_KEY")
ROBOTO_ORG_ID = os.getenv("ROBOTO_ORG_ID")
if ROBOTO_API_KEY is None:
    raise ValueError("ROBOTO_API_KEY is not set, that env variable is required for this lambda to work")
if ROBOTO_ORG_ID is None:
    logger.info("ROBOTO_ORG_ID is not set, if you are in multiple orgs, you will need to set this")

@event_source(data_class=S3Event)
def lambda_handler(event: S3Event, context: LambdaContext) -> None:
    """
    This is the main entrypoint for the Lambda function. It is triggered by an S3 event, and
    is responsible for processing the event and importing the files into Roboto.
    """
    records = list(event.records)
    logger.info(f"Received {len(records)} records")

    for record in records:
        if not record.event_name.startswith("ObjectCreated"):
            logger.info(f"Skipping {record.event_name}, currently only processing ObjectCreated events")
            continue
        handle_event_record(record, context)

    logger.info("Successfully processed all records")

def handle_event_record(event_record: S3EventRecord, context: LambdaContext) -> None:
    """
    This function is responsible for processing a single S3 event record and importing the file into Roboto.
    """
    create_dataset_args, import_file_args = infer_create_args_from_record(event_record, context)

    # This controls how we group files into datasets. The DatasetUniquenessQueries class provides
    # some common grouping queries, but you can provide your own if you're so inclined.
    #
    # The best_fit_for_args function will use the information available in the create_dataset_args
    # to choose the most granular grouping query that makes sense for the given args.
    match_roboql_query = DatasetUniquenessQueries.best_fit_for_args(create_dataset_args)

    logger.info("Create-if-not-existing dataset")
    ds = roboto.Dataset.create_if_not_exists(
        match_roboql_query=match_roboql_query,
        tags=create_dataset_args.tags,
        metadata=create_dataset_args.metadata,
        description=create_dataset_args.description,
        device_id=create_dataset_args.device_id,
        create_device_if_missing=True
    )
    logger.info(f"Got dataset {ds.dataset_id}, importing file to it")

    s3_uri = f"s3://{event_record.s3.bucket.name}/{event_record.s3.get_object.key}"
    roboto.File.import_one(
        dataset_id=ds.dataset_id,
        uri=s3_uri,
        relative_path=import_file_args.relative_path,
        tags=import_file_args.tags,
        metadata=import_file_args.metadata,
        description=import_file_args.description,
        device_id=import_file_args.device_id,
    )
    logger.info(f"Successfully imported file {s3_uri} to dataset {ds.dataset_id}")

def infer_create_args_from_record(event_record: S3EventRecord, context: LambdaContext) -> tuple[RobotoCreateDatasetArgs, RobotoImportFileArgs]:
    """
    Extension point for users to customize dataset and file import behavior.
    
    This function is intended to be modified by users to extract and combine information
    from the S3EventRecord with data from their own APIs/databases to provide rich
    context for Roboto imports.
    
    Adding metadata and tags makes search and analytics much more powerful downstream.
    Adding a name to a dataset allows users to bring their own identifiers like
    "flight_id" or "drive_id" into the system. The device_id is used for device-specific
    aggregations on the Roboto side, and descriptions provide human-readable context
    for users browsing the Roboto file explorer.
    
    Depending on your S3 path structure, you may be able to extract information like
    device_id, metadata.start_time, location, etc. from the S3 key scheme. Alternatively,
    you may need to examine x-amzn-meta headers, S3 object tags, or query your own
    databases for additional context.
    
    Args:
        event_record: The S3 event record containing bucket, key, and other S3 metadata
        context: The Lambda context containing request ID and other execution info
        
    Returns:
        A tuple of (RobotoCreateDatasetArgs, RobotoImportFileArgs) with the extracted
        information for dataset creation and file import
    """
    create_dataset_args = RobotoCreateDatasetArgs(
        description="This dataset was automatically created by the roboto-s3-integration-lambda. For more information, see https://github.com/roboto/roboto-s3-integration-lambda",
        device_id=None,
        metadata={
            "importer_aws_request_id": context.aws_request_id
        },
        name=None,
        tags=None,
    )

    import_file_args = RobotoImportFileArgs(
        description="This file was automatically imported by the roboto-s3-integration-lambda. For more information, see https://github.com/roboto/roboto-s3-integration-lambda",
        device_id=None,
        metadata={
            "importer_aws_request_id": context.aws_request_id
        },
        relative_path=event_record.s3.get_object.key,
        tags=None,
    )

    return create_dataset_args, import_file_args
