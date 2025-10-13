import boto3
import os


def get_dynamodb_table_requests_connexion():
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("DYNAMODB_TABLE_REQUESTS")
    return dynamodb.Table(table_name)


def get_dynamodb_table_favorites_connexion():
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("DYNAMODB_TABLE_FAVORITES")
    return dynamodb.Table(table_name)
