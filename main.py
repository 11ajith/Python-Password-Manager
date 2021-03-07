import sqlite3

from os import path

from database_functions import (add_service, add_user, check_data_from_service, create_database,
                                delete_service, delete_user, get_master_hashed, get_key,
                                get_user_id, get_usernames_list, list_saved_services,
                                update_service_password, update_service_username)
from encryption_functions import get_hash, generate_key, encrypt_password, decrypt_password

print(" _____   _____   _____   _____             _____   ___   ___    __ __   ___      _         ____   ___      ____  ___  ")
print("|     | |     | |       |       |   |   | |     | |   | |   |  |  |  | |   |    | |     | |    | |        |     |   | ")
print("|_____| |_____| |_____  |_____  |   |   | |     | |_|   |    | |  |  | |___|   |   |   |  |____| |    ___ |____ |_|   ")
print("|       |     |       |       | |   |   | |     | |  |  |    | |  |  | |   |  |     | |   |    | |   |   ||     |  |  ")
print("|       |     |  _____|  _____| |___|___| |_____| |   | |___|  |  |  | |   | |       |    |    | |___|   ||____ |   | ")

def main_menu():
    print('------------------------------')
    print('|   Specify your operation   |')
    print('| "1": Sign in               |')
    print('| "2": Register              |')
    print('| "3": Delete user           |')
    print('| "4": Exit                  |')
    print('------------------------------')
    return input()


def user_menu():
    print('-----------------------------------------')
    print('|       Available options are           |')
    print('| "1": list all                         |')
    print('| "2": add new                          |')
    print('| "3": get data                         |')
    print('| "4": update data                      |')
    print('| "5": delete                           |')
    print('| "6": exit                             |')
    print('-----------------------------------------')
    return input()


def check_user(username, provided_hash):
    users_list = get_usernames_list()

    for user in users_list:
        if username == user[0]:
            if provided_hash == get_master_hashed(username):
                return True
                break
            else:
                return False
                break
    else:
        return None


def main():
    if not path.exists('passwords.db'):
        create_database()

    while True:
        option = main_menu()

        if option not in ['1', '2', '3', '4']:
            print('Invalid option\n')

        elif option == '4':
            exit()

        elif option == '2':
            #  Create new user
            print('''Enter master key credentials\n''')

            #  Check if username is valid
            users_list = get_usernames_list()
            valid = False
            while not valid:
                username = input('\nEnter master username ')
                for name in users_list:
                    if username == name[0]:
                        print('\nUsername alredy taken')
                        break
                else:
                    valid = True

            master_password = input('\nEnter master password ')
            master_hashed = get_hash(master_password)
            key = generate_key()

            try:
                add_user(username, master_hashed, key)
                print('\nUser added successully!')
            except sqlite3.Error:
                print('\nAn error ocurred, try again later')

        elif option == '1':
            username = input('\nEnter master username ')
            provided_password = input('\nEnter master password ')
            provided_hashed = str(get_hash(provided_password))

            accessed = check_user(username, provided_hashed)

            if accessed:
                print(f'\nWelcome {username}\n')
                user_id = get_user_id(username)
                user_key = get_key(user_id)

                while True:
                    operation = user_menu()

                    if operation not in ['1', '2', '3', '4', '5', '6']:
                        print('\nInvalid option!')

                    elif operation == '6':
                        print(f'\nBye {username}\n')
                        break

                    elif operation == '1':
                        services_list = list_saved_services(user_id)

                        if len(services_list) == 0:
                            print("\nNo data available\n")
                        else:
                            print('\nListing available data\n')
                            for i in range(len(services_list)):
                                print(f'Service {i + 1}: {services_list[i][0]}\n')

                    elif operation == '2':
                        #  Check if service isn't alredy saved
                        services_list = list_saved_services(user_id)
                        valid = False
                        while not valid:
                            service_name = input('\nSpecify application name to add ')
                            for service in services_list:
                                if service_name == service[0]:
                                    print("\nApplication alredy registered")
                                    break
                            else:
                                valid = True

                        username = input(
                            f"\nWhat is your username in {service_name}? ")
                        password = input(
                            f'\nWhat is your password in {service_name}? ')
                        encrypted_password = encrypt_password(
                            user_key, password)

                        add_service(service_name, username,
                                    encrypted_password, user_id)

                        print('\nCredentials added successfully!')

                    elif operation == '3':
                        service = input('\nEnter application to check ')
                        service_list = list_saved_services(user_id)

                        for existing_service in service_list:
                            if service == existing_service[0]:
                                exists = True
                                break
                        else:
                            exists = False

                        if not exists:
                            print('\nSorry the application is not specified')
                        else:
                            username, hashed_password = check_data_from_service(
                                user_id, service)

                            password = decrypt_password(
                                user_key, hashed_password)

                            print(f'\nApplication: {service}\nUsername: {username}\nPassword: {password}')

                    elif operation == '4':
                        service = input('\nEnter the application to update ')

                        service_list = list_saved_services(user_id)

                        for name in service_list:
                            if name[0] == service:
                                exists = True
                                break
                        else:
                            exists = False

                        if exists:
                            username = input('\nEnter new username (----press enter to skip the change----) ')
                            password = input('\nEnter new password (----press enter to skip the change----) ')

                            if username == '' and password == '':
                                print('\nYou must change at least one credential')
                                continue

                            elif username == '':

                                encrypted_password = encrypt_password(
                                    user_key, password)
                                update_service_password(
                                    user_id, service, encrypted_password)

                            elif password == '':
                                update_service_username(
                                    user_id, service, username)

                            elif username != '' and password != '':
                                encrypted_password = encrypt_password(
                                    user_key, password)
                                update_service_password(
                                    user_id, service, encrypted_password)
                                update_service_username(
                                    user_id, service, username)

                            print('\nApplication updated successfully')

                        else:
                            print("\nThis application isn't registred")

                    elif operation == '5':
                        service = input('\nEnter the application to delete ')

                        service_list = list_saved_services(user_id)

                        for name in service_list:
                            if name[0] == service:
                                exists = True
                                break
                        else:
                            exists = False

                        if exists:
                            delete_service(user_id, service)
                            print('\nApplication deleted successfully!')

                        else:
                            print("\nThis application isn't registred")

            elif accessed is False:
                print('\nAccess denied!')

            elif accessed is None:
                print('\nUser not found')

        elif option == '3':
            username = input('\nEnter master username ')
            provided_password = input('\nEnter master password ')
            provided_hashed = str(get_hash(provided_password))

            accessed = check_user(username, provided_hashed)

            if accessed:
                user_id = get_user_id(username)
                delete_user(user_id)
                print(f'\nThe user {username} was deleted successfully')

            elif accessed is False:
                print('\nAccess denied!')

            elif accessed is None:
                print("\nThis user doesn't exists")


if __name__ == "__main__":
    main()
