import sys
import re
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO: fill this with your data
host = ''
username = ''
password = ''

if (host == '') | (username == '') | (password == ''):
    print('Fill the host, username and password for HUE')
    sys.exit(1)

# Constants
geckodriver = '/usr/local/bin/geckodriver'
hue_path = '/hue/accounts/login/?next=/hue/security/hive/#@roles'

# We create options for a headless browser
options = Options()
options.headless = True
assert options.headless

# We create a Firefox-based headless browser using the geckodriver
browser = Firefox(executable_path = geckodriver, options = options)

# We connect to the HUE login page
browser.get(host + hue_path)

# We fill the username
browser.find_element_by_id('id_username').send_keys(username)

# We fill the password
browser.find_element_by_id('id_password').send_keys(password)

# We click the button. This takes us to the main HUE page.
buttons = browser.find_element_by_css_selector('.btn').click()

# We look for the Roles table.
roles = None
try:
    roles = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, 'roles'))
    )

except:
    print('Could not find the Sentry roles table')
    sys.exit(1)

# We look for the records in the Roles table.
try:
    tbody = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.card-marginbottom > tbody:nth-child(2)'))
    )

except:
    print('Could not find the Sentry roles table records')
    sys.exit(1)

# These are the rows
rows = tbody.find_elements(By.TAG_NAME , 'tr')

if len(rows) == 0:
    print('Something went wrong. I dont know what is the cause but reruning the script usually fixes it.')
    print('Did you rerun it a few times and it is still not working? Please post what happened to you.')
    sys.exit(1)

#There are three <tr> per role
length = len(rows) // 3

# We open the output file
with open('output.tsv', 'w+') as file:

    for i in range(0, length):

        j = i * 3

        # Get the name
        name = rows[j].find_element_by_css_selector(f'.card-marginbottom > tbody:nth-child(2) > tr:nth-child({j + 1}) > td:nth-child(3)').text
            
        # Get the user groups
        try:
            groups = rows[j].find_element_by_css_selector(f'.card-marginbottom > tbody:nth-child(2) > tr:nth-child({j + 1}) > td:nth-child(4) > a:nth-child(1) > span:nth-child(1)')
        except:
            print(f'Could not find the user groups for the name {name}')
            sys.exit(1)

        # Click the down-fold button
        try:
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'.card-marginbottom > tbody:nth-child(2) > tr:nth-child({j + 1}) > td:nth-child(2) > a:nth-child(1) > i:nth-child(1)'))
            ).click()

        except:
            print(f'Could not find the down-fold button for the name {name}')
            sys.exit(1)

        # Read the list of permits / priviledges
        try:
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'.card-marginbottom > tbody:nth-child(2) > tr:nth-child({j + 2}) > td:nth-child(2) > div:nth-child(1)'))
            )

        except:
            print(f'Could not find the list of priviledges for the name {name}')

        k = 1
        permissions = []
        while k != 0:        
            try:
                permission = browser.find_element_by_css_selector(f'.card-marginbottom > tbody:nth-child(2) > tr:nth-child({j + 2}) > td:nth-child(2) > div:nth-child(1) > div:nth-child({k})')
                permissions.append(permission)
                k = k + 1
            except:
                k = 0

        # Parse the list:
        for permission in permissions:
            content = repr(permission.text)
            if re.search('SERVER', content):
                type_of_permission = 'server'
                value = re.search('server=(\w+)', content).group(1)
            elif re.search('DATABASE', content):
                type_of_permission = 'database'
                value = re.search('db=(\w+)', content).group(1)
            elif re.search('TABLE', content):
                type_of_permission = 'table'
                result = re.search('db=(\w+) table=(\w+)', content)
                value = result.group(1) + '.' +result.group(2)
            elif re.search('URI', content):
                type_of_permission = 'uri'
                if re.search('hdfs://', content):
                    value = re.search('(hdfs://\S+)', content).group(1)
                else:
                    value = re.search('(/\S+)', content).group(1)
            else:
                print('Found type of permission not supported')
                print(repr(permission.text))
                sys.exit(1)

            action = re.search('action=(\w+)', content).group(1)

            line = name + '\t' + groups.text.replace(' ', ',') + '\t' + type_of_permission + '\t' + value + '\t' + action + '\n'
            file.write(line)

# We close the browser
print('Closing the browser...')
browser.close()
print('End of program')