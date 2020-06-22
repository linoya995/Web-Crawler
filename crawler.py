import datetime
import hashlib
import requests
from bs4 import BeautifulSoup

SUCCESS_STATUS = 200


class Crawler:
    """
    "Crawler" class.
    A web crawler that is used to browses a vendor website
    in order to grab firmware files, and collect their metadata.
    """

    def __init__(self):
        print('')

    def __create_soup(self, url):
        """
        This function create BeautifulSoup object for parsing a document.
        :param url: website url.
        :return: soup - BeautifulSoup object for pulling data out of HTML.
        """

        # Try to get a web page
        req = requests.get(url)

        # Error
        if req.status_code != SUCCESS_STATUS:
            print("Error: requests failed. \n" + "url:" + url + " status code: " + req.status_code)

        html_doc = req.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup

    def __join_paths(self, absolute_url, relative_url):
        """
        Joining absolute and relative urls.
        :param absolute_url: an entire address.
        An example of an absolute URL would look like this:
        https://www.rockchipfirmware.com
        :param relative_url:
        :return:
        """
        return (absolute_url + '/' + relative_url).replace("\\", "/")

    def __check_if_need_to_crawl(self, hash_collection, link, soup):
        """
        Check if there is a need to crawl the site by comparing
        html hash codes.
        :param hash_collection: html hash codes collection.
        :param link: web-site link.
        :param soup: a beautiful soap object.
        :return:
        """
        remote_hash = None
        first_time = True if hash_collection.find_one({'url': link}) is None else False
        if not first_time: remote_hash = hash_collection.find_one({'url': link})
        if remote_hash is not None: remote_hash = remote_hash.get('hash')
        local_hash = hashlib.md5(soup.encode()).hexdigest()
        website_is_changed = True if remote_hash != local_hash else False

        print("first_time: ", first_time)
        print("website_is_changed: ", website_is_changed)

        return first_time, website_is_changed

    def crawler(self, root_url, hash_collection):
        """
        This function starts to crawl from root_url and browses the website
        in order to grab firmware files, and collect their metadata.
        the function hashes whole content of each page and save the hash
        code in hash_collection. in this way, hash_collection contain
        all html hash codes of all the websites that already have been crawled.
        by comparing between the remote hash and local hash the function can tell
        if the website information is changed. in this case,
        collects the new data, otherwise skips on this web page.
        :param root_url: - to start crawling from
        :param hash_collection: collection for saving html hash codes of the sited
        that have been already crawled. to be hold in data base.
        :return: result -list of all collected firmware files metadata.
        """

        print("*********************crawler started*********************c")
        print("Root website: " + root_url + "/n")

        result = []
        device_id = 1
        soup = self.create_soup(root_url)

        # find firmware download page
        download_page_link = soup.find_all('a', title="Download")[0].get('href')
        link = self.join_paths(root_url, download_page_link)
        soup = self.create_soup(link)

        # looping through paging
        while True:
            print("crawl site: " + link)

            first_time, website_is_changed = self.check_if_need_to_crawl(hash_collection, link, soup)

            # If it is the first crawling for this page or if the information on the website is changed
            if first_time or (not first_time and website_is_changed):

                # find all firmware device links in a page
                links = soup.find_all('td', class_="views-field views-field-title")  # name and link
                versions = soup.find_all('td', class_="views-field views-field-field-android-version2")  # version

                # looping through firmware downloads link
                for i in range(0, len(links)):
                    data = self.collect_metadata(self.join_paths(root_url, links[i]), versions[i], device_id)
                    print(data)

                    # Insert dict to result and
                    result.append(data)
                    device_id = device_id + 1

                dict_hash = {'url': link, 'hash': hashlib.md5(soup.encode()).hexdigest()}
                if first_time:
                    hash_collection.insert_one(dict_hash)
                else:
                    hash_collection.findandupadteone({'url': link},
                                                     {"$set": {'hash': hashlib.md5(soup.encode()).hexdigest()}})

            # find next page
            next_page = (soup.find('a', text="next"))
            if next_page is None: break
            link = self.join_paths(root_url, next_page.get('href'))
            soup = self.create_soup(link)

        print("*********************crawler finished*********************c")
        return result

    def __collect_metadata(self, page_link, device_version, device_id):
        """
        Collecting data about the product.
        :param page_link: url of the product page.
        :param device_version: device version.
        :param device_id: device id.
        :return: data - a dict that contain all products metadata.
        """
        data = {}

        # Collect metadata
        device_name = page_link.text.replace('\n', '')
        device_url = page_link.find('a').get('href')
        device_version = device_version.text.replace('\r\n', '').strip()

        # create soup
        soup = self.create_soup(page_link)

        # Collect build date
        build_date_class = "field-name-changed-date"
        build_date = soup.find('div', {'class': lambda x: x and build_date_class in x.split()})
        if build_date is not None:
            build_date = build_date.find('div', class_="field-item even").text

        # Collect download link
        download_link = soup.find('a', {'href': lambda x: x and ".zip" in x})
        if download_link is not None:
            download_name = download_link.text
            download_link = download_link.get('href')
        else:
            download_name = None

        # Insert data to dictionary
        data['device_id'] = device_id
        data['url'] = device_url
        data['version'] = device_version
        data['device_name'] = device_name
        data['build_date'] = build_date
        data['file_download_link'] = download_link
        data['file_name'] = download_name
        data["date"] = datetime.datetime.utcnow()

        return data
