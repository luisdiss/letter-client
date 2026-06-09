import argparse
import sys as _sys

'''
there must be subparser for all public functions in App, Conversations and Contacts. 
each subparser must add_argument for all arguments the user can pass to the corresponding function.
'''

class MyParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exit(self, status=0, message=None):
        if message: self._print_message(message, _sys.stderr)

    def parse_args(self, args=None, namespace=None):
            args, argv = self.parse_known_args(args, namespace)
            if args.command == None:
                print("invalid command")
                return None 
            elif argv:
                return None 
            return args

parser = MyParser(exit_on_error=True)
subparsers = parser.add_subparsers(dest='command')

add_contact_parser = subparsers.add_parser('add')
add_contact_parser.add_argument('username')
add_contact_parser.add_argument('name')

delete_contact_parser = subparsers.add_parser('delete')
delete_contact_parser.add_argument('username')

view_contacts_parser = subparsers.add_parser('view')

select_contact_parser = subparsers.add_parser('select')
select_contact_parser.add_argument('username')

view_messages_parser = subparsers.add_parser('messages')
view_messages_parser.add_argument('count', type=int)

get_messages_parser = subparsers.add_parser('get')

send_message_parser = subparsers.add_parser('send')
send_message_parser.add_argument('msg_text', nargs='+')

exit_parser = subparsers.add_parser('exit')
