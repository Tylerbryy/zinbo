import unittest
from unittest.mock import patch, MagicMock
from run import main, LanguageModelClientFactory, get_user_name, choose_language_model_client

class TestEmailProcessingProgram(unittest.TestCase):

    @patch('run.get_gmail_service')
    @patch('run.get_user_email')
    @patch('run.os.path.exists')
    @patch('run.os.makedirs')
    @patch('run.open', new_callable=unittest.mock.mock_open, read_data='{"email_id": true}')
    @patch('run.json.load')
    @patch('run.choose_language_model_client')
    @patch('run.LanguageModelClientFactory.get_client')
    @patch('run.get_user_name')
    @patch('run.fetch_emails')
    @patch('run.parse_email_data')
    @patch('run.process_email')
    @patch('run.report_statistics')
    def test_main_flow(self, mock_report_statistics, mock_process_email, mock_parse_email_data, mock_fetch_emails, mock_get_user_name, mock_get_client, mock_choose_client, mock_json_load, mock_open, mock_makedirs, mock_path_exists, mock_get_user_email, mock_get_gmail_service):
        # Setup mock return values and side effects
        mock_get_gmail_service.return_value = MagicMock()
        mock_get_user_email.return_value = 'test@example.com'
        mock_path_exists.return_value = True
        mock_json_load.return_value = {}
        mock_choose_client.return_value = ('gpt-4-1106-preview', 'api_key')
        mock_get_client.return_value = MagicMock()
        mock_get_user_name.return_value = ('Test', 'User')
        mock_fetch_emails.return_value = ([{'id': 'email_id'}], None)
        mock_parse_email_data.return_value = {'subject': 'Test Subject'}

        # Call the main function
        main()

        # Assertions to ensure each function was called
        mock_get_gmail_service.assert_called_once()
        mock_get_user_email.assert_called_once()
        mock_path_exists.assert_called()
        mock_makedirs.assert_not_called()
        mock_open.assert_called()
        mock_json_load.assert_called()
        mock_choose_client.assert_called_once()
        mock_get_client.assert_called_once_with('gpt-4-1106-preview', api_key='api_key', model_path=None)
        mock_get_user_name.assert_called_once()
        mock_fetch_emails.assert_called()
        mock_parse_email_data.assert_called()
        mock_process_email.assert_called()
        mock_report_statistics.assert_called_once()



@patch('run.get_gmail_service')
@patch('run.get_user_email')
@patch('run.os.path.exists')
def test_main_flow_no_email_file(self, mock_path_exists, mock_get_user_email, mock_get_gmail_service):
    # Test the behavior when the email file does not exist
    mock_path_exists.return_value = False
    mock_get_user_email.return_value = 'test@example.com'
    mock_get_gmail_service.return_value = MagicMock()

    with patch('run.makedirs') as mock_makedirs, \
         patch('run.open', new_callable=unittest.mock.mock_open) as mock_open:
        main()

        mock_makedirs.assert_called_once()
        mock_open.assert_called_once_with('email_file.json', 'w')

@patch('run.get_gmail_service')
@patch('run.get_user_email')
@patch('run.fetch_emails')
def test_main_flow_fetch_emails_failure(self, mock_fetch_emails, mock_get_user_email, mock_get_gmail_service):
    # Test the behavior when fetching emails fails
    mock_get_gmail_service.return_value = MagicMock()
    mock_get_user_email.return_value = 'test@example.com'
    mock_fetch_emails.return_value = (None, Exception("Failed to fetch emails"))

    with self.assertRaises(Exception) as context:
        main()

    self.assertTrue('Failed to fetch emails' in str(context.exception))

@patch('run.get_gmail_service')
@patch('run.get_user_email')
@patch('run.fetch_emails')
@patch('run.parse_email_data')
def test_main_flow_parse_email_failure(self, mock_parse_email_data, mock_fetch_emails, mock_get_user_email, mock_get_gmail_service):
    # Test the behavior when parsing emails fails
    mock_get_gmail_service.return_value = MagicMock()
    mock_get_user_email.return_value = 'test@example.com'
    mock_fetch_emails.return_value = ([{'id': 'email_id'}], None)
    mock_parse_email_data.side_effect = Exception("Failed to parse email")

    with self.assertRaises(Exception) as context:
        main()

    self.assertTrue('Failed to parse email' in str(context.exception))

@patch('run.get_gmail_service')
@patch('run.get_user_email')
@patch('run.fetch_emails')
@patch('run.parse_email_data')
@patch('run.process_email')
def test_main_flow_process_email_failure(self, mock_process_email, mock_parse_email_data, mock_fetch_emails, mock_get_user_email, mock_get_gmail_service):
    # Test the behavior when processing an email fails
    mock_get_gmail_service.return_value = MagicMock()
    mock_get_user_email.return_value = 'test@example.com'
    mock_fetch_emails.return_value = ([{'id': 'email_id'}], None)
    mock_parse_email_data.return_value = {'subject': 'Test Subject'}
    mock_process_email.side_effect = Exception("Failed to process email")

    with self.assertRaises(Exception) as context:
        main()

    self.assertTrue('Failed to process email' in str(context.exception))



if __name__ == '__main__':
    unittest.main()