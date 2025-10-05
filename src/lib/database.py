import boto3
import os

def get_dynamodb_table_connexion():
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE')
    return dynamodb.Table(table_name)