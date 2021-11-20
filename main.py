#
#
# Nutty Moms
#
# Simple web-scraper program that visits thr url: www.foodallergy.com.
# Each entry in the website database generates a unique url.  Each in turn
# is put into a text file which is loded into the program.  Then a query is
# made against each url and a contact name and email are loaded from each page.
# The final contact list is exported to a csv file.
#
import pandas as pd
import requests
from typing import List, Optional
from dataclasses import dataclass

#
# Contact class
#
# Scans the given url looking for the contact names and associated email.
# The contact pairs (name/email) are put into a tuple and then stored ina list.
#


@dataclass
class Contacts:
    urlstr: str
    state: str
    contacts = []

    def __post_init__(self) -> list:
        #
        # parse teh url string looking for the contact name and then the email
        #
        while True:
            contact_datum = Contacts._find_contact(self)
            email_datum = Contacts._find_email(self)
            if contact_datum is None or email_datum is None:
                break
            #
            # create a tuple and add to the contacts list
            #
            self.contacts.append((contact_datum, email_datum, self.state))

        return self.contacts

    #
    # find_contact
    #
    # The contact anme is in the frame following the "Contact Name:"
    # string
    #
    def _find_contact(self) -> Optional[str]:
        i = self.urlstr.find("Contact Name:")
        if i > 0:

            #
            # found a contact name.  Move the end of line
            #
            div_index = self.urlstr[i:].find('\n')

            #
            # move tot he end of the html field
            # and then strip any whitespace
            #
            cname = self.urlstr[i + div_index:]
            cnindex = cname.find('>')
            contact_str = cname[cnindex + 1:]
            contact_str = contact_str.strip()

            #
            # save the the current location of the url
            # so we can continue scanning from that point
            # forward
            #
            self.urlstr = contact_str

            return contact_str[:contact_str.find('\n')]

    #
    # find_email
    #
    # Scan forward looking for the "Contact Email:" string.
    # extract the email address
    #
    def _find_email(self) -> Optional[str]:

        i = self.urlstr.find("Contact Email:")
        if i > 0:

            #
            # found a valid email address.  Move to the end of the
            # line
            #
            div_index = self.urlstr[i:].find('\n')
            email = self.urlstr[i + div_index:]

            #
            # the email string "maiilto:" ends in a colon
            # so grab the email address from that point forward to the end of the
            # division (>)
            #
            email = email[email.find(':') + 1:]
            email_index = email.find('\"')
            email = email[:email_index]

            #
            # save the current url location for the next forward looking
            # search
            #
            self.urlstr = self.urlstr[i + div_index + email_index:]

            return email

    #
    # pairs
    #
    # returns the stored tuple list
    #
    @property
    def pairs(self):
        return self.contacts


""""----- END CLASS----"""


#
# get_urls
#
# Read the stored urls in from a text file and store them in
# a list
#


def get_urls() -> List:

    url_file = open("urls.txt", "r")
    url_list = url_file.readlines()

    #
    # remove any line-feeds
    #
    url_list = [url[:-1] for url in url_list]

    return url_list

#
# process_urls
#
# Extract the named pairs and then build a dataframe
# will all of the contact info
#


def process_urls():

    contacts = None

    print('Processing urls', end='')
    url_list = get_urls()
    for url in url_list:
        #
        # request the url string.  Note: the two letter state
        # abbreviation is passed in to help validate that all urls
        # were processed
        #
        f = requests.get(url)
        contacts = Contacts(f.text, url[-2:])
        print('.', end='')

    print('\nFound: {}'. format(len(contacts.pairs)))

    #
    # build the dataframe and drop any duolicate email addresses
    #
    df = pd.DataFrame(contacts.pairs, columns=['Contact', 'Email', 'State'])
    df.drop_duplicates(subset="Email", inplace=True)
    df.to_csv("nutty moms.csv", sep='\t')


#
# main entry point
#
if __name__ == '__main__':
    process_urls()
