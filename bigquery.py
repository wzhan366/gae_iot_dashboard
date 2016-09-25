from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials

def query_bigquery(sql):
    # Grab the application's default credentials from the environment.
    credentials = GoogleCredentials.get_application_default()
    # Construct the service object for interacting with the BigQuery API.
    bigquery_service = build('bigquery', 'v2', credentials=credentials)

    print bigquery_service
    query_request = bigquery_service.jobs()
    query_data = {
        'query': sql
    }

    query_response = query_request.query(
        projectId='spry-truck-132223',
        body=query_data).execute()
    return query_response['rows']

# print('Query Results:')
# for row in query_response['rows']:
#     print('\t'.join(field['v'] for field in row['f']))

def dataset_update(projectId, datasetId, dataset_body):
    credentials = GoogleCredentials.get_application_default()
    # Construct the service object for interacting with the BigQuery API.
    bigquery_service = build('bigquery', 'v2', credentials=credentials)
    request = bigquery_service.datasets().update(projectId=projectId, datasetId=datasetId, body=dataset_body)
    response = request.execute()

    print response

if __name__ == '__main__':
    dataset_body = {
    # TODO: Add desired entries of the 'dataset_body' dict
    '0013a20040e44261': 'e0'
    }
    # dataset_update('iot-platform-1385', 'iot_platform_data.xbee_list', dataset_body)
    sql = 'SELECT \
            mac, \
            year(timeStamp),\
            month(timeStamp),\
            day(timeStamp),\
            hour(timeStamp),\
            minute(timeStamp),\
            second(timeStamp), \
            temp,\
            FROM\
              [spry-truck-132223:streaming_1.monitor_1]\
            where day(timeStamp) = 17 and mac = '
    query_bigquery(sql)
