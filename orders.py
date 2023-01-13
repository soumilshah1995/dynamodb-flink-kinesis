try:
    import json
    import boto3
    import base64
    import os
    import uuid

    import datetime
    from datetime import datetime

    from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

    import decimal
    from decimal import Decimal
    import random

except Exception as e:
    print("Error ******* : {} ".format(e))

print('Loading function')


def unmarshall(dynamo_obj: dict) -> dict:
    """Convert a DynamoDB dict into a standard dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}


def marshall(python_obj: dict) -> dict:
    """Convert a standard dict into a DynamoDB ."""
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}


class Datetime(object):
    @staticmethod
    def get_year_month_day():
        """
        Return Year month and day
        :return: str str str
        """
        dt = datetime.now()
        year = dt.year
        month = dt.month
        day = dt.day
        return year, month, day


def flatten_dict(data, parent_key="", sep="_"):
    """Flatten data into a single dict"""
    try:
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key
            if type(value) == dict:
                items.extend(flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
    except Exception as e:
        return {}


def dict_clean(items):
    result = {}
    for key, value in items:
        if value is None:
            value = "n/a"
        if value == "None":
            value = "n/a"
        if value == "null":
            value = "n/a"
        if len(str(value)) < 1:
            value = "n/a"
        result[key] = str(value)
    return result


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)


global kinesis_client

kinesis_client = boto3.client('kinesis',
                              region_name=os.getenv("DEV_AWS_REGION_NAME"),
                              aws_access_key_id=os.getenv("DEV_AWS_ACCESS_KEY"),
                              aws_secret_access_key=os.getenv("DEV_AWS_SECRET_KEY")
                              )


def lambda_handler(event, context):
    for record in event['Records']:

        eventName = record.get("eventName")
        print("record", record)
        json_data = None

        if eventName.strip().lower() == "INSERT".lower():
            json_data = record.get("dynamodb").get("NewImage")

        if eventName.strip().lower() == "MODIFY".lower():
            json_data = record.get("dynamodb").get("NewImage")

        if eventName.strip().lower() == "REMOVE".lower():
            json_data = record.get("dynamodb").get("OldImage")

        print("json_data", json_data, type(json_data))

        if json_data is not None:
            json_data_unmarshal = unmarshall(json_data)
            print("json_data_unmarshal", json_data_unmarshal)

            year, month, day = Datetime.get_year_month_day()

            json_string = json.dumps(json_data_unmarshal, cls=CustomJsonEncoder)
            json_dict = json.loads(json_string)
            _final_processed_json = flatten_dict(json_dict)

            put_response = kinesis_client.put_record(
                StreamName=os.getenv("STREAM_NAME"),
                Data=json.dumps(_final_processed_json),
                PartitionKey=random.randint(1, 10).__str__()
            )

    return 'Successfully processed {} records.'.format(len(event['Records']))
