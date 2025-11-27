"""DynamoDB Client."""

import os

import boto3


def get_dynamodb_table_requests_connexion():  # noqa
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("DYNAMODB_TABLE_REQUESTS")
    return dynamodb.Table(table_name)


def get_dynamodb_table_favorites_connexion():  # noqa
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("DYNAMODB_TABLE_FAVORITES")
    return dynamodb.Table(table_name)
