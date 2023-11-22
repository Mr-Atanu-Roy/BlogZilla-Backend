from rest_framework_simplejwt.tokens import RefreshToken

#returns access and refresh tokens for a user
def get_token(user):
    '''
    i/p -> user object
    o/p -> access and refresh tokens
    '''

    try:
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    except Exception as e:
        print(e)
        return None


#converts a string sequence to a list
def str_to_list(data):
    '''
    i/p -> "abc, xyz, pqr"
    o/p -> ['abc', 'xyz', 'pqr']
    '''

    if data.strip() == '': return []
    l = data.split(',')
    stripped_list = [item.strip() for item in l]

    return stripped_list


#converts a list sequence to a string
def list_to_str(data):
    '''
    i/p -> ['abc', 'xyz', 'pqr']
    o/p -> "abc, xyz, pqr"
    '''

    if len(data) == 0: return ''
    cleaned_list = [item.strip() for item in data]
    return ', '.join(cleaned_list)

#check if data is list of strings
def is_valid_sequence(data):

    if isinstance(data, list) and all(isinstance(item, str) for item in data) and len(data) > 0:
        return True
    else:
        return False



