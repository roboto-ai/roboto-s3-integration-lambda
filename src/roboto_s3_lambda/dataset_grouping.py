import datetime

from roboto_s3_lambda.logger import logger
from roboto_s3_lambda.model import RobotoCreateDatasetArgs

class DatasetUniquenessQueries:
    """
    Creates common grouping RoboQL queries to power the `Dataset::create_if_not_exists` API
    """
    @staticmethod
    def dataset_per_day(current_day: datetime.datetime) -> str:
        """
        Create a single dataset for all data collected on a given day
        """
        start = current_day.date().isoformat()
        end = (current_day.date() + datetime.timedelta(days=1)).isoformat()
        return f"created >= '{start}' AND created < '{end}'"

    @staticmethod
    def dataset_per_device_per_day(device_id: str, current_day: datetime.datetime) -> str:
        """
        Create a dataset for each device for all data collected on a given day
        """
        start = current_day.date().isoformat()
        end = (current_day.date() + datetime.timedelta(days=1)).isoformat()
        return f"created >= '{start}' AND created < '{end}' AND device_id = '{device_id}'"

    @staticmethod
    def dataset_per_name(name: str) -> str:
        """
        Provide your own semantically meaningful name for a dataset.

        This is typically used when you have your own `mission_id` or similar which is already meaningful and unique
        """
        return f"name = '{name}'"

    @staticmethod
    def best_fit_for_args(create_dataset_args: RobotoCreateDatasetArgs) -> str:
        """
        Given the information available in the create_dataset_args, return the best fit for a grouping query
        """
        if create_dataset_args.name:
            logger.info(f"Using unique per name grouping query for name {create_dataset_args.name}")
            return DatasetUniquenessQueries.dataset_per_name(create_dataset_args.name)
        elif create_dataset_args.device_id:
            logger.info(f"Using unique per device per day grouping query for device {create_dataset_args.device_id}")
            return DatasetUniquenessQueries.dataset_per_device_per_day(
                create_dataset_args.device_id, datetime.datetime.now()
            )
        else:
            logger.info("Using unique per day grouping query")
            return DatasetUniquenessQueries.dataset_per_day(datetime.datetime.now())